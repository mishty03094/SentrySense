import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from mock_infra import mock_infrastructure

# Get project root
root_dir = os.path.dirname(os.path.dirname(__file__))
env_path = os.path.join(root_dir, '.env')

load_dotenv(dotenv_path=env_path)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

threats_folder = os.path.join(os.path.dirname(__file__), "threats")
output_file = os.path.join(os.path.dirname(__file__), "predicted_threats.json")

model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

# Load infrastructure for prompt
infra_text = json.dumps(mock_infrastructure, indent=2)

# Load existing predictions to avoid duplicates
if os.path.exists(output_file):
    with open(output_file, 'r') as f:
        predictions = json.load(f)
    processed_files = {item["file"] for item in predictions}
else:
    predictions = []
    processed_files = set()

# Updated prompt template
prompt_template = """
You are a cybersecurity AI assistant for an organization. Analyze the following CVE threat. Your response must:

- Give a clear, modern, technical description of the threat.
- Identify realistic affected systems based on this infrastructure:
{infra}
- Suggest specific, actionable fixes for the organization.
- Assign a risk level (Medium, High, Critical).
- Provide a realistic confidence score (0-1) with reasoning based on severity, exploitability, and relevance to the provided infrastructure.

DO NOT include references from the report.

CVE Report:
\"\"\" 
{threat_report}
\"\"\"

Provide your response strictly as valid JSON with the following fields:
- threat_type: Short threat title.
- predicted_time: Leave blank, we will auto-fill.
- description: Detailed, practical threat explanation.
- risk_level: One of "Medium", "High", or "Critical".
- affected_systems: List of realistically affected systems (hostnames or devices).
- suggested_fixes: Specific, actionable fixes.
"""

# Process only new CVEs
for filename in os.listdir(threats_folder):
    if not filename.endswith(".txt") or filename in processed_files:
        continue

    file_path = os.path.join(threats_folder, filename)
    
    with open(file_path, 'r') as f:
        threat_report = f.read()

    prompt = prompt_template.format(threat_report=threat_report, infra=infra_text)

    try:
        response = model.generate_content(prompt)
        ai_output = response.text.strip()

        print(f"\n----- RAW AI OUTPUT for {filename} -----\n{ai_output}\n--------------------------------------\n")

        # Remove wrapping triple backticks if present
        if ai_output.startswith("```json"):
            ai_output = ai_output[len("```json"):].strip()
        if ai_output.endswith("```"):
            ai_output = ai_output[:-3].strip()

        if not ai_output:
            print(f"Empty AI output for {filename}, skipping...\n")
            continue

        prediction = json.loads(ai_output)
        prediction["file"] = filename

        predictions.append(prediction)
        print(f"Processed {filename}\n")

    except Exception as e:
        print(f"Error processing {filename}: {e}\n")

with open(output_file, 'w') as f:
    json.dump(predictions, f, indent=4)

print(f"\nPredictions saved to {output_file}")
