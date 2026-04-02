# SAP-AI 자동생성 프로그램 도입 계획서

> **목표**: KCL(King's College London) 오픈소스 [`sap-kcl`](https://github.com/rct-sap-ai/sap-kcl)를 기반으로, 유한 SAP 양식에 맞는 초안 자동생성 프로그램을 개발한다.

---

## 1. 배경 및 근거

### 오픈소스 개요
- **레포**: `rct-sap-ai/sap-kcl`
- **기능**: 임상시험 프로토콜(PDF) → LLM 파이프라인 → SAP 초안(DOCX) 자동 생성
- **핵심 논문**: *"From Protocol to Analysis Plan: Development and Validation of a Large Language Model Pipeline for Statistical Analysis Plan Generation using Artificial Intelligence (SAPAI)"* — medRxiv 2026-03-19

### 논문 핵심 결과 (GPT-5 / Claude Sonnet 4 / Gemini 2.5 Pro 비교)

| 항목 | 결과 |
|---|---|
| 전체 정확도 | 77–78% |
| 행정·설계 항목 정확도 | 81–83% |
| 통계적 추론 항목 정확도 | 67–72% |
| 모델 간 차이 | 없음 (p=0.79) |
| 결론 | Human-in-the-loop 필수, 초안 작성에 실질적 시간 절감 가능 |

### 도입 이유
- SAP 작성은 시간·전문성 집약적 작업
- 프로토콜에서 반복 추출하는 항목(행정정보, 시험 설계, 분석 방법 등)은 LLM으로 충분히 자동화 가능
- 기존 KCL 템플릿 구조 → 유한 양식으로 교체만 하면 바로 활용 가능한 아키텍처

---

## 2. 유한 SAP 양식 분석

### 파일 분석 결과
- **분석 파일**: `SBS02T01_Ver02_Statistical_Analysis_Plan_20251212.docx`
- 단락 수: 314 | 표 수: 45

### 유한 SAP 목차 구조

| 섹션 | 제목 | 자동화 가능 여부 |
|---|---|---|
| Cover | Study Number, Title, Version | ✅ 프로토콜 추출 |
| Signature Page | Prepared/Checked/Approved by | ⛔ 수동 입력 |
| 1 | LIST OF ABBREVIATIONS | 🔶 반자동 (목록 생성) |
| 2 | INTRODUCTION | ✅ |
| 3 | OBJECTIVES | ✅ |
| 4 | ANALYSIS SETS | ✅ (표준 문구) |
| 4.1–4.5 | Screened / Randomized / Safety / FAS / PPS | ✅ |
| 5 | SUBJECT DISPOSITION | ✅ |
| 6 | DEMOGRAPHICS AND OTHER BASELINE CHARACTERISTICS | ✅ |
| 7 | EXTENT OF EXPOSURE AND TREATMENT COMPLIANCE | ✅ |
| 7.1–7.2 | Investigational Product / Treatment Compliance | ✅ |
| 8 | MEDICAL HISTORY AND MEDICATION | ✅ |
| 8.1–8.2 | Medical History / Prior & Concomitant Medication | ✅ |
| 9 | EFFICACY ANALYSIS | 🔶 고난이도 |
| 9.1 | Primary Efficacy Parameter(s) | 🔶 통계 모델 포함 |
| 9.2 | Secondary Efficacy Parameter(s) | 🔶 |
| 9.3 | Additional Efficacy parameter(s) | 🔶 |
| 10 | SAFETY ANALYSIS | ✅ (표준 문구) |
| 10.1–10.6 | AE / Lab / Vital / ECG / PE / Other | ✅ |
| 11 | INTERIM ANALYSIS | ✅ |
| *(추가)* | DMC ANALYSIS | ✅ |
| 12 | DETERMINATION OF SAMPLE SIZE | 🔶 수치 추출 |
| 13 | STATISTICAL SOFTWARE | ✅ (거의 고정) |
| *(추가)* | STATISTICAL CONSIDERATIONS | 🔶 |
| 14 | DATA HANDLING CONVENTIONS | ✅ (거의 표준) |
| 14.1–14.8 | Visit Windows / Derived Variables / Missing Data 등 | ✅ |
| 15 | CHANGES TO ANALYSIS SPECIFIED IN PROTOCOL | 🔶 |
| 16 | REFERENCES | 🔶 |
| 17 | APPENDIX | 🔶 |

> **범례**: ✅ 자동화 용이 (행정·표준 문구) | 🔶 반자동 (통계 추론·수치 추출) | ⛔ 자동화 불가 (서명·날짜)

---

## 3. 오픈소스 구조 및 확장 포인트

### 핵심 아키텍처
```
프로토콜 PDF
    ↓  Protocol 클래스 → 텍스트 추출
시스템 메시지 + 섹션별 프롬프트 목록
    ↓  LLM API 비동기 호출 × N섹션
{tag: 내용} 딕셔너리
    ↓  DocxTemplate.render()
유한 SAP 양식.docx  ✅
```

### 우리가 새로 만들 파일 (3개)

```
sap-kcl/
├── auto_sap/
│   ├── prompts/
│   │   └── prompts_yuhan_v1.py            ← 신규: 유한 SAP 항목별 프롬프트
│   ├── generate_templates/
│   │   └── generate_yuhan_template.py      ← 신규: 유한 템플릿 조립
│   └── templates/
│       └── yuhan_sap_template_v1.0.docx    ← 신규: 태그 삽입된 유한 양식
└── WriteSAPs/
    └── yuhan_sap.py                        ← 신규: 실행 예시
```

---

## 4. 유한 SAP 태그 설계 (전체 목록)

### 커버 / 행정 정보

| 태그명 | 섹션 | 설명 |
|---|---|---|
| `study_number` | Cover | YH####-### 형식 |
| `study_title_line1` | Cover | 시험 제목 1줄 |
| `study_title_line2` | Cover | (2줄인 경우) |
| `sap_version` | Cover | Ver.01, Ver.02 등 |
| `effective_date` | Cover | YYYY-MM-DD |

### 섹션별 본문

| 태그명 | 섹션 | KCL 대응 | 난이도 |
|---|---|---|---|
| `introduction` | 2. Introduction | `description_of_trial` | 중 |
| `objectives` | 3. Objectives | `primary_objectives` + `secondary_objectives` | 하 |
| `screened_set` | 4.1 | — (표준 문구) | 하 |
| `randomized_set` | 4.2 | — | 하 |
| `safety_set` | 4.3 | — | 하 |
| `fas_definition` | 4.4 FAS | — | 하 |
| `pps_definition` | 4.5 PPS | — | 하 |
| `subject_disposition` | 5 | — | 하 |
| `demographics` | 6 | — | 하 |
| `ip_exposure` | 7.1 | `adherence_to_treatment` | 하 |
| `treatment_compliance` | 7.2 | `adherence_to_treatment` | 하 |
| `medical_history` | 8.1 | — | 하 |
| `concomitant_medication` | 8.2 | `descriptive_concomitant_medications` | 하 |
| `primary_efficacy` | 9.1 | `primary_analysis_model` + `primary_estimand` | **고** |
| `secondary_efficacy` | 9.2 | `secondary_analysis` | **고** |
| `additional_efficacy` | 9.3 | — | **고** |
| `adverse_events` | 10.1 | `adverse_events` | 하 |
| `lab_parameters` | 10.2 | — | 하 |
| `vital_signs` | 10.3 | — | 하 |
| `ecg` | 10.4 | — | 하 |
| `physical_exam` | 10.5 | — | 하 |
| `other_safety` | 10.6 | — | 하 |
| `interim_analysis` | 11 | `interim_analysis` | 하 |
| `dmc_analysis` | DMC | — | 하 |
| `sample_size` | 12 | `sample_size` | 중 |
| `statistical_software` | 13 | — (거의 고정) | 하 |
| `statistical_considerations` | — | `multiple_comparisons` 등 | 중 |
| `visit_windows` | 14.1 | `visit_windows` | 중 |
| `derived_variables` | 14.2 | — | 중 |
| `repeated_assessments` | 14.3 | — | 하 |
| `missing_last_dose_date` | 14.4 | — | 하 |
| `missing_ae_severity` | 14.5 | — | 하 |
| `missing_causality` | 14.6 | — | 하 |
| `missing_dates` | 14.7 | `missing_data_sensitivity_analysis` | 하 |
| `lab_char_values` | 14.8 | — | 하 |
| `protocol_changes` | 15 | — | 중 |

---

## 5. 개발 계획

### Phase 0 — 준비 (1–2주)

| 작업 | 담당 | 비고 |
|---|---|---|
| 오픈소스 로컬 설치 및 데모 실행 | 개발자 | Python venv + requirements.txt |
| ✅ 유한 SAP 양식 확보 | 통계팀 | 완료 (`SBS02T01_Ver02` 기준) |
| 기존 SAP 예시 3–5건 수집 | 통계팀 | 검증용 정답 데이터 |
| LLM API 키 확보 | IT/구매 | Anthropic Claude 또는 OpenAI |

---

### Phase 1 — 유한 SAP 템플릿 태깅 (2–3주)

**목표**: 유한 SAP Word 양식에 Jinja2 `{{ tag }}` 삽입

#### 작업 순서
1. `SBS02T01_Ver02` 파일 복사 → `yuhan_sap_template_v1.0.docx`
2. 각 섹션 본문 위치에 `{{ tag_name }}` 태그 삽입
3. 고정 표준 문구는 그대로 유지 (불필요한 태그화 금지)
4. Instruction 셀(회색 지시문)은 완성 버전에서 삭제
5. 서명란 등 자동화 불가 영역은 빈칸 유지

#### 태그 삽입 규칙
```
[Before] The primary efficacy parameter will be the change from baseline in MSSBP...
[After]  {{ primary_efficacy }}
```

#### 결과물
- `yuhan_sap_template_v1.0.docx` — Jinja2 태그 삽입 완료
- `yuhan_tag_mapping.xlsx` — 태그명 ↔ 섹션 대응표

---

### Phase 2 — 유한 전용 프롬프트 설계 (2–3주)

**목표**: 유한 SAP 각 항목에 맞는 LLM 프롬프트 작성

#### 시스템 메시지 (기본 골격)
```python
def system_message(protocol_text):
    return f"""You are an expert statistician specializing in clinical trials.
    You are given a clinical trial protocol and will write sections for a 
    Statistical Analysis Plan (SAP) following Yuhan Corporation's SAP template format.
    
    Guidelines:
    - Write in English
    - Be concise; use bullet points only where the section inherently requires a list
    - Do not invent information not present in the protocol
    - Follow ICH E9(R1) estimand framework where applicable
    
    The protocol is:
    {protocol_text}
    """
```

#### 프롬프트 작성 원칙
- 단순 추출 항목 → `reasoning_effort: "minimal"`
- 통계 설계 항목 → `reasoning_effort: "high"`
- KCL 기존 프롬프트 최대한 재활용, 유한 고유 항목만 신규 작성

---

### Phase 3 — 코드 개발 (1–2주)

**목표**: `generate_yuhan_template.py` + `yuhan_sap.py` 개발

#### `generate_yuhan_template.py` 핵심 구조
```python
from auto_sap.classes.template_class import Template
from auto_sap.classes.prompt_register_class import PromptRegister
from auto_sap.prompts import prompts_yuhan_v1 as prompts_file
from importlib.resources import files

prompt_tasks = [
    # 커버/행정
    PromptRegister("study_number",    "minimal", "low"),
    PromptRegister("study_title_line1","low",     "low"),
    PromptRegister("sap_version",     "minimal", "low"),
    # 본문
    PromptRegister("introduction",    "medium",  "low"),
    PromptRegister("objectives",      "low",     "low"),
    PromptRegister("fas_definition",  "low",     "low"),
    PromptRegister("pps_definition",  "low",     "low"),
    PromptRegister("primary_efficacy","high",    "low"),   # 통계 모델 포함
    PromptRegister("secondary_efficacy","high",  "low"),
    PromptRegister("sample_size",     "medium",  "low"),
    PromptRegister("interim_analysis","low",     "low"),
    PromptRegister("visit_windows",   "medium",  "low"),
    # ... (전체 태그 목록)
]

yuhan_template_v1 = Template(
    template_path=files("auto_sap").joinpath(
        "templates/yuhan_sap_template_v1.0.docx"),
    system_message_function=prompts_file.system_message,
    prompt_register=prompt_tasks,
    prompts_dictionary=prompts_file.PROMPTS_DICTIONARY,
    template_name="yuhan_sap_template_v1.0.docx",
    prompts_name="yuhan_v1"
)
```

#### 실행 스크립트 (`yuhan_sap.py`)
```python
from auto_sap.generate_templates.generate_yuhan_template import yuhan_template_v1

yuhan_template_v1.write_sap(
    protocol_path="Protocols/YOUR_PROTOCOL.pdf",
    sap_folder_path="SAPs",
    sap_name="YOUR_STUDY_SAP_draft"
)
```

---

### Phase 4 — 검증 및 개선 (2–3주)

**목표**: 실제 프로토콜 3건으로 생성 품질 검증

#### 검증 방법
1. 기존 완성 SAP 3건 선택 (정답 데이터)
2. 해당 프로토콜 입력 → 자동 생성 SAP 초안 출력
3. 통계팀 담당자가 항목별 채점 (0–3점 척도, SAPAI 논문 방식 동일)
4. 항목별 정확도 집계 → 낮은 항목 프롬프트 개선

#### 성공 기준 (1차 목표)
- 행정·설계 항목 정확도: **≥ 75%**
- 통계 분석 항목 정확도: **≥ 60%**
- 통계팀 체감 평가: "수정 후 사용 가능" **≥ 70%**

---

## 6. 타임라인

```
Week 1–2   Phase 0  환경 설정 + 검증 데이터 수집
Week 3–5   Phase 1  유한 SAP 템플릿 태깅
Week 6–8   Phase 2  프롬프트 설계
Week 9–10  Phase 3  코드 개발
Week 11–13 Phase 4  검증 및 개선
Week 14    →         v1.0 내부 배포
```

---

## 7. 기술 스택

| 항목 | 내용 |
|---|---|
| 언어 | Python 3.11+ |
| 핵심 라이브러리 | `docxtpl`, `openai` or `anthropic`, `pypdf` |
| LLM 후보 | Anthropic Claude Sonnet 4 / OpenAI GPT-5 |
| 템플릿 포맷 | DOCX (Jinja2 태그 방식) |
| 실행 환경 | Python 가상환경 (venv) |
| 소스 관리 | GitHub (private fork) |

---

## 8. 고려 사항 및 리스크

### 🔒 데이터 보안 (최우선)
- 프로토콜은 기밀 문서 → LLM API 전송 전 **개인정보·영업비밀 마스킹** 검토 필요
- **Azure OpenAI** 또는 **AWS Bedrock (Anthropic Claude)** 사용 시 데이터 보호 계약 가능
- 온프레미스 모델(Ollama + 오픈소스 LLM) 대안도 검토

### 🧑‍⚕️ Human-in-the-Loop 필수
- 논문 결과: 통계 분석 설계 항목은 자동 생성 정확도 67–72% 수준
- 포지션: **"SAP 초안 작성 보조 도구"** — 최종 SAP 자동 완성 ❌
- 특히 Primary Efficacy (9.1), MMRM/ANCOVA 모델 설정은 반드시 통계사가 검토·수정

### 📄 SAP 양식 버전 관리
- 유한 SAP 양식 변경 시 태그 재작업 필요
- 양식-버전 간 태그 대응표 관리 체계 필요

### 💰 LLM 비용 추정
- 프로토콜 1건 처리 기준 약 $1–5 예상 (모델·섹션 수에 따라 상이)
- 배치 처리 최적화로 비용 절감 가능

---

## 9. 참고 자료

- 오픈소스: https://github.com/rct-sap-ai/sap-kcl
- 논문: https://www.medrxiv.org/content/10.64898/2026.03.19.26348626v2
- `docxtpl` 문서: https://docxtpl.readthedocs.io
- ICH E9(R1) Addendum on Estimands

---

*작성일: 2026-04-01 | 작성: AKiN | 기준 양식: SBS02T01_Ver02_SAP_20251212.docx*
