import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
# Get path to project root
root_dir = os.path.dirname(os.path.dirname(__file__))
env_path = os.path.join(root_dir, '.env')


load_dotenv(dotenv_path=env_path)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
threats_folder = os.path.join(os.path.dirname(__file__), "threats")
output_file = os.path.join(os.path.dirname(__file__), "predicted_threats.json")

# Initialize model
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")


# Improved, more practical prompt
prompt_template = """
You are a cybersecurity AI assistant. Analyze the following threat report in detail. Your response should include:

1. A short, clear, practical risk assessment for a modern organization.
2. Specific, actionable steps to mitigate or prevent the threat.
3. Keep the language concise, focused, and suitable for technical decision-makers.

Threat Report:
\"\"\"
{threat_report}
\"\"\"

Provide your response in clear, organized text format.
"""

# Collect predictions
predictions = []

# Loop through threat files
for filename in os.listdir(threats_folder):
    if filename.endswith(".txt"):
        file_path = os.path.join(threats_folder, filename)

        with open(file_path, 'r') as f:
            threat_report = f.read()

        # Fill in prompt
        prompt = prompt_template.format(threat_report=threat_report)

        # Generate prediction
        response = model.generate_content(prompt)
        prediction = response.text.strip()

        # Store result
        predictions.append({
            "file": filename,
            "threat_report": threat_report,
            "ai_prediction": prediction
        })

        print(f"Processed {filename}")

with open(output_file, 'w') as f:
    json.dump(predictions, f, indent=4)

print(f"\nPredictions saved to {output_file}")

