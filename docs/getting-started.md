# 설치 가이드

## Step 1: 저장소 클론

```bash
git clone https://github.com/minpark0427/YH-SAP.git
cd YH-SAP
```

## Step 2: Python 가상환경 설정

```bash
# Python 3.11 이상 필요
python3 -m venv YH-SAP-venv
source YH-SAP-venv/bin/activate   # Mac/Linux
# Windows: YH-SAP-venv\Scripts\activate

pip install -r sap-kcl/requirements.txt
pip install python-docx docxtpl PyPDF2 anthropic python-dotenv
```

## Step 3: Claude Code 설치

이 파이프라인의 기본 LLM 백엔드는 **Claude Code CLI**입니다.

```bash
# Claude Code CLI 설치 (npm 필요)
npm install -g @anthropic-ai/claude-code

# 인증 (최초 1회)
claude login

# 설치 확인
claude --version
```

!!! note "Anthropic 구독"
    Claude Code는 Anthropic 구독이 필요합니다. API 키 방식을 사용하려면 실행 시 `--backend anthropic`을 사용하고 `ANTHROPIC_API_KEY` 환경변수를 설정하세요.

## Step 4: 프로토콜 파일 준비

프로젝트 루트에 분석할 프로토콜 파일을 넣습니다:

```bash
cp /path/to/YH#####-###_Clinical_Protocol.docx .
```

!!! tip "DOCX 권장"
    DOCX 프로토콜은 테이블 자동 추출이 가능합니다. PDF는 텍스트만 추출됩니다.

## 사용 방법

### 기본 실행

```bash
cd sap-kcl
source ../YH-SAP-venv/bin/activate

# SAP 생성 (기본 모델: claude-sonnet-4-6)
python -m WriteSAPs.yuhan_sap_json ../프로토콜파일.docx
```

### 모델 선택

| 모델 | 속도 | 품질 | 용도 | 명령어 |
|------|------|------|------|--------|
| `claude-haiku-4-5` | ~80초 | ★★★ | 테스트, 프롬프트 튜닝 | `--test` |
| `claude-sonnet-4-6` | ~3분 | ★★★★ | 일상 업무, 팀 배포 | (기본값) |
| `claude-opus-4-6` | ~10분 | ★★★★★ | 최종 제출, 통계 추론 | `--model claude-opus-4-6` |

```bash
# 테스트 (빠름, 1-2분)
python -m WriteSAPs.yuhan_sap_json ../프로토콜.docx --test

# 기본 (sonnet, 3-5분)
python -m WriteSAPs.yuhan_sap_json ../프로토콜.docx

# 최고 품질 (opus, 10-15분)
python -m WriteSAPs.yuhan_sap_json ../프로토콜.docx --model claude-opus-4-6

# 출력 폴더 지정
python -m WriteSAPs.yuhan_sap_json ../프로토콜.docx --output-dir SAPs_최종
```

### 출력 파일

```
SAPs_출력폴더/
├── YH_SAP_프로토콜명.docx         ← SAP 문서 (Word로 열기)
└── YH_SAP_프로토콜명_content.txt  ← 원문 텍스트 (디버깅용)
```

## 출력물 이해하기

### 정상 내용
일반 검정 텍스트로 프로토콜 기반 SAP 내용이 작성됩니다.

### 노란색 하이라이트 `[REVIEW NEEDED]`
프로토콜에 관련 정보가 부족하여 AI가 내용을 생성하지 못한 섹션입니다.

→ 통계 담당자가 직접 작성하거나 프로토콜 확인 후 보완해야 합니다.

### 프로토콜 테이블
프로토콜에서 자동 추출된 테이블(Objectives, Schedule of Activities, PK Parameters 등)이 해당 섹션에 삽입됩니다.
