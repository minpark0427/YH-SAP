# YH-SAP Pipeline Optimization: Targeted-Context Generation

## TL;DR

> **Quick Summary**: 현재 전체 프로토콜(111K chars)을 36개 LLM 호출 모두에 반복 주입하는 비효율적 구조를, 코드 기반 프로토콜 섹셔닝 + SAP 태그별 관련 섹션 매핑 + wave 기반 병렬 실행으로 개선. High-complexity 섹션은 근거 추출 → draft 생성 2단계로 분리.
> 
> **Deliverables**:
> - `ProtocolSegmenter` 클래스: 프로토콜을 heading 기반으로 섹션 분할
> - `SECTION_MAPPING` 테이블: SAP 태그 → 관련 프로토콜 섹션 매핑
> - `ContextAssembler` 클래스: 매핑 기반 targeted context 조립 + 공통 컨텍스트
> - High-complexity 2단계 생성 로직 (근거 추출 → draft)
> - Wave 기반 실행 로직
> - 기존 `write_sap()` API 유지, 내부만 리팩터링
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: Task 1 → Task 4 → Task 6 → Task 8

---

## Context

### Original Request
프로토콜을 한번에 넣다보니 작업 컨텍스트에 무리가 있음. 병렬 서브에이전트로 나누고, 런타임 문제 개선.

### Interview Summary
**Key Discussions**:
- 코드 기반 segmentation (LLM 아님) — 프로토콜 heading/table 구조 활용
- 3단 구조: segmentation → mapping → targeted generation
- Context reduction이 timeout 해결의 핵심 (재시도보다 근본 원인 제거)
- write_sap() 외부 API 유지
- High-complexity 섹션 단계 분리 포함

**Research Findings**:
- 프로토콜 구조: `번호.\t제목` 패턴으로 heading이 명확 (TOC lines 32-157)
- 프로토콜 크기: 111,780 chars, 1,338 lines
- 28개 테이블 포함 (pipe-delimited로 이미 interleaving됨)
- 현재 36개 태스크가 각각 ~111K system message 받음 → 총 ~4M chars 입력

### Metis Review
**Identified Gaps** (addressed):
- TOC 라인과 본문 라인이 중복 존재: segmenter에서 TOC 영역 제외 필요
- 테이블이 pipe-delimited로 인접 heading 아래에 위치하지만, heading 없이 시작하는 테이블 존재 가능: 직전 섹션에 귀속시키는 규칙 필요
- 공통 컨텍스트(study design, treatment arms 등)를 어디서 추출할지 명확화 필요: Protocol Synopsis(섹션 1.1)에서 추출
- wave 실행 시 wave 간 결과 전달 메커니즘 명확화 필요: high-complexity 태스크의 1단계 결과가 2단계 입력이 됨

---

## Work Objectives

### Core Objective
전체 프로토콜 반복 주입 → 태그별 관련 섹션만 선택적 주입으로 전환하여, 호출당 컨텍스트를 ~70% 축소하고 production 모드에서의 안정성 확보.

### Concrete Deliverables
- `auto_sap/classes/protocol_segmenter.py` — 프로토콜 섹셔닝 클래스
- `auto_sap/section_mapping.py` — SAP 태그-프로토콜 섹션 매핑 테이블
- `auto_sap/classes/context_assembler.py` — targeted context 조립기
- `auto_sap/classes/template_class.py` — wave 기반 실행 + 2단계 생성 통합
- `auto_sap/prompts/prompts_yuhan_v1.py` — system_message 함수 시그니처 변경

### Definition of Done
- [ ] YH00000 프로토콜로 E2E 실행 성공 (36개 섹션, 0 ERROR)
- [ ] 호출당 평균 context size가 기존 대비 50% 이상 감소
- [ ] write_sap() 외부 인터페이스 변경 없음
- [ ] 기존 content.txt 대비 품질 동등 이상

### Must Have
- 코드 기반 heading 파싱 (LLM 호출 없이)
- SAP 태그별 관련 프로토콜 섹션만 선택적 주입
- 공통 전역 컨텍스트 (study design, treatment arms, population) 얇게 유지
- High-complexity 섹션(primary_efficacy, secondary_efficacy, sample_size) 2단계 생성
- write_sap() API 하위 호환

### Must NOT Have (Guardrails)
- LLM 기반 프로토콜 분류/섹셔닝 (규칙 기반만)
- LLM 호출 retry/model fallback 로직 (context reduction으로 timeout 자체를 해결)
  - 단, context assembly 시 매핑 실패에 대한 full-protocol fallback은 안전장치로 포함 (Task 4)
- 프롬프트 내용 자체의 튜닝 (이번 스코프 아님)
- 새로운 외부 의존성 추가
- auto_code pipeline 변경

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: NO (기존 테스트 없음)
- **Automated tests**: None (E2E 검증으로 대체)
- **Framework**: None

### QA Policy
Every task includes agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Library/Module**: Use Bash (python3 REPL) — Import, call functions, compare output
- **API/Backend**: Use Bash — Run pipeline, check output files

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation — 독립적 모듈):
├── Task 1: ProtocolSegmenter 클래스 [deep]
├── Task 2: SECTION_MAPPING + GLOBAL_CONTEXT_SECTIONS [unspecified-high]
└── Task 4: High-complexity 2단계 생성 로직 [deep]

Wave 2 (Assembly — Wave 1 결과 통합):
└── Task 3: ContextAssembler 클래스 [deep]

Wave 3 (Integration — template_class + chat_classes 리팩터링):
└── Task 5: template_class 리팩터링 + chat_classes 시그니처 [deep]

Wave 4 (Validation):
└── Task 6: E2E 검증 + 비교 [unspecified-high]

Critical Path: Task 1 → Task 3 → Task 5 → Task 6
Parallel Speedup: Wave 1에서 3개 병렬
Max Concurrent: 3 (Wave 1)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|-----------|--------|
| 1 | — | 3 |
| 2 | — | 3 |
| 3 | 1, 2 | 5 |
| 4 | — | 5 |
| 5 | 3, 4 | 6 |
| 6 | 5 | — |

### Agent Dispatch Summary

- **Wave 1**: **3 tasks** — T1 → `deep`, T2 → `unspecified-high`, T4 → `deep`
- **Wave 2**: **1 task** — T3 → `deep`
- **Wave 3**: **1 task** — T5 → `deep`
- **Wave 4**: **1 task** — T6 → `unspecified-high`

---

## TODOs

- [ ] 1. ProtocolSegmenter 클래스

  **What to do**:
  - `auto_sap/classes/protocol_segmenter.py` 신규 생성
  - `Protocol.protocol_txt`를 입력받아 heading 기반으로 섹션 단위 분할
  - Heading 패턴: `^\d+(\.\d+)*\.\t` (예: `1.`, `1.1.`, `10.2.1.`)
  - TOC 영역 (line 28~176 근처, "목차"부터 "그림 목차" 끝까지) 자동 감지 및 제외
  - 테이블(pipe-delimited 행)은 직전 heading 섹션에 귀속
  - Appendix 영역도 별도 섹션으로 분할
  - 출력: `dict[str, str]` — key는 섹션 번호 (예: "10.2", "5.1"), value는 해당 섹션 전체 텍스트
  - `get_section(section_id: str) -> str` 메서드 — **prefix 매칭**: `get_section("10")`은 섹션 10 + 10.1 + 10.2 + ... 모든 하위 섹션을 결합하여 반환. `get_section("10.2")`는 10.2 + 10.2.1 + ... 반환.
  - `get_sections(section_ids: list[str]) -> str` 메서드 (여러 섹션 결합, 각각 prefix 매칭 적용)
  - `get_global_summary() -> str` 메서드 — 섹션 1.1 (Protocol Synopsis) 텍스트 반환

  **Must NOT do**:
  - LLM 호출
  - 외부 라이브러리 추가
  - Protocol 클래스 자체 수정

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 텍스트 파싱 로직이 다양한 edge case 처리 필요 (TOC 감지, 테이블 귀속, heading 깊이)
  - **Skills**: [`python`]
    - `python`: 정규표현식 기반 텍스트 파싱

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 4)
  - **Blocks**: Task 3
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `auto_sap/classes/protocol_classes.py:39-73` — load_docx()의 interleaving 방식 이해 (paragraph + table이 어떤 형태로 텍스트화되는지)
  - 프로토콜 텍스트 구조: line 32~157이 heading 목록, line 177부터 본문 시작

  **API/Type References**:
  - `Protocol.protocol_txt: str` — 이 문자열이 입력

  **External References**:
  - 없음 (순수 Python re 모듈만 사용)

  **WHY Each Reference Matters**:
  - `protocol_classes.py` — 테이블이 pipe(`|`) 구분자로 렌더링되는 패턴을 알아야 테이블 행을 식별하고 인접 heading에 귀속 가능
  - 프로토콜 heading 구조 — TOC와 본문의 heading이 동일 패턴이므로 TOC 영역을 먼저 제외해야 정확한 분할 가능

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: YH00000 프로토콜 섹셔닝 정상 동작
    Tool: Bash (python3)
    Preconditions: YH-SAP-venv 활성화, YH00000 프로토콜 docx 존재
    Steps:
      1. python3 -c "from auto_sap.classes.protocol_segmenter import ProtocolSegmenter; from auto_sap.classes.protocol_classes import Protocol; p = Protocol('../YH00000-101_Clinical Protocol_Ver1.0_22Feb2024.docx'); s = ProtocolSegmenter(p.protocol_txt); print(f'Sections: {len(s.sections)}'); print(list(s.sections.keys())[:10])"
      2. Assert: sections 수 ≥ 20개
      3. python3 -c "...; text = s.get_section('10.2'); print(f'Section 10.2 length: {len(text)}'); assert '안전성' in text or 'Safety' in text"
      4. python3 -c "...; text = s.get_sections(['4', '9.2', '10.1']); print(f'Combined length: {len(text)}'); assert len(text) < 111780"
      5. python3 -c "...; summary = s.get_global_summary(); print(f'Summary length: {len(summary)}'); assert len(summary) > 500 and len(summary) < 20000"
    Expected Result: 20+ sections parsed, get_section returns relevant text, combined < full protocol
    Failure Indicators: KeyError on section IDs, empty sections, TOC text mixed into body sections
    Evidence: .sisyphus/evidence/task-1-segmenter-basic.txt

  Scenario: TOC 영역이 본문 섹션에 포함되지 않음
    Tool: Bash (python3)
    Preconditions: Same as above
    Steps:
      1. python3 -c "...; all_text = ' '.join(s.sections.values()); assert '목차 [TABLE OF CONTENTS]' not in all_text; print('TOC excluded: PASS')"
    Expected Result: TOC 텍스트가 어떤 섹션에도 포함되지 않음
    Failure Indicators: TOC 라인이 본문 섹션에 포함됨
    Evidence: .sisyphus/evidence/task-1-segmenter-toc-exclusion.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `feat(protocol): add ProtocolSegmenter class`
  - Files: `auto_sap/classes/protocol_segmenter.py`

- [ ] 2. SECTION_MAPPING 테이블

  **What to do**:
  - `auto_sap/section_mapping.py` 신규 생성
  - `SAP_TO_PROTOCOL_MAP: dict[str, list[str]]` — 각 SAP 태그가 참조해야 할 프로토콜 섹션 번호 리스트
  - 36개 SAP 태그 모두에 대해 매핑 정의
  - 매핑 예시:
    - `"statistical_software_version"` → `["10"]` (통계적 고려사항 섹션만)
    - `"primary_efficacy"` → `["4", "5.1", "9.2", "10"]` (목적, 디자인, 유효성 평가, 통계 분석)
    - `"adverse_events"` → `["9.4", "10.2"]` (이상사례 정의 + 안전성 분석)
    - `"sample_size"` → `["4", "5.1", "5.2", "10.8"]` (목적, 디자인, 근거, 대상자수)
    - `"screened_set"` → `["6", "10.1"]` (대상자 모집단, 분석 집단)
    - `"demographics"` → `["6", "9.1"]` (대상자 모집단, 스크리닝 평가)
    - `"visit_windows"` → `["2.1", "9"]` (수행 일정, 평가 절차)
    - `"introduction"` → `["1.1", "3", "5.1"]` (개요, 서론, 디자인)
  - 매핑 근거를 docstring 또는 인라인 코멘트로 간단히 기록
  - **`GLOBAL_CONTEXT_SECTIONS: list[str]` 상수도 이 파일에 추가** (기존 Task 3을 흡수)
    - 공통 컨텍스트에 포함할 섹션: `["1.1"]` (Protocol Synopsis) 또는 `["1.1", "5.1"]`
    - 모든 SAP 태그 호출에 공통으로 주입되는 study overview용

  **Must NOT do**:
  - LLM 호출로 매핑 생성
  - 프로토콜 특정(YH00000-specific) 하드코딩 — 매핑은 일반적인 clinical protocol 구조 기반이어야 함

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: clinical trial protocol 구조 + SAP 섹션 관계에 대한 도메인 지식 필요
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 4)
  - **Blocks**: Task 3
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `auto_sap/prompts/prompts_yuhan_v1.py` — 각 SAP 섹션 프롬프트 내용을 보면 어떤 프로토콜 정보가 필요한지 유추 가능
  - `auto_sap/generate_templates/generate_yuhan_template.py` — 36개 PromptRegister 목록과 순서

  **API/Type References**:
  - 프로토콜 heading 구조 (위 분석에서 확인됨): 섹션 1~12 + Appendix

  **WHY Each Reference Matters**:
  - `prompts_yuhan_v1.py` — 각 프롬프트가 "프로토콜에서 X를 추출하라"고 명시하므로, 어떤 프로토콜 섹션이 관련인지 역추적 가능
  - 프로토콜 heading 구조 — 매핑 대상(value)이 이 heading 번호체계를 따라야 함

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 36개 SAP 태그 모두에 매핑 존재
    Tool: Bash (python3)
    Preconditions: section_mapping.py 생성됨
    Steps:
      1. python3 -c "from auto_sap.section_mapping import SAP_TO_PROTOCOL_MAP; from auto_sap.prompts.prompts_yuhan_v1 import PROMPTS_DICTIONARY; missing = set(PROMPTS_DICTIONARY.keys()) - set(SAP_TO_PROTOCOL_MAP.keys()); print(f'Missing: {missing}'); assert len(missing) == 0"
      2. python3 -c "...; assert all(isinstance(v, list) and len(v) > 0 for v in SAP_TO_PROTOCOL_MAP.values()); print('All mappings non-empty: PASS')"
    Expected Result: 36/36 매핑 존재, 모두 비어있지 않음
    Failure Indicators: missing 태그 존재, 빈 리스트
    Evidence: .sisyphus/evidence/task-2-mapping-completeness.txt

  Scenario: statistical_software_version은 최소 컨텍스트만 매핑
    Tool: Bash (python3)
    Steps:
      1. python3 -c "from auto_sap.section_mapping import SAP_TO_PROTOCOL_MAP; sections = SAP_TO_PROTOCOL_MAP['statistical_software_version']; print(f'Sections: {sections}'); assert len(sections) <= 2"
    Expected Result: 1~2개 섹션만 매핑됨
    Evidence: .sisyphus/evidence/task-2-mapping-minimal.txt

  Scenario: GLOBAL_CONTEXT_SECTIONS 상수 존재
    Tool: Bash (python3)
    Steps:
      1. python3 -c "from auto_sap.section_mapping import GLOBAL_CONTEXT_SECTIONS; print(GLOBAL_CONTEXT_SECTIONS); assert isinstance(GLOBAL_CONTEXT_SECTIONS, list) and len(GLOBAL_CONTEXT_SECTIONS) >= 1"
    Expected Result: 리스트 존재, 1개 이상 섹션 ID 포함
    Evidence: .sisyphus/evidence/task-2-global-context.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `feat(mapping): add SAP-to-protocol section mapping table`
  - Files: `auto_sap/section_mapping.py`

- [ ] 3. ContextAssembler 클래스

  **What to do**:
  - `auto_sap/classes/context_assembler.py` 신규 생성
  - `ContextAssembler(segmenter: ProtocolSegmenter, mapping: dict, global_sections: list, full_protocol_text: str)` 초기화
  - `full_protocol_text` 저장 — fallback 시 사용
  - `assemble(sap_tag: str) -> str` 메서드:
    1. `GLOBAL_CONTEXT_SECTIONS`에서 공통 컨텍스트 추출 (Protocol Synopsis 등)
    2. `SAP_TO_PROTOCOL_MAP[sap_tag]`에서 관련 섹션 추출
    3. 두 가지를 결합하여 하나의 context string 반환
    4. 형식: `"=== STUDY OVERVIEW ===\n{global}\n\n=== RELEVANT PROTOCOL SECTIONS ===\n{specific}"`
  - `assemble_all() -> dict[str, str]` — 36개 태그 모두에 대해 context 조립, 캐시
  - context 크기를 로깅 (`print(f"{sap_tag}: {len(context)} chars")`)

  - **Fallback 안전장치**: 매핑된 섹션이 비어있거나 파싱 실패 시, 전체 프로토콜 텍스트로 fallback
    - `if not specific.strip(): return full_protocol_text` 패턴
    - WARNING 로그 출력하여 어떤 태그에서 fallback 발생했는지 추적 가능
    - 이 fallback이 발생하면 기존(AS-IS)과 동일한 동작 → 최악의 경우에도 기존보다 나빠지지 않음

  **Must NOT do**:
  - LLM 호출
  - 프로토콜 텍스트 임의 가공/요약
  - 매핑에 없는 섹션 추가 추측

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: segmenter + mapping + global context를 통합하는 조립 로직 + fallback 처리
  - **Skills**: [`python`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (Wave 2 단독)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 5
  - **Blocked By**: Tasks 1, 2

  **References**:

  **Pattern References**:
  - `auto_sap/classes/protocol_segmenter.py` (Task 1 산출물) — `get_section()`, `get_sections()`, `get_global_summary()` API
  - `auto_sap/section_mapping.py` (Task 2 산출물) — `SAP_TO_PROTOCOL_MAP`, `GLOBAL_CONTEXT_SECTIONS`

  **API/Type References**:
  - ProtocolSegmenter의 sections dict와 get 메서드들

  **WHY Each Reference Matters**:
  - segmenter API를 직접 호출하므로, 정확한 인터페이스를 알아야 함
  - mapping 구조가 `dict[str, list[str]]`이므로 iteration 방식 결정에 필요

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: primary_efficacy context가 전체 프로토콜보다 작음
    Tool: Bash (python3)
    Preconditions: Tasks 1-2 완료
    Steps:
      1. python3 -c "
from auto_sap.classes.protocol_segmenter import ProtocolSegmenter
from auto_sap.classes.context_assembler import ContextAssembler
from auto_sap.classes.protocol_classes import Protocol
from auto_sap.section_mapping import SAP_TO_PROTOCOL_MAP, GLOBAL_CONTEXT_SECTIONS
p = Protocol('../YH00000-101_Clinical Protocol_Ver1.0_22Feb2024.docx')
seg = ProtocolSegmenter(p.protocol_txt)
asm = ContextAssembler(seg, SAP_TO_PROTOCOL_MAP, GLOBAL_CONTEXT_SECTIONS)
ctx = asm.assemble('primary_efficacy')
print(f'primary_efficacy context: {len(ctx)} chars')
print(f'full protocol: {len(p.protocol_txt)} chars')
print(f'reduction: {100 - len(ctx)*100//len(p.protocol_txt)}%')
assert len(ctx) < len(p.protocol_txt)
assert '=== STUDY OVERVIEW ===' in ctx
assert '=== RELEVANT PROTOCOL SECTIONS ===' in ctx
"
    Expected Result: primary_efficacy context < 111K chars, 구조화된 포맷
    Failure Indicators: context가 전체 프로토콜과 동일 크기, 누락된 섹션
    Evidence: .sisyphus/evidence/task-3-assembler-reduction.txt

  Scenario: statistical_software_version context가 최소화됨
    Tool: Bash (python3)
    Steps:
      1. python3 -c "...; ctx = asm.assemble('statistical_software_version'); print(f'sw_version context: {len(ctx)} chars'); assert len(ctx) < 30000"
    Expected Result: 30K chars 미만 (전체 111K 대비 ~70% 축소)
    Evidence: .sisyphus/evidence/task-3-assembler-minimal.txt

  Scenario: 36개 태그 모두 assemble 가능
    Tool: Bash (python3)
    Steps:
      1. python3 -c "...; all_ctx = asm.assemble_all(); print(f'Tags assembled: {len(all_ctx)}'); assert len(all_ctx) == 36; avg = sum(len(v) for v in all_ctx.values()) // 36; print(f'Avg context: {avg} chars')"
    Expected Result: 36개 모두 성공, 평균 context < 60K
    Evidence: .sisyphus/evidence/task-3-assembler-all.txt

  Scenario: 매핑 실패 시 fallback이 전체 프로토콜로 동작
    Tool: Bash (python3)
    Steps:
      1. python3 -c "
from auto_sap.classes.protocol_segmenter import ProtocolSegmenter
from auto_sap.classes.context_assembler import ContextAssembler
from auto_sap.classes.protocol_classes import Protocol
p = Protocol('../YH00000-101_Clinical Protocol_Ver1.0_22Feb2024.docx')
seg = ProtocolSegmenter(p.protocol_txt)
# 빈 매핑으로 fallback 테스트
asm = ContextAssembler(seg, {'test_tag': ['99.99']}, ['1.1'])
ctx = asm.assemble('test_tag')
print(f'Fallback context length: {len(ctx)}')
assert len(ctx) >= len(p.protocol_txt) * 0.9  # fallback은 전체 프로토콜과 유사한 크기
print('Fallback works: PASS')
"
    Expected Result: 존재하지 않는 섹션 매핑 시 전체 프로토콜로 fallback, WARNING 로그 출력
    Failure Indicators: KeyError, 빈 문자열 반환
    Evidence: .sisyphus/evidence/task-3-assembler-fallback.txt
  ```

  **Commit**: YES
  - Message: `feat(context): add ContextAssembler for targeted-context generation`
  - Files: `auto_sap/classes/context_assembler.py`

- [ ] 4. High-complexity 2단계 생성 로직

  **What to do**:
  - `auto_sap/classes/multi_step_generator.py` 신규 생성
  - High-complexity 태그 목록: `["primary_efficacy", "secondary_efficacy", "sample_size"]`
  - 2단계 구조:
    - **Step 1 (근거 추출)**: 관련 프로토콜 섹션에서 해당 SAP 작성에 필요한 핵심 정보만 추출하는 prompt
      - 예: primary_efficacy → "프로토콜에서 primary endpoint, analysis model, analysis set, statistical test, significance level을 추출하시오"
    - **Step 2 (draft 생성)**: Step 1 결과 + 기존 SAP prompt를 결합하여 최종 SAP 섹션 생성
  - `MultiStepGenerator` 클래스:
    - `__init__(self, extraction_prompts: dict[str, str])` — 태그별 추출 프롬프트
    - `async generate(self, tag: str, context: str, sap_prompt: str, chat_bot) -> str` — 2단계 실행
  - 추출 프롬프트는 간결하게 (reasoning_effort: "low") — 핵심 정보 bullet point로 추출만
  - 생성 프롬프트는 기존 것 그대로 사용하되, context를 Step 1 결과로 교체

  **Must NOT do**:
  - 기존 프롬프트 내용 수정 (시그니처만 변경)
  - 3개 이외의 태그에 multi-step 적용
  - Step 1에 high reasoning 사용 (추출은 low로 충분)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 2단계 LLM 호출 체인 + async 통합
  - **Skills**: [`python`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2)
  - **Blocks**: Task 5
  - **Blocked By**: None (standalone 모듈, 독립적으로 설계 가능)

  **References**:

  **Pattern References**:
  - `auto_sap/classes/chat_classes.py:ClaudeCodeChatAsync.get_response()` — async LLM 호출 패턴
  - `auto_sap/prompts/prompts_yuhan_v1.py:PROMPTS_EFFICACY` — primary_efficacy, secondary_efficacy 프롬프트 내용 (어떤 정보를 추출해야 하는지 유추)
  - `auto_sap/prompts/prompts_yuhan_v1.py:PROMPTS_SAMPLE_SIZE` — sample_size 프롬프트

  **WHY Each Reference Matters**:
  - `chat_classes.py` — async get_response 시그니처를 알아야 2단계 호출 체인 구현 가능
  - 기존 프롬프트 — Step 1 추출 프롬프트를 설계할 때, 최종 SAP에 어떤 정보가 필요한지 알아야 함

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: MultiStepGenerator 인스턴스 생성 및 태그 목록 확인
    Tool: Bash (python3)
    Steps:
      1. python3 -c "from auto_sap.classes.multi_step_generator import MultiStepGenerator, HIGH_COMPLEXITY_TAGS; print(HIGH_COMPLEXITY_TAGS); assert set(HIGH_COMPLEXITY_TAGS) == {'primary_efficacy', 'secondary_efficacy', 'sample_size'}"
    Expected Result: 3개 태그 정확히 일치
    Evidence: .sisyphus/evidence/task-4-multistep-tags.txt

  Scenario: extraction prompt 존재 확인
    Tool: Bash (python3)
    Steps:
      1. python3 -c "from auto_sap.classes.multi_step_generator import MultiStepGenerator; g = MultiStepGenerator(); assert all(tag in g.extraction_prompts for tag in ['primary_efficacy', 'secondary_efficacy', 'sample_size']); print('All extraction prompts present: PASS')"
    Expected Result: 3개 태그 모두 추출 프롬프트 존재
    Evidence: .sisyphus/evidence/task-4-multistep-prompts.txt
  ```

  **Commit**: YES
  - Message: `feat(generation): add MultiStepGenerator for high-complexity SAP sections`
  - Files: `auto_sap/classes/multi_step_generator.py`

- [ ] 5. template_class.py 리팩터링 + chat_classes 시그니처 변경

  **What to do**:

  **A. template_class.py 리팩터링**:
  - `get_sap_content_async()` 메서드 변경:
    1. Protocol 텍스트 → `ProtocolSegmenter`로 섹셔닝
    2. `ContextAssembler`로 태그별 context 조립 (`context_map = assembler.assemble_all()`)
    3. High-complexity 태그는 `MultiStepGenerator` 사용
    4. 나머지 태그는 기존 방식 (단, system_message에 전체 프로토콜 대신 targeted context 사용)
  - 기존 system_message_function을 유지하되, 호출 시 전체 protocol 대신 assembled context를 전달
  - 각 태그별로 별도 chat_bot 인스턴스 생성 (태그마다 다른 system_message)
  - Wave 실행은 기존 async 방식 유지 (asyncio.gather) — 이미 병렬화되어 있으므로 wave 분리는 불필요
  - `write_sap()` 외부 인터페이스는 변경 없음

  **B. chat_classes.py 시그니처 변경** (Task 6/7 통합):
  - 현재 `run_prompts_register()`는 모든 프롬프트에 동일 system_message 사용
  - **변경 방식 결정**: 두 가지 방법 중 하나 선택:
    - **Option A** (권장): `run_prompts_register`를 사용하지 않고, `get_sap_content_async`에서 직접 태그별 chat_bot을 생성하여 `get_response()` 호출. 기존 `run_prompts_register`는 그대로 유지 (하위 호환).
    - **Option B**: `run_prompts_register`에 `context_map` 파라미터 추가. 주어지면 태그별로 system_message 재구성.
  - Option A가 더 깔끔: template_class만 변경하면 되고 chat_classes는 건드리지 않음

  **C. prompts_yuhan_v1.py**:
  - `system_message()` 함수 내부 변경 없음
  - docstring만 업데이트: "protocol_text 인자에 전체 프로토콜 또는 targeted context가 전달될 수 있음"

  **Must NOT do**:
  - write_sap() 시그니처 변경
  - 새로운 CLI 인자 추가
  - 기존 backend 선택 로직 변경
  - 프롬프트 텍스트 내용 변경

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 기존 코드와의 통합이 핵심. 여러 새 모듈을 조립하면서 하위 호환 유지
  - **Skills**: [`python`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (단독)
  - **Blocks**: Task 6
  - **Blocked By**: Tasks 3, 4

  **References**:

  **Pattern References**:
  - `auto_sap/classes/template_class.py:get_sap_content_async()` — 현재 구현 (리팩터링 대상)
  - `auto_sap/classes/template_class.py:write_sap()` — 외부 인터페이스 (변경 불가)
  - `auto_sap/classes/chat_classes.py:ClaudeCodeChatAsync.run_prompts_register()` — 현재 async 실행 패턴

  **API/Type References**:
  - `ContextAssembler.assemble(tag) -> str` (Task 3 산출물)
  - `ContextAssembler.assemble_all() -> dict[str, str]` (Task 3 산출물)
  - `MultiStepGenerator.generate(tag, context, prompt, chat_bot) -> str` (Task 4 산출물)
  - `ProtocolSegmenter(protocol_txt) -> ProtocolSegmenter` (Task 1 산출물)

  **WHY Each Reference Matters**:
  - `get_sap_content_async` — 이 메서드가 리팩터링의 핵심 대상. 현재 동작을 완벽히 이해해야 안전하게 변경 가능
  - `write_sap` — 이 메서드의 시그니처가 변경되면 안 됨. 호출부 확인 필요
  - `run_prompts_register` — 현재 system_message가 chat_bot 초기화 시 설정되므로, targeted context 방식에서는 태그별로 다른 system_message가 필요. 이 부분의 아키텍처 변경이 핵심

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: write_sap() 시그니처 변경 없음 확인
    Tool: Bash (python3)
    Steps:
      1. python3 -c "import inspect; from auto_sap.classes.template_class import Template; sig = inspect.signature(Template.write_sap); print(f'Parameters: {list(sig.parameters.keys())}'); assert 'protocol_path' in sig.parameters; assert 'sap_name' in sig.parameters"
    Expected Result: protocol_path, sap_name 파라미터 존재
    Evidence: .sisyphus/evidence/task-5-api-compat.txt

  Scenario: targeted context가 실제로 사용되는지 확인 (로그 기반)
    Tool: Bash (python3)
    Steps:
      1. 테스트 모드로 1개 섹션만 실행하여 로그에서 context size 확인
      2. Context size가 111K 미만인지 검증
    Expected Result: 로그에 각 태그별 context size 출력, 모두 < 111K
    Evidence: .sisyphus/evidence/task-5-targeted-context-log.txt
  ```

  **Commit**: YES
  - Message: `refactor(template): integrate targeted-context and multi-step generation`
  - Files: `auto_sap/classes/template_class.py`, `auto_sap/prompts/prompts_yuhan_v1.py`

- [ ] 6. E2E 검증 + baseline 비교

  **What to do**:
  - YH00000 프로토콜로 전체 파이프라인 실행 (test mode: haiku)
  - 기존 결과물 `SAPs/YH_SAP_YH00000-101_Clinical Protocol_Ver1.0_22Feb2024_content.txt`와 비교
  - 검증 항목:
    1. 36개 섹션 모두 생성됨 (0 ERROR)
    2. 각 태그별 context size 로그 → 평균 50% 이상 감소 확인
    3. 생성 품질 spot-check: primary_efficacy, sample_size, introduction 3개 섹션 비교
    4. 실행 시간 기록
    5. docx 정상 생성 및 열림 확인
    6. **매핑 완전성 검증**: fallback WARNING이 0개인지 확인. WARNING 발생 시 해당 태그의 매핑 보강 필요
    7. **매핑 커버리지 검증**: 각 태그별 targeted context에 기존 결과물의 핵심 키워드가 포함되는지 샘플 체크
  - 결과를 `.sisyphus/evidence/task-6-e2e-results.md`에 기록

  **Must NOT do**:
  - production 모드(sonnet)로 실행 (비용/시간)
  - 기존 결과물 삭제 또는 덮어쓰기

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`python`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 4 (단독)
  - **Blocks**: None (최종 태스크)
  - **Blocked By**: Task 5

  **References**:

  **Pattern References**:
  - `WriteSAPs/yuhan_sap.py` — 실행 커맨드 패턴
  - `SAPs/YH_SAP_YH00000-101_Clinical Protocol_Ver1.0_22Feb2024_content.txt` — baseline 결과물

  **WHY Each Reference Matters**:
  - `yuhan_sap.py` — 실행 방법과 --test 플래그 확인
  - baseline content.txt — 비교 대상. 새 결과가 이보다 품질이 낮으면 안 됨

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: E2E 파이프라인 성공
    Tool: Bash
    Preconditions: Tasks 1-5 완료, venv 활성화
    Steps:
      1. cd sap-kcl && source ../YH-SAP-venv/bin/activate
      2. python3 -m WriteSAPs.yuhan_sap "../YH00000-101_Clinical Protocol_Ver1.0_22Feb2024.docx" --test --output-dir SAPs_v3
      3. grep -c "ERROR" SAPs_v3/*_content.txt
      4. wc -c SAPs_v3/*.docx
    Expected Result: 0 ERROR lines, docx file > 100KB
    Failure Indicators: ERROR in content, docx missing or empty, timeout
    Evidence: .sisyphus/evidence/task-6-e2e-pipeline.txt

  Scenario: Context size reduction 확인
    Tool: Bash
    Steps:
      1. 실행 로그에서 각 태그별 context size 추출
      2. 평균 계산
      3. assert avg_context < 60000 (111K의 ~54%)
    Expected Result: 평균 context < 60K chars
    Evidence: .sisyphus/evidence/task-6-context-reduction.txt

  Scenario: 품질 spot-check (primary_efficacy)
    Tool: Bash
    Steps:
      1. grep -A 50 "primary_efficacy:" SAPs_v3/*_content.txt > new_primary.txt
      2. grep -A 50 "primary_efficacy:" SAPs/*_content.txt > old_primary.txt
      3. wc -w new_primary.txt old_primary.txt  # 단어 수 비교
      4. 내용이 빈 문자열이나 ERROR가 아닌지 확인
    Expected Result: 새 결과가 기존과 비슷한 길이, 의미 있는 내용 포함
    Evidence: .sisyphus/evidence/task-6-quality-spotcheck.txt

  Scenario: 매핑 완전성 — fallback WARNING 0건
    Tool: Bash
    Steps:
      1. 실행 로그에서 "WARNING.*falling back" 패턴 grep
      2. 발견 건수 == 0 확인
    Expected Result: fallback WARNING 0건 (모든 태그가 targeted context로 정상 동작)
    Failure Indicators: 1건 이상의 WARNING → 해당 태그 매핑 보강 필요
    Evidence: .sisyphus/evidence/task-6-mapping-completeness.txt

  Scenario: 매핑 커버리지 — targeted context에 핵심 키워드 존재
    Tool: Bash (python3)
    Steps:
      1. primary_efficacy context에 "TEAE" 또는 "adverse" 키워드 확인 (이 태그는 AE 관련이 아니므로 없어도 됨)
      2. adverse_events context에 "이상사례" 또는 "adverse event" 키워드 확인
      3. sample_size context에 "시험대상자 수" 또는 "sample size" 키워드 확인
      4. visit_windows context에 "수행 일정" 또는 "schedule" 키워드 확인
    Expected Result: 각 태그의 context에 해당 도메인 핵심 키워드 존재
    Evidence: .sisyphus/evidence/task-6-mapping-coverage.txt
  ```

  **Commit**: NO (검증만)

---

## Final Verification Wave

> After ALL implementation tasks, run verification.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read plan. Verify each deliverable exists. Check "Must NOT Have" compliance. Compare context sizes.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | VERDICT`

- [ ] F2. **E2E Quality Check** — `unspecified-high`
  Run full pipeline with YH00000 protocol. Compare output with existing `SAPs/YH_SAP_YH00000-101_Clinical Protocol_Ver1.0_22Feb2024_content.txt`. Verify 36/36 sections generated, 0 errors.
  Output: `Sections [N/N] | Errors [N] | Quality [PASS/FAIL] | VERDICT`

---

## Commit Strategy

- **Wave 1**: `feat(protocol): add ProtocolSegmenter, section mapping, and MultiStepGenerator` — protocol_segmenter.py, section_mapping.py, multi_step_generator.py
- **Wave 2**: `feat(context): add ContextAssembler for targeted-context generation` — context_assembler.py
- **Wave 3**: `refactor(template): integrate targeted-context and multi-step generation` — template_class.py, prompts_yuhan_v1.py
- **Wave 4**: `test(e2e): validate pipeline with YH00000 protocol` — verification only

---

## Success Criteria

### Verification Commands
```bash
cd sap-kcl && source ../YH-SAP-venv/bin/activate
python3 -m WriteSAPs.yuhan_sap ../YH00000-101_Clinical\ Protocol_Ver1.0_22Feb2024.docx --test
# Expected: 36 sections generated, 0 errors, output in SAPs/
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] write_sap() API unchanged
- [ ] Context size reduction ≥50%
- [ ] E2E output quality ≥ baseline
