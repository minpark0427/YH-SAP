# YH-SAP Architecture Evolution

> sap-kcl 원본에서 유한 SAP 파이프라인으로의 발전 과정

---

## Phase 0: 원본 sap-kcl (KCL 오픈소스)

**논문**: Jafari et al. (2026), "From Protocol to Analysis Plan: Development and Validation of a Large Language Model Pipeline for Statistical Analysis Plan Generation using Artificial Intelligence (SAPAI)"

**원본 아키텍처**:
```
Protocol PDF → Protocol 클래스 (텍스트 추출)
    → system_message(전체 프로토콜 텍스트)
    → 36개 프롬프트를 순차/병렬 LLM 호출
    → docxtpl로 {{ tag }} 위치에 plain text 삽입
    → SAP.docx 출력
```

**핵심 설계 결정**:
- LLM 출력을 **단일 string**으로 받아 docxtpl의 `{{ tag }}` 위치에 그대로 삽입
- 전체 프로토콜(~100K chars)을 **매 호출마다 system_message로 반복 주입**
- OpenAI GPT 기반, `reasoning_effort` / `verbosity` 파라미터로 난이도 조절
- 출력 포맷에 대한 제약 없음 → LLM이 자유 형식으로 응답

**논문 결과**: 전체 정확도 77-78%, 통계 추론 항목 67-72%. Human-in-the-loop 필수.

---

## Phase 1: 유한 양식 적응 (2024.03)

**변경 사항**:
- KCL 템플릿 → 유한 SAP 템플릿 (36개 태그)
- KCL 프롬프트 → 유한 SAP 프롬프트 (한국 제약 임상시험 맥락)
- OpenAI → Anthropic Claude (claudecode 백엔드 추가)
- DOCX 프로토콜 지원 (기존 PDF만 → PDF/DOCX/TXT)

**남은 문제**:
- 전체 프로토콜 반복 주입 → 컨텍스트 비효율
- docxtpl 단일 string 삽입 → 서식 제어 불가

---

## Phase 2: Targeted-Context Generation (2024.04)

**핵심 개선**: 전체 프로토콜 111K를 매번 주입하는 대신, 태그별 관련 섹션만 선택적 주입.

**새로 추가된 모듈**:
- `ProtocolSegmenter`: 프로토콜 heading 기반 섹셔닝 (126개 섹션)
- `SECTION_MAPPING`: SAP 태그 → 프로토콜 섹션 매핑 (36개)
- `ContextAssembler`: 공통 컨텍스트 + 태그별 섹션 조립, fallback 안전장치
- `MultiStepGenerator`: 고복잡도 섹션(primary_efficacy, sample_size 등)은 2단계 생성

**결과**: 89% 컨텍스트 축소 (평균 12.5K/호출), 실행시간 57% 단축.

**남은 문제**: LLM이 markdown 문법으로 응답 → docxtpl이 plain text로 삽입 → `# Heading`, `**bold**` 등이 그대로 표시됨.

---

## Phase 3: JSON 구조화 출력 + python-docx 직접 빌드 (현재)

### 문제 진단

docxtpl 방식의 근본적 한계:
1. `{{ tag }}`에는 **string 하나**만 삽입 가능
2. LLM 출력이 여러 paragraph로 구성되어야 하는데, 하나의 paragraph에 모든 텍스트가 들어감
3. 서식(bold, bullet, 들여쓰기)을 제어할 방법이 없음
4. LLM에게 "markdown 쓰지 마"라고 해도 불안정 (프롬프트 강제는 100% 보장 불가)

사람이 작성한 SAP(`YH00000-101_SAP ver1.0`)의 docx 구조:
- Heading 스타일 미사용 → `List Paragraph`(bold)로 제목, `Normal`로 본문
- 각 문장/단락이 별도의 paragraph element
- 색상은 기본 검정, bold는 run-level formatting

### 해결: JSON 구조화 출력

**Before (docxtpl 방식)**:
```
LLM → "# Introduction\n\n**Background**: YH00000 is..." (markdown string)
    → docxtpl {{ introduction }} 에 그대로 삽입
    → docx에서 "# Introduction\n\n**Background**: YH00000 is..." 텍스트로 표시
```

**After (JSON + python-docx 방식)**:
```
LLM → {"paragraphs": [
         {"text": "Gaucher disease is...", "style": "body"},
         {"text": "YH00000 is a novel...", "style": "body"},
         {"text": "Primary Objective", "style": "bold"},
         {"text": "To evaluate safety...", "style": "body"}
       ]}
    → python-docx가 각 item을 별도 paragraph로 생성
    → style별로 적절한 Word 스타일 적용 (Normal, bold run, ListParagraph 등)
    → docx에서 사람이 쓴 것과 동일한 구조
```

### 기술적 변경

| 구성요소 | docxtpl 방식 (Phase 2) | JSON 방식 (Phase 3) |
|---------|----------------------|-------------------|
| LLM 출력 포맷 | 자유 텍스트 (markdown 혼재) | JSON `{"paragraphs": [...]}` |
| 템플릿 엔진 | docxtpl (Jinja2 in docx) | python-docx 직접 빌드 |
| 서식 제어 | 불가 (단일 string 삽입) | paragraph별 style 매핑 |
| Heading 처리 | LLM이 `#` 문법 사용 → 텍스트로 표시 | `"style": "bold"` → run bold |
| Bullet 처리 | LLM이 `- ` 문법 → 텍스트로 표시 | `"style": "bullet"` → ListParagraph |
| 색상 | 템플릿 placeholder 색상 상속 | 검정(`000000`) 강제 |
| Fallback | 없음 | JSON 파싱 실패 시 plain text → paragraph 분할 |

---

## Phase 4: GAP Analysis + PK/PD 일반화 + 태그 확장 (현재)

### 문제 진단

계획서, SAP 양식, 사람 작성 SAP를 3방향 교차 검증한 결과:

1. **CRITICAL: PK/PD 분석 미스매치** — 프롬프트가 "Primary Efficacy Parameter" 관점으로 설계되어 있어, Phase 1 (efficacy 없음, PK/PD 중심)에서 LLM이 "Not applicable" 반환
2. **Phase 1 특화 섹션 누락** — 사람이 작성한 SAP에는 Protocol Deviation, Baseline Definition, Subgroup Analysis 등이 별도 섹션으로 존재
3. **커버/행정 태그 미구현** — study_number 등 계획서에 명시된 5개 태그

### 해결

**PK/PD 프롬프트 일반화:**
```
기존: "Write the Primary Efficacy Parameter(s) section"
변경: "Write the Primary Analysis Parameter(s) section.
       IMPORTANT: For Phase 1 studies without formal efficacy endpoints,
       describe the primary PK analysis plan instead."
```

모든 efficacy 프롬프트(primary, secondary, additional)에 Phase 조건 분기 추가.

**신규 태그 3개 추가:**

| 태그 | 섹션 | 설명 |
|------|------|------|
| `protocol_deviation` | 4.4 | 프로토콜 위반 분류/요약 방법 |
| `baseline_definition` | 4.13 | 분석 변수의 베이스라인 정의 규칙 |
| `subgroup_analysis` | 4.18 | 하위그룹 분석 계획 |

**결과: 36개 → 39개 태그**, 3방향 완전 일치 유지 (prompts ↔ register ↔ mapping).

### 파일 구조

```
auto_sap/
├── classes/
│   ├── template_class.py          ← Phase 2 (docxtpl, A안) — 유지
│   ├── json_renderer.py           ← Phase 3 (python-docx, B안) — 신규
│   ├── protocol_segmenter.py      ← Phase 2 — 공유
│   ├── context_assembler.py       ← Phase 2 — 공유
│   └── multi_step_generator.py    ← Phase 2 — 공유
├── section_mapping.py             ← Phase 2 — 공유
└── prompts/
    └── prompts_yuhan_v1.py        ← 공유 (system_message에 JSON 포맷 지시 추가)

WriteSAPs/
├── yuhan_sap.py                   ← Phase 2 runner (A안)
└── yuhan_sap_json.py              ← Phase 3 runner (B안)
```

---

## 요약: 각 Phase별 핵심 기여

| Phase | 핵심 변경 | 해결한 문제 |
|-------|---------|-----------|
| 0 (원본) | sap-kcl 오픈소스 | 기반 아키텍처 |
| 1 (양식 적응) | 유한 템플릿 + Claude 백엔드 | 한국 제약사 양식 지원 |
| 2 (Targeted Context) | 섹셔닝 + 매핑 + 2단계 생성 | 컨텍스트 비효율 (89% 축소) |
| 3 (JSON 구조화) | JSON 출력 + python-docx | 서식 제어 + 문서 품질 |
| 4 (GAP 해소) | PK/PD 일반화 + 태그 확장 (36→39) | Phase 1 대응 + 섹션 누락 |
