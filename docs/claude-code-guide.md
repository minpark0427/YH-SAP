# Claude Code로 SAP 생성하기

Claude Code는 AI와 대화하면서 코드를 실행할 수 있는 터미널 도구입니다.
SAP 생성을 가장 쉽게 하는 방법입니다.

## 1단계: 터미널에서 Claude Code 열기

```bash
# YH-SAP 폴더로 이동
cd /path/to/YH-SAP

# Claude Code 시작 — 프로젝트 폴더에서 실행해야 CLAUDE.md를 자동 인식합니다
claude
```

터미널에 `>` 프롬프트가 나타나면 준비 완료입니다.

## 2단계: SAP 생성 요청 (자연어)

Claude Code 프롬프트에 한국어 또는 영어로 요청합니다:

```
> 프로토콜 파일 YH12345-101_Clinical_Protocol.docx로 SAP를 생성해줘.
> 테스트 모드로 먼저 돌려봐.
```

Claude Code가 알아서:

1. 가상환경을 활성화하고
2. 파이프라인을 실행하고
3. 결과를 확인해서 알려줍니다

## 3단계: 결과 확인 및 재실행

```
> 결과 어때? ERROR나 SKIP이 몇 개야?

> 괜찮으면 sonnet 모델로 다시 생성해줘.

> primary_efficacy 섹션만 opus로 다시 생성할 수 있어?
```

## 실제 사용 예시 (대화 흐름)

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

## 직접 명령어 실행 (대화 없이)

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
```

## 검증 실행

생성된 SAP의 품질을 확인하려면:

```
사용자> 방금 생성한 SAP를 5회 반복 검증해줘

Claude> [run_validation_5x.py 실행]
       5/5 ALL PASS
       - 46 tags, 0 errors, 0 markdown, 0 blue...
```

또는 직접:

```bash
python scripts/run_validation_5x.py
```
