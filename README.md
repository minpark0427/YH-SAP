# YH-SAP

Clinical trial protocol → Statistical Analysis Plan (SAP) 초안 자동생성 파이프라인

> KCL(King's College London) 오픈소스 [sap-kcl](https://github.com/rct-sap-ai/sap-kcl)를 기반으로, 유한양행 SAP 양식에 맞는 초안을 자동생성합니다.

---

## 주요 기능

- 프로토콜(PDF/DOCX) 입력 → 36개 SAP 섹션 자동생성 → DOCX 출력
- **Targeted-Context Generation** — 프로토콜을 섹션 단위로 분할하여 각 SAP 태그에 관련 섹션만 선택적 주입 (89% 컨텍스트 축소)
- **JSON 구조화 출력** — LLM이 JSON으로 응답하여 python-docx가 paragraph 단위로 서식 적용
- **Multi-Step Generation** — 고복잡도 섹션(primary efficacy, sample size 등)은 근거 추출 → 생성 2단계
- **3개 LLM 백엔드** — Claude CLI (구독 인증), Anthropic API, OpenAI API

## 아키텍처

```
Protocol (PDF/DOCX)
    │
    ▼
ProtocolSegmenter ─── heading 기반 126개 섹션 분할
    │
    ▼
ContextAssembler ──── SAP 태그별 관련 섹션 조립 (SECTION_MAPPING)
    │                  + 공통 컨텍스트 (Protocol Synopsis)
    ▼
LLM (Claude Opus / Sonnet / Haiku)
    │  ┌─ 일반 섹션: 1단계 생성
    │  └─ 고복잡도 섹션: MultiStepGenerator (추출 → 생성)
    ▼
JsonSapRenderer ──── JSON → python-docx paragraph 단위 렌더링
    │
    ▼
SAP.docx
```

## 빠른 시작

### 1. 환경 설정

```bash
# Python 3.11+ 필요
python -m venv YH-SAP-venv
source YH-SAP-venv/bin/activate
pip install -r sap-kcl/requirements.txt
pip install python-docx docxtpl PyPDF2 anthropic
```

### 2. Claude CLI 설치 (권장 백엔드)

```bash
# Claude CLI가 설치되어 있고 구독 인증이 완료된 상태여야 합니다
claude --version
```

### 3. 사전 준비 파일

프로젝트 루트에 다음 파일이 필요합니다 (gitignore에 의해 repo에 포함되지 않음):

| 파일 | 설명 | 필수 |
|------|------|------|
| `SBS02T01 Ver02_*.docx` | 유한 SAP 양식 원본 (템플릿 재생성 시) | 선택 |
| Protocol DOCX/PDF | 분석 대상 프로토콜 | 필수 |

> `sap-kcl/auto_sap/templates/yuhan_sap_template_v1.0.docx` (Jinja2 태그 템플릿)는 repo에 포함되어 있습니다.

### 4. SAP 생성

```bash
cd sap-kcl

# B안: JSON 구조화 출력 (권장)
python -m WriteSAPs.yuhan_sap_json <protocol.docx> --model claude-opus-4-6

# 테스트 모드 (haiku, 빠름)
python -m WriteSAPs.yuhan_sap_json <protocol.docx> --test

# A안: docxtpl 방식 (레거시)
python -m WriteSAPs.yuhan_sap <protocol.docx>
python -m WriteSAPs.yuhan_sap <protocol.docx> --test
```

### 5. 출력 확인

```
SAPs_v4_json/
├── YH_SAP_<protocol_name>.docx         ← SAP 문서
└── YH_SAP_<protocol_name>_content.txt  ← 원문 텍스트 (디버깅용)
```

## 프로젝트 구조

```
YH-SAP/
├── README.md
├── CLAUDE.md                               ← Claude Code 가이드
├── docs/
│   └── architecture-evolution.md           ← Phase 0-3 발전 과정
├── scripts/
│   ├── create_yuhan_template.py            ← 양식에서 Jinja2 템플릿 생성
│   └── validate_sap.py                     ← LLM 기반 품질 검증 스크립트
│
└── sap-kcl/                                ← 핵심 파이프라인
    ├── auto_sap/
    │   ├── classes/
    │   │   ├── protocol_classes.py         ← Protocol 로더 (PDF/DOCX/TXT)
    │   │   ├── protocol_segmenter.py       ← 프로토콜 heading 기반 섹셔닝
    │   │   ├── context_assembler.py        ← 태그별 targeted context 조립
    │   │   ├── multi_step_generator.py     ← 고복잡도 2단계 생성
    │   │   ├── json_renderer.py            ← JSON → docx 렌더러 (B안)
    │   │   ├── template_class.py           ← docxtpl 렌더러 (A안, 레거시)
    │   │   └── chat_classes.py             ← LLM 백엔드 (Claude/Anthropic/OpenAI)
    │   ├── prompts/
    │   │   └── prompts_yuhan_v1.py         ← 36개 SAP 섹션 프롬프트
    │   ├── section_mapping.py              ← SAP 태그 → 프로토콜 섹션 매핑
    │   ├── generate_templates/
    │   │   └── generate_yuhan_template.py  ← PromptRegister 정의
    │   └── templates/
    │       └── yuhan_sap_template_v1.0.docx
    │
    └── WriteSAPs/
        ├── yuhan_sap_json.py               ← B안 러너 (JSON + python-docx)
        └── yuhan_sap.py                    ← A안 러너 (docxtpl, 레거시)
```

## SAP 섹션 (36개 태그)

| 섹션 | 태그 | 복잡도 |
|------|------|--------|
| 2. Introduction | `introduction` | Medium |
| 3. Objectives | `objectives` | Low |
| 4.1-4.5 Analysis Sets | `screened_set`, `randomized_set`, `safety_set`, `fas_definition`, `pps_definition` | Minimal-Low |
| 5. Subject Disposition | `subject_disposition` | Low |
| 6. Demographics | `demographics` | Low |
| 7.1-7.2 Exposure/Compliance | `ip_exposure`, `treatment_compliance` | Low |
| 8.1-8.2 Medical History/Meds | `medical_history`, `concomitant_medication` | Low |
| 9.1-9.3 Efficacy | `primary_efficacy`, `secondary_efficacy`, `additional_efficacy` | **High** |
| 10.1-10.6 Safety | `adverse_events`, `lab_parameters`, `vital_signs`, `ecg`, `physical_exam`, `other_safety` | Low-Medium |
| 11. Interim Analysis | `interim_analysis` | Low |
| 12. Sample Size | `sample_size` | **High** |
| 13. Software | `statistical_software_version` | Minimal |
| 14.1-14.8 Data Handling | `visit_windows`, `derived_variables`, `missing_*` 등 | Low-Medium |
| 15. Protocol Changes | `protocol_changes` | Low |

## 검증

```bash
# LLM 기반 품질 검증 (사람이 쓴 SAP + 체크리스트 대비)
python scripts/validate_sap.py
```

체크리스트 기준 8개 카테고리(22개 질문)에 대해 AI SAP를 평가합니다.

## 참고

- **원본 오픈소스**: [rct-sap-ai/sap-kcl](https://github.com/rct-sap-ai/sap-kcl)
- **논문**: Jafari et al. (2026), *"From Protocol to Analysis Plan: Development and Validation of a Large Language Model Pipeline for Statistical Analysis Plan Generation using Artificial Intelligence (SAPAI)"*
- **발전 과정**: [`docs/architecture-evolution.md`](docs/architecture-evolution.md)

## 라이선스

이 프로젝트는 sap-kcl 오픈소스를 기반으로 하며, 유한양행 내부 사용을 위해 개발되었습니다.
