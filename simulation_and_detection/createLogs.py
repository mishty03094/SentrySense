import os
import random
import json
from datetime import datetime, timedelta

os.makedirs('logs', exist_ok=True)
SEED = 42
random.seed(SEED)

roles_actions = {
    "finance": ["accessed_payroll", "approved_payment", "viewed_report", "requested_refund", "exported_csv"],
    "developer": ["pushed_code", "accessed_repo", "deployed_app", "merged_pr", "ran_tests"],
    "sales": ["viewed_leads", "downloaded_report", "updated_client", "called_client", "sent_invoice"],
    "ops": ["restarted_server", "accessed_logs", "updated_config", "deployed_patch", "checked_uptime"],
    "admin": ["deleted_user", "created_user", "changed_permissions", "reset_password", "edited_policy"]
}

common_locations = ['US', 'UK', 'DE', 'FR', 'JP', 'IN', 'CN', 'CA', 'AU', 'IT']
rare_locations = ['RU', 'UA', 'BR', 'NG', 'IR', 'PK', 'VE']

num_logs = 12000
anomaly_ratio = 0.13  # Slightly higher to allow more overlap
anomaly_count = int(num_logs * anomaly_ratio)

logs = []
user_profiles = {}
anomaly_types = [
    "impossible_location", "unusual_time", "role_action_mismatch",
    "high_frequency_action", "subtle_time", "subtle_location", "feature_swap", "hard_negative"
]

base_time = datetime.now() - timedelta(days=60)

# Generate normal logs
for i in range(num_logs - anomaly_count):
    role = random.choice(list(roles_actions.keys()))
    user = f"user_{random.randint(1, 3500)}_{role}"
    if user not in user_profiles:
        user_profiles[user] = {
            "normal_location": random.choice(common_locations),
            "normal_hours": random.choice(range(8, 18)),
            "action_freq": {}
        }
    profile = user_profiles[user]
    location = profile["normal_location"]
    hour = profile["normal_hours"]
    action = random.choice(roles_actions[role])
    # Add subtle noise to normal logs (30% chance)
    if random.random() < 0.3:
        hour = (hour + random.choice([-3, -2, -1, 1, 2, 3])) % 24
        location = random.choice([loc for loc in common_locations if loc != location]) if random.random() < 0.2 else location
    # Feature swap: swap one feature with another user's profile (10% of normals)
    if random.random() < 0.1:
        swap_user = f"user_{random.randint(1, 3500)}_{role}"
        if swap_user in user_profiles and swap_user != user:
            location = user_profiles[swap_user]["normal_location"]
    log_time = (base_time + timedelta(minutes=i*random.randint(1,3))).replace(hour=hour, minute=random.randint(0,59), second=random.randint(0,59))
    logs.append({
        "user": user,
        "role": role,
        "location": location,
        "time": log_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "action": action,
        "risk_score": 0,
        "is_anomaly": 0,
        "anomaly_type": "normal"
    })

# Generate anomalies (mostly subtle and overlapping)
for i in range(anomaly_count):
    anomaly_type = random.choices(
        anomaly_types,
        weights=[0.06, 0.06, 0.10, 0.07, 0.25, 0.25, 0.15, 0.06],  # Most anomalies are subtle/overlapping
        k=1
    )[0]
    role = random.choice(list(roles_actions.keys()))
    user = f"user_{random.randint(1, 3500)}_{role}"
    location = random.choice(rare_locations) if anomaly_type == "impossible_location" else random.choice(common_locations)
    hour = random.choice([2, 3, 4, 22, 23]) if anomaly_type == "unusual_time" else random.choice(range(7, 21))
    action = random.choice(roles_actions[role])

    # Role-action mismatch
    if anomaly_type == "role_action_mismatch":
        wrong_role = random.choice([r for r in roles_actions if r != role])
        action = random.choice(roles_actions[wrong_role])
    # High frequency action
    if anomaly_type == "high_frequency_action":
        action = random.choice(roles_actions[role])
        for _ in range(3):
            log_time = (base_time + timedelta(minutes=random.randint(0, num_logs))).replace(hour=hour, minute=random.randint(0,59), second=random.randint(0,59))
            logs.append({
                "user": user,
                "role": role,
                "location": location,
                "time": log_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "action": action,
                "risk_score": 1,
                "is_anomaly": 1,
                "anomaly_type": anomaly_type
            })
        continue
    # Subtle anomalies
    if anomaly_type == "subtle_time":
        hour = (hour + random.choice([-4, -3, -2, -1, 1, 2, 3, 4])) % 24
    if anomaly_type == "subtle_location":
        if location in common_locations:
            location = random.choice([loc for loc in common_locations if loc != location])
    # Feature swap: swap multiple features with another user
    if anomaly_type == "feature_swap":
        swap_user = f"user_{random.randint(1, 3500)}_{role}"
        if swap_user in user_profiles and swap_user != user:
            location = user_profiles[swap_user]["normal_location"]
            hour = user_profiles[swap_user]["normal_hours"]
    # Hard negative: looks suspicious but is labeled as anomaly
    is_anomaly = 1
    if anomaly_type == "hard_negative":
        is_anomaly = 1
        # But make it look almost normal
        if random.random() < 0.7:
            location = random.choice(common_locations)
            hour = random.choice(range(8, 18))
    log_time = (base_time + timedelta(minutes=random.randint(0, num_logs))).replace(hour=hour, minute=random.randint(0,59), second=random.randint(0,59))
    logs.append({
        "user": user,
        "role": role,
        "location": location,
        "time": log_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "action": action,
        "risk_score": 1,
        "is_anomaly": is_anomaly,
        "anomaly_type": anomaly_type
    })

# Add a small amount of random label noise to normal logs
for log in random.sample([l for l in logs if l["is_anomaly"] == 0], k=int(0.05 * len(logs))):
    log["is_anomaly"] = 1
    log["anomaly_type"] = "random_label_noise"

random.shuffle(logs)

with open("logs/sample_logs.json", "w") as f:
    json.dump(logs, f, indent=2)

print(f"Generated {len(logs)} logs with {sum(log['is_anomaly'] for log in logs)} anomalies.")
