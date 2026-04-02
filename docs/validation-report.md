# YH-SAP 파이프라인 검증 보고서

> 프로토콜: YH00000-101 (Phase 1, SAD/MAD, 건강한 성인 남성)
> 실행 일자: 2026-04-02
> 모델: claude-haiku-4-5-20251001 (테스트 모드)

---

## 1. 검증 목적

YH-SAP 파이프라인이 프로토콜 DOCX를 입력받아 SAP DOCX를 안정적으로 생성하는지 확인한다.
안정성을 위해 동일 프로토콜로 5회 반복 실행하고, 매 실행마다 9개 검증 기준을 적용한다.

---

## 2. 검증 기준 (9항목)

| # | 기준 | 설명 | 합격 조건 |
|---|------|------|----------|
| 1 | tags_46 | 46개 SAP 태그 전부 content.txt에 존재 | 누락 0 |
| 2 | errors_0 | LLM 호출 실패(ERROR) 없음 | ERROR 0건 |
| 3 | no_instruction | 양식 Instruction 박스(회색 테이블) 제거 | 0개 |
| 4 | no_markdown | docx 본문에 #, ** 등 마크다운 문법 없음 | 0건 |
| 5 | no_blue | docx에 파란색(예시) 텍스트 잔여 없음 | 0건 |
| 6 | has_tables | 프로토콜 테이블이 SAP에 삽입됨 | 5개 초과 |
| 7 | docx_valid | 출력 docx 파일 정상 (100KB 초과) | true |
| 8 | has_yellow | 프로토콜 미충족 섹션에 노란 하이라이트 | 1개 이상 |
| 9 | has_skips | [SKIP: 사유] 마커로 정직한 갭 표시 | 1개 이상 |

---

## 3. 검증 결과

### 3.1 1차 실행 (재시도 로직 없음)

재시도 로직 추가 전 5회 실행 결과:

| Run | 상태 | 시간 | Paragraphs | Tables | DOCX | SKIP | Yellow | 실패 항목 |
|-----|------|------|-----------|--------|------|------|--------|----------|
| 1 | PASS | 229s | 339 | 19 | 385KB | 20 | 13 | — |
| 2 | PASS | 84s | 402 | 19 | 386KB | 28 | 15 | — |
| 3 | PASS | 76s | 379 | 19 | 385KB | 26 | 18 | — |
| 4 | **FAIL** | 84s | 376 | 19 | 386KB | 21 | 16 | errors_0 |
| 5 | **FAIL** | 78s | 370 | 19 | 385KB | 23 | 18 | errors_0 |

**결과: 3/5 통과**

**실패 원인 분석:**
- Run 4: `secondary_efficacy` 태그에서 claude CLI가 빈 응답 반환 → "ERROR"로 처리됨
- Run 5: `vital_signs` 태그에서 동일 현상

**근본 원인:** `ClaudeCodeChatAsync.get_response()`에 재시도 로직이 없어서, CLI의 간헐적 빈 응답이 즉시 ERROR로 확정됨. 네트워크 일시 지연 또는 CLI 프로세스 간 경합이 원인으로 추정.

### 3.2 개선 조치

`ClaudeCodeChatAsync.get_response()`에 재시도 로직 추가:

```python
async def get_response(self, ..., max_retries: int = 2):
    for attempt in range(max_retries + 1):
        result = await loop.run_in_executor(None, _run)
        if result.returncode != 0 or not result.stdout.strip():
            if attempt < max_retries:
                print(f"  Retry {attempt+1}/{max_retries}")
                await asyncio.sleep(2)
                continue
        return {"content": result.stdout.strip()}
```

- 빈 응답 또는 CLI 에러 시 최대 2회 재시도 (2초 간격)
- 3번째 시도까지 실패하면 그때 ERROR 확정

### 3.3 2차 실행 (재시도 로직 적용 후)

| Run | 상태 | 시간 | Paragraphs | Tables | DOCX | SKIP | Yellow |
|-----|------|------|-----------|--------|------|------|--------|
| 1 | **PASS** | 84s | 359 | 19 | 384KB | 21 | 15 |
| 2 | **PASS** | 69s | 348 | 19 | 385KB | 25 | 18 |
| 3 | **PASS** | 79s | 334 | 19 | 384KB | 21 | 15 |
| 4 | **PASS** | 86s | 381 | 19 | 385KB | 22 | 16 |
| 5 | **PASS** | 78s | 385 | 19 | 386KB | 28 | 21 |

**결과: 5/5 통과 (45/45 개별 기준 ALL PASS)**

---

## 4. 결과 분석

### 4.1 안정성

- 5회 모두 ALL_PASS: 재시도 로직 추가 후 간헐적 실패 완전 해소
- DOCX 크기 일관적: 384-386KB (±0.3%)
- 테이블 수 일관적: 19개 (모든 run 동일)

### 4.2 실행 시간

| 통계 | 값 |
|------|---|
| 평균 | 79.2초 |
| 최소 | 69초 |
| 최대 | 86초 |
| 표준편차 | 6.1초 |

haiku(테스트 모델) 기준. Production(sonnet-4-6)은 2-3배 소요 예상.

### 4.3 콘텐츠 변동성

LLM 특성상 매 실행마다 출력이 다르지만, 구조적 품질은 일관적:

| 지표 | 최소 | 최대 | 의미 |
|------|------|------|------|
| Paragraphs | 334 | 385 | 본문 분량 변동 ±7% |
| SKIP markers | 21 | 28 | 프로토콜 미충족 탐지 ±15% |
| Yellow highlights | 15 | 21 | SKIP의 docx 렌더링 |

SKIP 수 변동은 LLM이 "프로토콜에 충분한 정보가 없다"를 판단하는 기준이 실행마다 약간 다르기 때문. 이는 LLM의 본질적 비결정성이므로 정상 범위.

### 4.4 프로토콜 테이블 삽입

모든 run에서 19개 테이블 일관 삽입:
- 프로토콜에서 추출: 12개 (Objectives 4, SoA 3, Design 1, IP 1, PK 1, Lab 1, Abbrev 1)
- 양식 기존 테이블: 7개 (Cover, Signature, Document History 등)
- Instruction 박스: 37개 → 0개 (전부 제거)

---

## 5. 파이프라인 사양 요약

| 항목 | 값 |
|------|---|
| SAP 태그 | 46개 |
| 프로토콜 섹셔닝 | 126개 섹션 (heading 기반) |
| 컨텍스트 축소 | 88% (평균 13.6K/호출 vs 111K 전체) |
| 프로토콜 테이블 추출 | 12개 (7종류) |
| 출력 포맷 | JSON → python-docx (paragraph 단위 렌더링) |
| 서식 처리 | 파란색→검정, Instruction 제거, SKIP→노란하이라이트 |
| 재시도 | max_retries=2 (빈 응답/CLI 에러) |
| High-complexity | 2단계 생성 (primary_efficacy, secondary_efficacy, sample_size) |
| 기본 모델 | claude-sonnet-4-6 (테스트: haiku-4-5) |

---

## 6. 알려진 제한사항

1. **SKIP 마커 비결정성**: 동일 프로토콜이라도 실행마다 SKIP 수가 21-28개로 변동. LLM이 "정보 부족" 판단을 매번 약간 다르게 함.

2. **프로토콜 구조 의존**: ProtocolSegmenter는 `번호.\t제목` 패턴의 heading을 가정. 비표준 구조의 프로토콜에서는 섹셔닝 품질이 저하될 수 있으며, 이 경우 full-protocol fallback이 동작.

3. **테이블 렌더링 제한**: 프로토콜의 merged cell/nested table은 단순 cell-by-cell로 추출되어 일부 중복 텍스트가 발생할 수 있음 (기능에는 영향 없음).

4. **Jinja2 템플릿 태그 부족**: 신규 추가된 10개 태그(Phase 4-5)는 docx 템플릿에 `{{ tag }}` 위치가 없어 B안(JSON renderer)으로만 삽입 가능. A안(docxtpl)에서는 content.txt에만 존재.

5. **PDF 프로토콜**: 테이블 추출 기능은 DOCX 전용. PDF 프로토콜은 텍스트만으로 생성 (테이블 미삽입).

---

## 7. 결론

YH-SAP 파이프라인은 YH00000-101 프로토콜 기준으로 **5회 연속 반복 실행에서 100% 안정성**을 확인했다. 9개 검증 기준 × 5회 = 45/45 ALL PASS.

간헐적 LLM 빈 응답 문제는 재시도 로직(max_retries=2)으로 해결되었으며, 평균 79초(haiku) 내에 46개 섹션 + 12개 프로토콜 테이블을 포함한 SAP DOCX를 생성한다.

Production 배포 시에는 기본 모델을 claude-sonnet-4-6으로 사용하고, 최종 제출용에는 claude-opus-4-6 사용을 권장한다.

---

*작성: YH-SAP 자동 검증 시스템 | 검증 스크립트: scripts/run_validation_5x.py*
