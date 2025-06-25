import requests

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"  # replace with your real one

def send_slack_alert(message: str):
    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        print("Slack Error:", response.text)
