# Install required libraries
# !pip install pdfplumber anthropic openai

import pdfplumber
import json
import anthropic
import openai
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Set up API keys
claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_text_from_pdf(pdf_path):
    """Extract all text from PDF"""
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
    return full_text

# ============================================================
# AGENT 1: OUTCOMES EXTRACTION WITH TYPES
# ============================================================

def extract_outcomes_with_types(pdf_text):
    """Extract outcomes WITH outcome types"""
    
    prompt = f"""You are analyzing a clinical trial protocol. Extract all primary and secondary outcomes with their timepoints AND outcome types.

For each outcome, determine if it is:
- "continuous" (measured on a continuous scale, e.g. blood pressure, score)
- "binary" (yes/no, success/failure, e.g. response rate)
- "time_to_event" (time until something happens, e.g. survival, time to progression)
- "count" (number of events, e.g. number of adverse events)
- "ordinal" (ordered categories, e.g. mild/moderate/severe)

Return the data in this exact JSON format:
{{
  "primary_outcomes": [
    {{
      "outcome": "description of the outcome measure",
      "timepoints": ["timepoint 1", "timepoint 2"],
      "outcome_type": "continuous/binary/time_to_event/count/ordinal"
    }}
  ],
  "secondary_outcomes": [
    {{
      "outcome": "description of the outcome measure",
      "timepoints": ["timepoint 1", "timepoint 2"],
      "outcome_type": "continuous/binary/time_to_event/count/ordinal"
    }}
  ]
}}

Protocol text:
{pdf_text[:100000]}

Return ONLY valid JSON, no other text. DO NOT include markdown formatting or code blocks."""

    try:
        response = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = response.content[0].text.strip()
        
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
            result = result.rsplit("```")[0]
        
        return json.loads(result)
    
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return None

def verify_outcomes_with_chatgpt(pdf_text, claude_results):
    """Verify outcomes extraction with ChatGPT"""
    
    prompt = f"""You are verifying an extraction of clinical trial outcomes. 

Here are the outcomes that were extracted:

{json.dumps(claude_results, indent=2)}

Now review the original protocol text and verify if this extraction is correct and complete:

{pdf_text[:80000]}

Respond in this JSON format:
{{
  "is_correct": true or false,
  "missing_outcomes": ["list any outcomes that were missed"],
  "incorrect_outcomes": ["list any outcomes that were extracted incorrectly"],
  "incorrect_outcome_types": ["list any outcomes with wrong type classification"],
  "missing_timepoints": ["list any timepoints that were missed"],
  "additional_notes": "any other observations",
  "confidence_score": "high/medium/low"
}}

Return ONLY valid JSON."""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a clinical trial protocol analyzer. Verify extractions accurately and return only JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=4000
        )
        
        result = response.choices[0].message.content.strip()
        
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
            result = result.rsplit("```")[0]
        
        return json.loads(result)
    
    except Exception as e:
        print(f"Error calling ChatGPT API: {e}")
        return None

# ============================================================
# AGENT 2: TRIAL DESIGN EXTRACTION
# ============================================================

def extract_trial_design(pdf_text):
    """Extract trial design information"""
    
    prompt = f"""You are analyzing a clinical trial protocol. Extract the key trial design elements.

Return the data in this exact JSON format:
{{
  "study_type": "RCT/observational/single_arm/other",
  "design": "parallel/crossover/factorial/adaptive/other",
  "randomization": "yes/no",
  "blinding": "open_label/single_blind/double_blind/triple_blind",
  "number_of_arms": number,
  "arms": [
    {{
      "name": "arm name",
      "description": "brief description",
      "sample_size": number or "not specified"
    }}
  ],
  "total_sample_size": number or "not specified",
  "duration": "study duration",
  "population": "target population description",
  "inclusion_criteria_summary": "brief summary",
  "exclusion_criteria_summary": "brief summary",
  "statistical_considerations": "any mentioned statistical approaches"
}}

Protocol text:
{pdf_text[:100000]}

Return ONLY valid JSON, no other text. DO NOT include markdown formatting or code blocks."""

    try:
        response = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = response.content[0].text.strip()
        
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
            result = result.rsplit("```")[0]
        
        return json.loads(result)
    
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return None

# ============================================================
# AGENT 3: STATISTICAL ANALYSIS PLAN
# ============================================================

def generate_analysis_plan(outcomes, trial_design, pdf_text):
    """Generate statistical analysis plan based on outcomes and design"""
    
    prompt = f"""You are a biostatistician creating a statistical analysis plan.

TRIAL DESIGN:
{json.dumps(trial_design, indent=2)}

OUTCOMES:
{json.dumps(outcomes, indent=2)}

PROTOCOL EXCERPT:
{pdf_text[:50000]}

Create a detailed statistical analysis plan. For each outcome, specify:
1. The statistical model to use
2. Covariates to adjust for (if any)
3. The comparison being made
4. Any sensitivity analyses

Return in this JSON format:
{{
  "primary_analyses": [
    {{
      "outcome": "outcome name",
      "outcome_type": "continuous/binary/time_to_event/etc",
      "model": "specific model (e.g., linear mixed model, logistic regression, Cox proportional hazards)",
      "comparison": "what is being compared (e.g., treatment vs control)",
      "covariates": ["covariate1", "covariate2"],
      "rationale": "why this model and these covariates",
      "handling_missing_data": "approach for missing data",
      "sensitivity_analyses": ["sensitivity analysis 1", "sensitivity analysis 2"]
    }}
  ],
  "secondary_analyses": [
    {{
      "outcome": "outcome name",
      "outcome_type": "continuous/binary/time_to_event/etc",
      "model": "specific model",
      "comparison": "what is being compared",
      "covariates": ["covariate1", "covariate2"],
      "rationale": "why this model and these covariates"
    }}
  ],
  "multiplicity_adjustment": "approach for multiple testing (e.g., Bonferroni, Hochberg, hierarchical testing)",
  "interim_analyses": "plan for interim analyses if applicable",
  "subgroup_analyses": ["subgroup 1", "subgroup 2"],
  "general_notes": "any other important statistical considerations"
}}

Be specific and practical. Consider the trial design when choosing models and covariates.

Return ONLY valid JSON, no other text. DO NOT include markdown formatting or code blocks."""

    try:
        response = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=6000,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = response.content[0].text.strip()
        
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
            result = result.rsplit("```")[0]
        
        return json.loads(result)
    
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return None

# ============================================================
# MAIN WORKFLOW
# ============================================================

def run_complete_analysis():
    """Main function orchestrating all three agents"""
    
    # Load PDF

    
    filename = "Protocols/boppp.pdf"
    
    # Extract PDF text
    print(f"\n{'='*70}")
    print("STEP 1: EXTRACTING TEXT FROM PDF")
    print('='*70)
    pdf_text = extract_text_from_pdf(filename)
    print(f"✓ Extracted {len(pdf_text)} characters\n")
    
    # ========================================
    # AGENT 1: OUTCOMES EXTRACTION
    # ========================================
    print(f"{'='*70}")
    print("STEP 2: AGENT 1 - EXTRACTING OUTCOMES WITH TYPES")
    print('='*70)
    print("Agent 1 is analyzing the protocol to extract outcomes...")
    
    outcomes = extract_outcomes_with_types(pdf_text)
    
    if not outcomes:
        print("Failed to extract outcomes. Exiting.")
        return
    
    print(f"\n✓ Agent 1 extracted:")
    print(f"  - {len(outcomes.get('primary_outcomes', []))} primary outcomes")
    print(f"  - {len(outcomes.get('secondary_outcomes', []))} secondary outcomes")
    
    # Verify with ChatGPT
    print("\nChatGPT is verifying the extraction...")
    verification = verify_outcomes_with_chatgpt(pdf_text, outcomes)
    
    if verification:
        print(f"\n✓ ChatGPT Verification:")
        print(f"  - Is Correct: {verification.get('is_correct')}")
        print(f"  - Confidence: {verification.get('confidence_score')}")
        if verification.get('additional_notes'):
            print(f"  - Notes: {verification['additional_notes']}")
    
    # Display outcomes to user
    print(f"\n{'='*70}")
    print("EXTRACTED OUTCOMES")
    print('='*70)
    
    print("\nPRIMARY OUTCOMES:")
    for i, item in enumerate(outcomes.get('primary_outcomes', []), 1):
        print(f"\n{i}. {item['outcome']}")
        print(f"   Type: {item['outcome_type']}")
        print(f"   Timepoints: {', '.join(item['timepoints'])}")
    
    print("\n\nSECONDARY OUTCOMES:")
    for i, item in enumerate(outcomes.get('secondary_outcomes', []), 1):
        print(f"\n{i}. {item['outcome']}")
        print(f"   Type: {item['outcome_type']}")
        print(f"   Timepoints: {', '.join(item['timepoints'])}")
    
    # User confirmation for outcomes
    print(f"\n{'='*70}")
    print("USER CONFIRMATION REQUIRED")
    print('='*70)
    outcomes_confirmation = input("\nAre these outcomes correct? (yes/no): ").strip().lower()
    
    if outcomes_confirmation not in ['yes', 'y']:
        feedback = input("What needs to be corrected? (or press Enter to skip): ").strip()
        print(f"\n⚠ Outcomes marked for review. Feedback: {feedback}")
        print("Continuing with current extraction...")
    else:
        print("\n✓ Outcomes confirmed by user!")
    
    # ========================================
    # AGENT 2: TRIAL DESIGN EXTRACTION
    # ========================================
    print(f"\n{'='*70}")
    print("STEP 3: AGENT 2 - EXTRACTING TRIAL DESIGN")
    print('='*70)
    print("Agent 2 is analyzing the trial design...")
    
    trial_design = extract_trial_design(pdf_text)
    
    if not trial_design:
        print("Failed to extract trial design. Exiting.")
        return
    
    print("\n✓ Agent 2 extracted trial design")
    
    # Display trial design
    print(f"\n{'='*70}")
    print("TRIAL DESIGN")
    print('='*70)
    print(f"\nStudy Type: {trial_design.get('study_type')}")
    print(f"Design: {trial_design.get('design')}")
    print(f"Randomization: {trial_design.get('randomization')}")
    print(f"Blinding: {trial_design.get('blinding')}")
    print(f"Number of Arms: {trial_design.get('number_of_arms')}")
    print(f"Total Sample Size: {trial_design.get('total_sample_size')}")
    print(f"Duration: {trial_design.get('duration')}")
    
    print("\nStudy Arms:")
    for arm in trial_design.get('arms', []):
        print(f"\n  - {arm['name']}")
        print(f"    Description: {arm['description']}")
        print(f"    Sample Size: {arm['sample_size']}")
    
    print(f"\nPopulation: {trial_design.get('population')}")
    print(f"\nInclusion Criteria: {trial_design.get('inclusion_criteria_summary')}")
    print(f"\nExclusion Criteria: {trial_design.get('exclusion_criteria_summary')}")
    print(f"\nStatistical Considerations: {trial_design.get('statistical_considerations')}")
    
    # User confirmation for trial design
    print(f"\n{'='*70}")
    print("USER CONFIRMATION REQUIRED")
    print('='*70)
    design_confirmation = input("\nIs this trial design correct? (yes/no): ").strip().lower()
    
    if design_confirmation not in ['yes', 'y']:
        feedback = input("What needs to be corrected? (or press Enter to skip): ").strip()
        print(f"\n⚠ Trial design marked for review. Feedback: {feedback}")
        print("Continuing with current extraction...")
    else:
        print("\n✓ Trial design confirmed by user!")
    
    # ========================================
    # AGENT 3: STATISTICAL ANALYSIS PLAN
    # ========================================
    print(f"\n{'='*70}")
    print("STEP 4: AGENT 3 - GENERATING STATISTICAL ANALYSIS PLAN")
    print('='*70)
    print("Agent 3 is creating a comprehensive statistical analysis plan...")
    print("This may take a moment as it considers the outcomes and trial design...\n")
    
    analysis_plan = generate_analysis_plan(outcomes, trial_design, pdf_text)
    
    if not analysis_plan:
        print("Failed to generate analysis plan. Exiting.")
        return
    
    print("✓ Agent 3 generated analysis plan")
    
    # Display analysis plan
    print(f"\n{'='*70}")
    print("STATISTICAL ANALYSIS PLAN")
    print('='*70)
    
    print("\nPRIMARY ANALYSES:")
    for i, analysis in enumerate(analysis_plan.get('primary_analyses', []), 1):
        print(f"\n{i}. {analysis['outcome'][:80]}...")
        print(f"   Outcome Type: {analysis['outcome_type']}")
        print(f"   Model: {analysis['model']}")
        print(f"   Comparison: {analysis['comparison']}")
        print(f"   Covariates: {', '.join(analysis.get('covariates', ['None']))}")
        print(f"   Rationale: {analysis.get('rationale', 'N/A')}")
        print(f"   Missing Data: {analysis.get('handling_missing_data', 'N/A')}")
        if analysis.get('sensitivity_analyses'):
            print(f"   Sensitivity Analyses:")
            for sa in analysis['sensitivity_analyses']:
                print(f"     - {sa}")
    
    print("\n\nSECONDARY ANALYSES:")
    for i, analysis in enumerate(analysis_plan.get('secondary_analyses', []), 1):
        print(f"\n{i}. {analysis['outcome'][:80]}...")
        print(f"   Outcome Type: {analysis['outcome_type']}")
        print(f"   Model: {analysis['model']}")
        print(f"   Comparison: {analysis['comparison']}")
        print(f"   Covariates: {', '.join(analysis.get('covariates', ['None']))}")
        print(f"   Rationale: {analysis.get('rationale', 'N/A')}")
    
    print("\n\nADDITIONAL CONSIDERATIONS:")
    print(f"Multiplicity Adjustment: {analysis_plan.get('multiplicity_adjustment', 'N/A')}")
    print(f"Interim Analyses: {analysis_plan.get('interim_analyses', 'N/A')}")
    print(f"Subgroup Analyses: {', '.join(analysis_plan.get('subgroup_analyses', ['None']))}")
    print(f"General Notes: {analysis_plan.get('general_notes', 'N/A')}")
    
    # User confirmation for analysis plan
    print(f"\n{'='*70}")
    print("USER CONFIRMATION REQUIRED")
    print('='*70)
    analysis_confirmation = input("\nIs this analysis plan correct? (yes/no): ").strip().lower()
    
    if analysis_confirmation not in ['yes', 'y']:
        feedback = input("What needs to be changed? (or press Enter to skip): ").strip()
        print(f"\n⚠ Analysis plan marked for review. Feedback: {feedback}")
    else:
        print("\n✓ Analysis plan confirmed by user!")
    
    # ========================================
    # SAVE FINAL OUTPUT
    # ========================================
    final_output = {
        "outcomes": outcomes,
        "outcomes_verification": verification,
        "trial_design": trial_design,
        "statistical_analysis_plan": analysis_plan,
        "user_confirmations": {
            "outcomes_confirmed": outcomes_confirmation in ['yes', 'y'],
            "design_confirmed": design_confirmation in ['yes', 'y'],
            "analysis_confirmed": analysis_confirmation in ['yes', 'y']
        },
        "status": "complete"
    }
    
    with open('clinical_trial_analysis_complete.json', 'w') as f:
        json.dump(final_output, f, indent=2)
    
    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE")
    print('='*70)
    print("\n✓ All agents have completed their tasks!")
    print("✓ Saved: clinical_trial_analysis_complete.json")
    
    files.download('clinical_trial_analysis_complete.json')
    
    # Print full JSON
    print(f"\n{'='*70}")
    print("FULL JSON OUTPUT")
    print('='*70)
    print(json.dumps(final_output, indent=2))
    
    # ========================================
    # INTERACTIVE Q&A
    # ========================================
    print(f"\n{'='*70}")
    print("INTERACTIVE MODE")
    print('='*70)
    print("Ask me anything about the extracted information, or type 'done' to finish.\n")
    
    while True:
        user_question = input("You: ").strip()
        
        if user_question.lower() in ['done', 'exit', 'quit', '']:
            print("\nGoodbye!")
            break
        
        try:
            response = claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Based on this clinical trial analysis:

OUTCOMES:
{json.dumps(outcomes, indent=2)}

TRIAL DESIGN:
{json.dumps(trial_design, indent=2)}

STATISTICAL ANALYSIS PLAN:
{json.dumps(analysis_plan, indent=2)}

User question: {user_question}

Please answer their question clearly and concisely."""
                    }
                ]
            )
            
            answer = response.content[0].text
            print(f"\nClaude: {answer}\n")
            
        except Exception as e:
            print(f"Error: {e}\n")
    
    return final_output

# ============================================================
# RUN THE COMPLETE ANALYSIS
# ============================================================

results = run_complete_analysis()