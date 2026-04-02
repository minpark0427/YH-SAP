"""
SAP Quality Validator — LLM-based comparison of AI-generated SAP vs human-written SAP.

Uses the Yuhan SAP checklist as evaluation criteria.
Runs claude CLI for each evaluation item.
"""

import subprocess
import json
import sys
import os
from pathlib import Path


def claude_evaluate(prompt: str, model: str = "claude-sonnet-4-5") -> str:
    """Call claude CLI and return response."""
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)
    result = subprocess.run(
        ["claude", "--print", "-p", "-", "--model", model],
        capture_output=True, text=True, input=prompt, env=env, timeout=300,
    )
    if result.returncode != 0:
        return f"ERROR: {result.stderr[:200]}"
    return result.stdout.strip()


# Checklist items mapped to SAP sections
CHECKLIST_ITEMS = [
    {
        "id": "1",
        "category": "임상시험 기본 정보",
        "questions": [
            "임상시험의 목적 및 디자인, 산출된 대상자수 관련 설명이 임상시험 계획서의 내용과 다르거나 누락된 내용이 없는가?",
            "유효성 및 안전성 평가변수가 임상시험 계획서와 다르거나 누락된 내용이 없는가?",
        ],
        "ai_tags": ["introduction", "objectives", "sample_size"],
        "human_sections": ["INTRODUCTION", "TRIAL OBJECTIVES", "SYNOPSIS"],
    },
    {
        "id": "2",
        "category": "분석군 정의 및 임상시험 참여 상태/기저치 특성",
        "questions": [
            "분석군 정의가 기술되어 있고, 기술된 분석군의 정의가 임상시험 계획서의 내용과 상반되거나 누락된 내용이 없는가?",
            "통계분석별 대상 분석군을 명시하고 있는가?",
            "대상자의 임상시험 참여 상태, 분석군별 분포, 인구학적 정보 및 기저치 특성에 대한 적절한 통계분석 방법이 기술되어 있는가?",
        ],
        "ai_tags": ["screened_set", "randomized_set", "safety_set", "fas_definition", "pps_definition", "subject_disposition", "demographics"],
        "human_sections": ["Analysis Sets", "Subject Disposition", "Demographics"],
    },
    {
        "id": "3",
        "category": "병력/선행/병용약물",
        "questions": [
            "적절한 통계분석 방법이 기술되어 있는가?",
            "의학적 코딩 사전의 명칭 및 버전과 분석되는 Coding Level이 명시되어 있는가?",
            "선행약물과 병용약물의 구분 기준이 명시되어 있는가?",
        ],
        "ai_tags": ["medical_history", "concomitant_medication"],
        "human_sections": ["Medical History", "Prior and Concomitant Medication"],
    },
    {
        "id": "4",
        "category": "순응도 및 노출",
        "questions": [
            "적절한 통계분석 방법이 기술되어 있는가?",
            "순응도 그리고/또는 노출 계산 방법이 제시되어 있는가?",
        ],
        "ai_tags": ["ip_exposure", "treatment_compliance"],
        "human_sections": ["IP Compliance"],
    },
    {
        "id": "5",
        "category": "유효성 평가변수",
        "questions": [
            "적절한 통계분석 방법이 기술되어 있는가?",
            "주분석군에 대해 명시하고 있는가?",
            "유의수준이 명시되어 있는가?",
        ],
        "ai_tags": ["primary_efficacy", "secondary_efficacy", "additional_efficacy"],
        "human_sections": ["Pharmacokinetics Analyses", "Pharmacodynamic Analyses"],
    },
    {
        "id": "6",
        "category": "안전성 평가변수",
        "questions": [
            "적절한 통계분석 방법이 기술되어 있는가?",
            "통계분석 방법이 누락된 안전성 평가변수가 없는가?",
            "의학적 코딩 사전의 명칭 및 버전과 분석되는 Coding Level이 명시되어 있는가?",
        ],
        "ai_tags": ["adverse_events", "lab_parameters", "vital_signs", "ecg", "physical_exam", "other_safety"],
        "human_sections": ["Safety Analysis"],
    },
    {
        "id": "7",
        "category": "결측치 처리방법",
        "questions": [
            "중도탈락 대상자 등 유효성 평가변수에 대한 일반적 결측치 처리방법이 적절한가?",
            "안전성 평가변수에 대한 결측치 처리방법이 적절한가?",
            "날짜의 일부 또는 전체의 누락, Visit Window 위반에 대한 처리방법이 적절한가?",
        ],
        "ai_tags": ["visit_windows", "derived_variables", "missing_last_dose_date", "missing_ae_severity", "missing_causality", "missing_dates", "lab_char_values"],
        "human_sections": ["Definition of Baseline"],
    },
    {
        "id": "8",
        "category": "기타 (중간분석, 다중성, 소프트웨어, 프로토콜 변경)",
        "questions": [
            "중간분석에 대한 적절한 통계분석 방법이 기술되어 있는가?",
            "통계분석에 이용되는 통계 프로그램이 명시되어 있는가?",
            "임상시험 계획서에서 명시된 통계분석방법에서 변경된 내용이 없는가?",
        ],
        "ai_tags": ["interim_analysis", "dmc_analysis", "statistical_software_version", "statistical_considerations", "protocol_changes"],
        "human_sections": ["SOFTWARE LIST"],
    },
]


def extract_ai_sections(content_path: str, tags: list[str]) -> str:
    """Extract specific sections from AI-generated SAP content file."""
    with open(content_path, "r") as f:
        content = f.read()

    parts = []
    for tag in tags:
        marker = f"{tag}: "
        idx = content.find(marker)
        if idx == -1:
            continue
        # Find next tag or end
        next_idx = len(content)
        for other_tag in tags:
            if other_tag == tag:
                continue
        # Simple approach: find next line that starts a new tag
        lines = content[idx:].split("\n")
        section_lines = [lines[0]]
        for line in lines[1:]:
            # New tag starts with "word_word: " pattern
            if line and not line.startswith(" ") and ": " in line[:50] and "_" in line.split(":")[0]:
                break
            section_lines.append(line)
        parts.append("\n".join(section_lines))

    return "\n\n---\n\n".join(parts)


def main():
    ai_content_path = "sap-kcl/SAPs_v3/YH_SAP_YH00000-101_Clinical Protocol_Ver1.0_22Feb2024_content.txt"
    human_sap_path = "/tmp/human_sap.txt"

    with open(human_sap_path, "r") as f:
        human_sap = f.read()

    with open(ai_content_path, "r") as f:
        ai_content = f.read()

    print("=" * 80)
    print("SAP QUALITY VALIDATION REPORT")
    print("AI-generated SAP vs Human-written SAP")
    print("Based on Yuhan Corporation SAP Checklist")
    print("=" * 80)
    print()

    results = []

    for item in CHECKLIST_ITEMS:
        print(f"\n{'='*60}")
        print(f"Checklist {item['id']}: {item['category']}")
        print(f"{'='*60}")

        ai_text = extract_ai_sections(ai_content_path, item["ai_tags"])

        # Truncate human SAP to relevant parts (keep under token limits)
        human_excerpt = human_sap[:80000]  # First 80K covers most content sections

        prompt = f"""You are a senior biostatistician reviewing a Statistical Analysis Plan (SAP) for a Phase 1 clinical trial (YH00000-101).

TASK: Compare the AI-generated SAP sections against the human-written reference SAP, using the Yuhan Corporation SAP checklist criteria below.

CHECKLIST CATEGORY: {item['category']}

CHECKLIST QUESTIONS:
{chr(10).join(f"  Q{i+1}. {q}" for i, q in enumerate(item['questions']))}

=== AI-GENERATED SAP (relevant sections) ===
{ai_text[:15000]}

=== HUMAN-WRITTEN SAP (reference, excerpt) ===
{human_excerpt[:15000]}

INSTRUCTIONS:
1. For each checklist question, evaluate the AI-generated SAP.
2. Score each question: PASS (adequate), PARTIAL (some gaps), FAIL (missing/wrong).
3. Provide specific evidence from both documents.
4. Note any information present in human SAP but missing in AI SAP.
5. Note any information the AI SAP adds that is NOT in the protocol (hallucination risk).

FORMAT YOUR RESPONSE AS:
## Checklist {item['id']}: {item['category']}

### Q1: [question text]
**Score**: [PASS/PARTIAL/FAIL]
**AI SAP**: [what was found]
**Human SAP**: [what the reference says]
**Gap**: [what's missing or different]

[repeat for each question]

### Overall Assessment
**Score**: [X/Y PASS]
**Key Gaps**: [bullet points]
**Hallucination Risk**: [any fabricated content?]

Answer in English. Be specific and cite actual content from both documents.
"""

        print(f"  Evaluating {len(item['questions'])} questions...")
        response = claude_evaluate(prompt)
        print(response)
        results.append({
            "id": item["id"],
            "category": item["category"],
            "response": response,
        })

    # Final summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)

    summary_prompt = f"""Based on the following SAP validation results, provide a concise executive summary.

{chr(10).join(f"Checklist {r['id']} ({r['category']}): {r['response'][:500]}" for r in results)}

Provide:
1. Overall quality score (percentage of PASS across all questions)
2. Top 3 most critical gaps
3. Top 3 strengths of the AI-generated SAP
4. Recommendation: Is this SAP ready for human review? What sections need the most attention?

Be specific and actionable. Answer in Korean for the Yuhan team.
"""

    summary = claude_evaluate(summary_prompt)
    print(summary)

    # Save full report
    report_path = "sap-kcl/SAPs_v3/validation_report.md"
    with open(report_path, "w") as f:
        f.write("# SAP Quality Validation Report\n\n")
        f.write("AI-generated SAP vs Human-written SAP\n")
        f.write("Based on Yuhan Corporation SAP Checklist\n\n")
        for r in results:
            f.write(f"\n---\n\n{r['response']}\n")
        f.write(f"\n---\n\n# Executive Summary\n\n{summary}\n")

    print(f"\nFull report saved to: {report_path}")


if __name__ == "__main__":
    os.chdir("/Users/mymini/Vibecoding/YH-SAP")
    main()
