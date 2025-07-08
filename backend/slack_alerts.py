import requests

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"  # replace with your real one

def send_slack_alert(message: str, blocks: list = None):
    payload = {"text": message}
    if blocks:
        payload["blocks"] = blocks  # for rich formatting

    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        print("Slack Error:", response.text)