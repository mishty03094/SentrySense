import requests
import os

# 1. Create folder to save threat reports inside predictive_ai/threats
current_dir = os.path.dirname(__file__)  # Gets path to predictive_ai
output_folder = os.path.join(current_dir, "threats")
os.makedirs(output_folder, exist_ok=True)

# 2. Define API URL - Limit to recent 5 CVEs (no severity filter to include both HIGH & MEDIUM)
url = "https://services.nvd.nist.gov/rest/json/cves/2.0?resultsPerPage=5"

# 3. Add headers to avoid 404 (pretend to be a browser)
headers = {
    "User-Agent": "Mozilla/5.0 (compatible; SentrySense/1.0)"
}

# 4. Fetch data
response = requests.get(url, headers=headers)

# 5. Check response
if response.status_code != 200:
    print(f"Error fetching data. Status code: {response.status_code}")
    exit()

data = response.json()

count = 0  # To track saved files

# 6. Loop through vulnerabilities
for item in data.get('vulnerabilities', []):
    cve = item.get('cve', {})
    cve_id = cve.get('id', 'N/A')

    # Skip if file already exists
    file_path = os.path.join(output_folder, f"{cve_id}.txt")
    if os.path.exists(file_path):
        print(f"{cve_id} already exists. Skipping...")
        continue

    # Extract English description
    descriptions = cve.get('descriptions', [])
    description = next((d['value'] for d in descriptions if d['lang'] == 'en'), 'No description available.')

    # Extract severity and score
    metrics = cve.get('metrics', {})
    severity = 'Unknown'
    score = 'Unknown'

    if 'cvssMetricV2' in metrics:
        metric = metrics['cvssMetricV2'][0]
        severity = metric.get('baseSeverity', 'Unknown')
        score = metric.get('cvssData', {}).get('baseScore', 'Unknown')

    # Extract published date
    published_date = cve.get('published', 'Unknown')

    # Filter for HIGH and MEDIUM severity only
    if severity in ["HIGH", "MEDIUM"]:
        with open(file_path, 'w') as f:
            f.write(f"CVE ID: {cve_id}\n")
            f.write(f"Published Date: {published_date}\n")
            f.write(f"Description: {description}\n")
            f.write(f"Severity: {severity} (Score: {score})\n")

            # Add reference links
            references = cve.get('references', [])
            if references:
                f.write("References:\n")
                for ref in references:
                    f.write(f" - {ref.get('url', '')}\n")

        print(f"Saved {cve_id}.txt ({severity})")
        count += 1

print(f"\nTotal NEW HIGH/MEDIUM severity threats saved: {count}")
