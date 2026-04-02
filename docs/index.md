# YH-SAP

**임상시험 프로토콜 → Statistical Analysis Plan (SAP) 초안 자동생성 파이프라인**

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

## 검증 결과

5회 반복 실행, 9개 검증 기준 — **45/45 ALL PASS**

| Run | 시간 | Paragraphs | Tables | DOCX | SKIP 마커 |
|-----|------|-----------|--------|------|----------|
| 1 | 84s | 359 | 19 | 384KB | 21 |
| 2 | 69s | 348 | 19 | 385KB | 25 |
| 3 | 79s | 334 | 19 | 384KB | 21 |
| 4 | 86s | 381 | 19 | 385KB | 22 |
| 5 | 78s | 385 | 19 | 386KB | 28 |

상세 보고서: [검증 보고서](validation-report.md)

## 빠른 시작

```bash
git clone https://github.com/minpark0427/YH-SAP.git
cd YH-SAP
python3 -m venv YH-SAP-venv && source YH-SAP-venv/bin/activate
pip install -r sap-kcl/requirements.txt
pip install python-docx docxtpl PyPDF2 anthropic python-dotenv

cd sap-kcl
python -m WriteSAPs.yuhan_sap_json ../프로토콜.docx --test
```

자세한 설치 방법은 [설치 가이드](getting-started.md)를 참고하세요.
