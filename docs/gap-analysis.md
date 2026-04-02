# GAP Analysis: 계획서 vs SAP 양식 vs 현재 구현

> 도입 계획서, 유한 SAP 양식(SBS02T01), 사람 작성 SAP(YH00000-101), 현재 코드 간 매핑 완전성 분석

---

## 1. 현재 상태: 3방향 일관성

| 구성요소 | 항목 수 | 일치 |
|---------|--------|------|
| PROMPTS_DICTIONARY | 36 | ✅ |
| PromptRegister | 36 | ✅ |
| SECTION_MAPPING | 36 | ✅ |
| docx 템플릿 태그 | 36 | ✅ |

**36개 태그 간 완전 일치** — prompts, register, mapping, template 모두 동기화됨.

---

## 2. 발견된 GAP

### GAP 1: 커버/행정 태그 미구현 (계획서에만 있음)

계획서 섹션 4에 명시되었으나 현재 미구현:

| 태그 | 설명 | 우선순위 |
|------|------|---------|
| `study_number` | YH####-### 형식 | Low (프로토콜에서 추출 용이) |
| `study_title_line1/2` | 시험 제목 | Low |
| `sap_version` | Ver.01 등 | Low (고정값) |
| `effective_date` | YYYY-MM-DD | Low (고정값) |

**판단**: 프로토콜에서 단순 추출하는 항목이므로 구현 난이도 낮음. 하지만 JSON 렌더러(B안)에서는 커버 페이지를 직접 조작해야 하므로 별도 처리 필요.

### GAP 2: PK/PD 분석 섹션 미스매치 (CRITICAL)

**현재**: `primary_efficacy`, `secondary_efficacy`, `additional_efficacy` 태그가 "유효성 분석" 관점으로 프롬프트 설계됨.

**사람 작성 SAP**: Phase 1 시험이므로 유효성 분석이 없고, 대신:
- 4.15 Pharmacokinetics Analyses (PK 분석)
- 4.16 Pharmacodynamic Analyses (PD 분석)
- 4.17 Exploratory Analyses
- 4.19 Preliminary PK Analyses
- 4.20 Preliminary PD Analyses

**문제**: 프롬프트가 "Primary Efficacy Parameter" 작성을 요청하는데, Phase 1에는 efficacy가 없음. LLM이 "Not applicable"로 응답하거나, PK/PD를 efficacy로 잘못 분류할 수 있음.

**권장 조치**:
1. `primary_efficacy` 프롬프트를 "Primary Analysis Parameter (Efficacy or PK/PD)"로 일반화
2. 또는 `pk_analysis`, `pd_analysis` 태그를 별도 추가하고, Phase에 따라 동적으로 선택
3. 프롬프트에 "If this is a Phase 1 study with no efficacy endpoints, describe the primary PK/PD analysis instead" 조건문 추가

### GAP 3: Phase 1 특화 섹션 누락

사람 작성 SAP에는 있지만 현재 태그 없음:

| 섹션 | 설명 | 우선순위 |
|------|------|---------|
| 4.4 Protocol Deviation | 프로토콜 위반 처리 | Medium |
| 4.6-4.9 Special Tests | 약물검사, 간염, 매독, HIV 등 | Low (Phase 1 특화) |
| 4.13 Definition of Baseline | 베이스라인 정의 규칙 | Medium |
| 4.18 Subgroup Analysis | 하위그룹 분석 | Medium |
| 4.19-4.20 Preliminary PK/PD | 중간 PK/PD 분석 | Medium (Phase 1 필수) |
| 4.21 Blinded Analyses | 눈가림 유지 분석 | Low |

### GAP 4: 미구현 표준 섹션

| 섹션 | 설명 | 우선순위 |
|------|------|---------|
| 1. LIST OF ABBREVIATIONS | 약어 목록 자동 생성 | Low (반자동 가능) |
| 3. SYNOPSIS | 프로토콜 요약 | Medium (introduction과 겹침) |
| 16. REFERENCES | 참고문헌 | Low |
| 17. APPENDIX | 부록 | Low |

### GAP 5: 태그명 불일치

| 계획서 태그명 | 현재 구현 태그명 | 차이 |
|-------------|---------------|------|
| `statistical_software` | `statistical_software_version` | 계획서보다 구체적 (OK) |

이것은 의도적 변경이므로 문제 없음.

---

## 3. 우선순위별 개선 권장 사항

### 즉시 (High Priority)

1. **PK/PD 프롬프트 일반화** — `primary_efficacy` 프롬프트에 Phase 1 조건 추가
   ```
   "If this is a Phase 1 study without formal efficacy endpoints, 
    describe the primary pharmacokinetic (PK) and/or pharmacodynamic (PD) 
    analysis plan instead."
   ```

2. **Protocol Deviation 태그 추가** — 사람 SAP에서 별도 섹션으로 존재

3. **Baseline Definition 태그 추가** — 분석의 기준점 정의는 SAP 핵심 항목

### 중기 (Medium Priority)

4. Preliminary PK/PD 태그 추가 (Phase 1 특화)
5. Subgroup Analysis 태그 추가
6. Synopsis 섹션 (introduction과 통합 또는 별도)
7. 커버 페이지 태그 구현 (study_number 등)

### 장기 (Low Priority)

8. Special Tests (4.6-4.9) — 프로토콜별 동적 생성
9. Blinded Analyses
10. LIST OF ABBREVIATIONS 자동 생성
11. REFERENCES / APPENDIX

---

## 4. 결론

**현재 36개 태그는 내부적으로 완전 일치**하지만, 사람이 실제로 작성한 SAP와 비교하면 **PK/PD 분석 섹션 대응 미흡**과 **Phase 1 특화 섹션 10개 누락**이 주요 GAP입니다. 특히 PK/PD 미스매치는 Phase 1 프로토콜에서 생성 품질에 직접 영향을 미치므로 최우선 개선이 필요합니다.
