# YH-SAP

임상시험 프로토콜 → Statistical Analysis Plan (SAP) 초안 자동생성 파이프라인

> KCL(King's College London) 오픈소스 [sap-kcl](https://github.com/rct-sap-ai/sap-kcl)를 기반으로, 유한양행 SAP 양식에 맞는 초안을 자동생성합니다.

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| **46개 SAP 섹션 자동생성** | 프로토콜(PDF/DOCX)에서 모든 SAP 섹션을 한 번에 생성 |
| **Targeted-Context** | 프로토콜을 126개 섹션으로 분할, 태그별 관련 부분만 주입 (88% 컨텍스트 축소) |
| **JSON 구조화 출력** | LLM이 JSON으로 응답 → python-docx가 paragraph 단위 서식 적용 |
| **프로토콜 테이블 자동 삽입** | Objectives, Schedule of Activities, PK Parameters 등 12개 테이블 추출·삽입 |
| **SKIP 마커 + 노란 하이라이트** | 프로토콜에 정보 없는 섹션은 억지로 쓰지 않고 노란색으로 표시 |
| **Instruction 박스 자동 제거** | 양식의 회색 가이드 박스 37개를 최종 SAP에서 제거 |
| **PK/PD 일반화** | Phase 1 시험도 지원 (efficacy 대신 PK/PD 분석 자동 전환) |
| **재시도 로직** | LLM 빈 응답 시 최대 2회 자동 재시도 |

## 아키텍처

```
Protocol (PDF/DOCX)
    │
    ├─ ProtocolSegmenter ──── heading 기반 126개 섹션 분할
    │
    ├─ ProtocolTableExtractor ─ 핵심 테이블 12개 추출 (DOCX만)
    │
    ▼
ContextAssembler ──── SAP 태그별 관련 섹션 조립
    │                  + 공통 컨텍스트 (Protocol Synopsis)
    ▼
LLM (Claude Opus / Sonnet / Haiku)
    │  ┌─ 일반 섹션: 1단계 JSON 생성
    │  └─ 고복잡도 섹션: 2단계 (근거 추출 → 생성)
    ▼
JsonSapRenderer
    │  ┌─ JSON → paragraph 단위 docx 렌더링
    │  ├─ 프로토콜 테이블 삽입
    │  ├─ [SKIP] → 노란 하이라이트 변환
    │  ├─ 파란색 텍스트 → 검정 변환
    │  └─ Instruction 박스 제거
    ▼
SAP.docx
```

---

## 설치 가이드

### Step 1: 저장소 클론

```bash
git clone https://github.com/minpark0427/YH-SAP.git
cd YH-SAP
```

### Step 2: Python 가상환경 설정

```bash
# Python 3.11 이상 필요
python3 -m venv YH-SAP-venv
source YH-SAP-venv/bin/activate   # Mac/Linux
# Windows: YH-SAP-venv\Scripts\activate

pip install -r sap-kcl/requirements.txt
pip install python-docx docxtpl PyPDF2 anthropic python-dotenv
```

### Step 3: Claude Code 설치

이 파이프라인의 기본 LLM 백엔드는 **Claude Code CLI**입니다.

```bash
# Claude Code CLI 설치 (npm 필요)
npm install -g @anthropic-ai/claude-code

# 인증 (최초 1회)
claude login

# 설치 확인
claude --version
```

> Claude Code는 Anthropic 구독이 필요합니다. API 키 방식을 사용하려면 `--backend anthropic`을 사용하세요.

### Step 4: 프로토콜 파일 준비

프로젝트 루트에 분석할 프로토콜 파일을 넣습니다:

```bash
# 예시
cp /path/to/YH#####-###_Clinical_Protocol.docx .
```

> **DOCX 권장**: DOCX 프로토콜은 테이블 자동 추출이 가능합니다. PDF는 텍스트만 추출됩니다.

---

## 사용 방법

### 기본 실행

```bash
cd sap-kcl
source ../YH-SAP-venv/bin/activate

# SAP 생성 (기본 모델: claude-sonnet-4-6)
python -m WriteSAPs.yuhan_sap_json ../프로토콜파일.docx
```

### 모델 선택

```bash
# 테스트 (빠름, 1-2분) — 프롬프트 수정 후 빠른 확인용
python -m WriteSAPs.yuhan_sap_json ../프로토콜.docx --test

# 기본 (sonnet, 3-5분) — 일상 업무용
python -m WriteSAPs.yuhan_sap_json ../프로토콜.docx

# 최고 품질 (opus, 10-15분) — 최종 제출용
python -m WriteSAPs.yuhan_sap_json ../프로토콜.docx --model claude-opus-4-6
```

| 모델 | 속도 | 품질 | 용도 |
|------|------|------|------|
| `claude-haiku-4-5` | ~80초 | ★★★ | 테스트, 프롬프트 튜닝 |
| `claude-sonnet-4-6` (기본) | ~3분 | ★★★★ | 일상 업무, 팀 배포 |
| `claude-opus-4-6` | ~10분 | ★★★★★ | 최종 제출, 통계 추론 |

### 출력 디렉토리 지정

```bash
python -m WriteSAPs.yuhan_sap_json ../프로토콜.docx --output-dir SAPs_출력폴더
```

### 출력 파일

```
SAPs_출력폴더/
├── YH_SAP_프로토콜명.docx         ← SAP 문서 (Word로 열기)
└── YH_SAP_프로토콜명_content.txt  ← 원문 텍스트 (디버깅용)
```

---

## Claude Code로 SAP 생성하기 (권장 워크플로우)

Claude Code는 AI와 대화하면서 코드를 실행할 수 있는 터미널 도구입니다.
SAP 생성을 가장 쉽게 하는 방법입니다.

### 1단계: 터미널에서 Claude Code 열기

```bash
# YH-SAP 폴더로 이동
cd /path/to/YH-SAP

# Claude Code 시작 — 프로젝트 폴더에서 실행해야 CLAUDE.md를 자동 인식합니다
claude
```

터미널에 `>` 프롬프트가 나타나면 준비 완료입니다.

### 2단계: SAP 생성 요청 (자연어)

Claude Code 프롬프트에 한국어 또는 영어로 요청합니다:

```
> 프로토콜 파일 YH12345-101_Clinical_Protocol.docx로 SAP를 생성해줘.
> 테스트 모드로 먼저 돌려봐.
```

Claude Code가 알아서:
1. 가상환경을 활성화하고
2. 파이프라인을 실행하고
3. 결과를 확인해서 알려줍니다

### 3단계: 결과 확인 및 재실행

```
> 결과 어때? ERROR나 SKIP이 몇 개야?

> 괜찮으면 sonnet 모델로 다시 생성해줘.

> primary_efficacy 섹션만 opus로 다시 생성할 수 있어?
```

### 실제 사용 예시 (대화 흐름)

```
사용자> 이 프로토콜로 SAP 만들어줘: ../YH00000-101_Clinical Protocol_Ver1.0_22Feb2024.docx
       테스트 모드로 먼저 해봐

Claude> [파이프라인 실행 중... 46개 섹션 생성]
       완료! 결과:
       - 46/46 섹션 생성
       - 23개 SKIP (프로토콜에 없는 내용)
       - 19개 테이블 (12개 프로토콜에서 추출)
       SAPs_v4_json/ 폴더에 저장됨

사용자> SKIP된 항목 중에 FAS 정의는 왜 SKIP이야?

Claude> 프로토콜에 Full Analysis Set(FAS)이 명시적으로 정의되어 있지 않습니다.
       Safety Analysis Population, PK Analysis Set 등은 있지만 FAS는 없습니다.
       통계 담당자가 직접 정의해야 합니다.

사용자> 알겠어. 이제 sonnet으로 최종본 만들어줘.

Claude> [claude-sonnet-4-6으로 재실행... 3분]
       완료! SAPs_final/ 폴더에 저장됨
```

### 직접 명령어 실행 (대화 없이)

대화 모드 없이 한 줄로 실행할 수도 있습니다:

```bash
# 터미널에서 직접 (Claude Code 밖에서)
cd YH-SAP/sap-kcl
source ../YH-SAP-venv/bin/activate

# 테스트 (haiku, ~80초)
python -m WriteSAPs.yuhan_sap_json ../프로토콜.docx --test

# 기본 (sonnet, ~3분)
python -m WriteSAPs.yuhan_sap_json ../프로토콜.docx

# 최고 품질 (opus, ~10분)
python -m WriteSAPs.yuhan_sap_json ../프로토콜.docx --model claude-opus-4-6

# 출력 폴더 지정
python -m WriteSAPs.yuhan_sap_json ../프로토콜.docx --output-dir SAPs_최종
```

---

## 출력물 이해하기

### 정상 내용
일반 검정 텍스트로 프로토콜 기반 SAP 내용이 작성됩니다.

### 노란색 하이라이트 `[REVIEW NEEDED]`
프로토콜에 관련 정보가 부족하여 AI가 내용을 생성하지 못한 섹션입니다.
→ 통계 담당자가 직접 작성하거나 프로토콜 확인 후 보완해야 합니다.

### 프로토콜 테이블
프로토콜에서 자동 추출된 테이블(Objectives, Schedule of Activities, PK Parameters 등)이 해당 섹션에 삽입됩니다.

---

## 검증 결과

5회 반복 실행, 9개 검증 기준 — **45/45 ALL PASS**

| Run | 시간 | Paragraphs | Tables | DOCX | SKIP 마커 |
|-----|------|-----------|--------|------|----------|
| 1 | 84s | 359 | 19 | 384KB | 21 |
| 2 | 69s | 348 | 19 | 385KB | 25 |
| 3 | 79s | 334 | 19 | 384KB | 21 |
| 4 | 86s | 381 | 19 | 385KB | 22 |
| 5 | 78s | 385 | 19 | 386KB | 28 |

검증 기준: 46태그 완전생성, 0에러, Instruction제거, 마크다운없음, 파란색없음, 테이블삽입, DOCX유효, 노란하이라이트, SKIP마커

상세 보고서: [`docs/validation-report.md`](docs/validation-report.md)

---

## 프로젝트 구조

```
YH-SAP/
├── README.md                               ← 이 파일
├── CLAUDE.md                               ← Claude Code 가이드
├── docs/
│   ├── architecture-evolution.md           ← Phase 0-5 발전 과정
│   ├── gap-analysis.md                     ← 계획서 vs 양식 vs 구현 GAP 분석
│   └── validation-report.md                ← 5x 검증 보고서
├── scripts/
│   ├── create_yuhan_template.py            ← 양식에서 Jinja2 템플릿 생성
│   ├── validate_sap.py                     ← LLM 기반 품질 검증
│   ├── verify_sap_quality.py               ← 자동 + LLM 품질 검증
│   └── run_validation_5x.py               ← 5회 반복 검증 스크립트
│
└── sap-kcl/                                ← 핵심 파이프라인
    ├── auto_sap/
    │   ├── classes/
    │   │   ├── protocol_classes.py         ← Protocol 로더 (PDF/DOCX/TXT)
    │   │   ├── protocol_segmenter.py       ← heading 기반 섹셔닝 (126개)
    │   │   ├── context_assembler.py        ← 태그별 targeted context 조립
    │   │   ├── multi_step_generator.py     ← 고복잡도 2단계 생성
    │   │   ├── table_extractor.py          ← 프로토콜 테이블 추출 (12개)
    │   │   ├── json_renderer.py            ← JSON → docx 렌더러
    │   │   ├── template_class.py           ← docxtpl 렌더러 (레거시)
    │   │   └── chat_classes.py             ← LLM 백엔드 (3종 + 재시도)
    │   ├── prompts/
    │   │   └── prompts_yuhan_v1.py         ← 46개 SAP 프롬프트
    │   ├── section_mapping.py              ← SAP 태그 → 프로토콜 섹션 매핑
    │   ├── generate_templates/
    │   │   └── generate_yuhan_template.py  ← 46개 PromptRegister 정의
    │   └── templates/
    │       └── yuhan_sap_template_v1.0.docx
    │
    └── WriteSAPs/
        ├── yuhan_sap_json.py               ← JSON 러너 (권장)
        └── yuhan_sap.py                    ← docxtpl 러너 (레거시)
```

## SAP 섹션 (46개 태그)

| # | 섹션 | 태그 | 복잡도 |
|---|------|------|--------|
| 1 | Abbreviations | `abbreviations` | Low |
| 2 | Introduction | `introduction` | Medium |
| 3 | Objectives | `objectives` | Low |
| — | General Considerations | `general_considerations` | Medium |
| 4.1–4.5 | Analysis Sets | `screened_set` `randomized_set` `safety_set` `fas_definition` `pps_definition` | Minimal–Low |
| 5 | Subject Disposition | `subject_disposition` | Low |
| 6 | Demographics | `demographics` | Low |
| 7.1–7.2 | Exposure / Compliance | `ip_exposure` `treatment_compliance` | Low |
| 8.1–8.2 | Medical History / Meds | `medical_history` `concomitant_medication` | Minimal–Low |
| — | Special Screening Tests | `special_tests` | Low |
| 9.1 | Primary Analysis (Efficacy/PK) | `primary_efficacy` | **High** |
| 9.2 | Secondary Analysis (Efficacy/PD) | `secondary_efficacy` | **High** |
| 9.3 | Additional/Exploratory | `additional_efficacy` | Medium |
| — | Preliminary PK / PD | `preliminary_pk` `preliminary_pd` | Medium |
| — | Blinded Analyses | `blinded_analyses` | Low |
| 10.1–10.6 | Safety | `adverse_events` `lab_parameters` `vital_signs` `ecg` `physical_exam` `other_safety` | Low–Medium |
| 11 | Interim Analysis | `interim_analysis` | Low |
| — | DMC Analysis | `dmc_analysis` | Minimal |
| 12 | Sample Size | `sample_size` | **High** |
| 13 | Statistical Software | `statistical_software_version` | Minimal |
| — | Statistical Considerations | `statistical_considerations` | Medium |
| 14.1–14.8 | Data Handling | `visit_windows` `derived_variables` `repeated_assessments` `missing_last_dose_date` `missing_ae_severity` `missing_causality` `missing_dates` `lab_char_values` | Low–Medium |
| — | Protocol Deviation | `protocol_deviation` | Low |
| — | Baseline Definition | `baseline_definition` | Low |
| — | Subgroup Analysis | `subgroup_analysis` | Low |
| — | References | `references` | Low |
| 15 | Protocol Changes | `protocol_changes` | Low |

---

## 참고

- **원본 오픈소스**: [rct-sap-ai/sap-kcl](https://github.com/rct-sap-ai/sap-kcl)
- **논문**: Jafari et al. (2026), *"From Protocol to Analysis Plan: Development and Validation of a LLM Pipeline for SAP Generation (SAPAI)"*
- **발전 과정**: [`docs/architecture-evolution.md`](docs/architecture-evolution.md)
- **GAP 분석**: [`docs/gap-analysis.md`](docs/gap-analysis.md)
- **검증 보고서**: [`docs/validation-report.md`](docs/validation-report.md)

## 라이선스

이 프로젝트는 [sap-kcl](https://github.com/rct-sap-ai/sap-kcl) 오픈소스를 기반으로 합니다.
