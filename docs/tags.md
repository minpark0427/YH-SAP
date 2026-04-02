# SAP 섹션 (46개 태그)

| # | 섹션 | 태그 | 복잡도 |
|---|------|------|--------|
| 1 | Abbreviations | `abbreviations` | Low |
| 2 | Introduction | `introduction` | Medium |
| 3 | Objectives | `objectives` | Low |
| — | General Considerations | `general_considerations` | Medium |
| 4.1 | Screened Set | `screened_set` | Minimal |
| 4.2 | Randomized Set | `randomized_set` | Minimal |
| 4.3 | Safety Set | `safety_set` | Minimal |
| 4.4 | Full Analysis Set | `fas_definition` | Minimal |
| 4.5 | Per-Protocol Set | `pps_definition` | Low |
| 5 | Subject Disposition | `subject_disposition` | Low |
| 6 | Demographics | `demographics` | Low |
| 7.1 | IP Exposure | `ip_exposure` | Low |
| 7.2 | Treatment Compliance | `treatment_compliance` | Low |
| 8.1 | Medical History | `medical_history` | Minimal |
| 8.2 | Concomitant Medication | `concomitant_medication` | Low |
| — | Special Screening Tests | `special_tests` | Low |
| 9.1 | Primary Analysis (Efficacy/PK) | `primary_efficacy` | **High** |
| 9.2 | Secondary Analysis (Efficacy/PD) | `secondary_efficacy` | **High** |
| 9.3 | Additional/Exploratory | `additional_efficacy` | Medium |
| — | Preliminary PK Analyses | `preliminary_pk` | Medium |
| — | Preliminary PD Analyses | `preliminary_pd` | Medium |
| — | Blinded Analyses | `blinded_analyses` | Low |
| 10.1 | Adverse Events | `adverse_events` | Medium |
| 10.2 | Lab Parameters | `lab_parameters` | Low |
| 10.3 | Vital Signs | `vital_signs` | Low |
| 10.4 | ECG | `ecg` | Low |
| 10.5 | Physical Exam | `physical_exam` | Minimal |
| 10.6 | Other Safety | `other_safety` | Minimal |
| 11 | Interim Analysis | `interim_analysis` | Low |
| — | DMC Analysis | `dmc_analysis` | Minimal |
| 12 | Sample Size | `sample_size` | **High** |
| 13 | Statistical Software | `statistical_software_version` | Minimal |
| — | Statistical Considerations | `statistical_considerations` | Medium |
| 14.1 | Visit Windows | `visit_windows` | Medium |
| 14.2 | Derived Variables | `derived_variables` | Medium |
| 14.3 | Repeated Assessments | `repeated_assessments` | Low |
| 14.4 | Missing Last Dose Date | `missing_last_dose_date` | Low |
| 14.5 | Missing AE Severity | `missing_ae_severity` | Minimal |
| 14.6 | Missing Causality | `missing_causality` | Minimal |
| 14.7 | Missing Dates | `missing_dates` | Medium |
| 14.8 | Lab Character Values | `lab_char_values` | Low |
| — | Protocol Deviation | `protocol_deviation` | Low |
| — | Baseline Definition | `baseline_definition` | Low |
| — | Subgroup Analysis | `subgroup_analysis` | Low |
| — | References | `references` | Low |
| 15 | Protocol Changes | `protocol_changes` | Low |

## 복잡도 설명

| 복잡도 | reasoning_effort | 설명 |
|--------|-----------------|------|
| **Minimal** | minimal | 단순 추출, 표준 문구 |
| **Low** | low | 기본적인 요약·정리 |
| **Medium** | medium | 중간 수준의 통계적 판단 |
| **High** | high | 통계 모델 설계, 2단계 생성 적용 |

## High 복잡도 섹션

다음 3개 섹션은 `MultiStepGenerator`를 통해 2단계로 생성됩니다:

1. **primary_efficacy** — 근거 추출 (PK parameters, analysis model) → SAP 작성
2. **secondary_efficacy** — 근거 추출 (PD markers, food effect) → SAP 작성
3. **sample_size** — 근거 추출 (assumptions, power, alpha) → SAP 작성
