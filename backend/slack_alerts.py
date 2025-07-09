import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_alert(message: str, blocks: list = None):
    if not SLACK_WEBHOOK_URL:
        print("Slack Webhook URL not found in environment.")
        return

    payload = {"text": message}
    if blocks:
        payload["blocks"] = blocks

    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        print("Slack Error:", response.text)
