# Simulated infrastructure map for SentrySense

mock_infrastructure = {
    "servers": [
        {
            "hostname": "web-server-01",
            "ip": "192.168.1.10",
            "os": "Ubuntu 22.04 LTS",
            "services": ["Nginx", "Gunicorn", "Flask API"],
            "critical": True
        },
        {
            "hostname": "app-server-01",
            "ip": "192.168.1.20",
            "os": "Ubuntu 22.04 LTS",
            "services": ["Python Backend", "Celery Worker", "Redis"],
            "critical": True
        },
        {
            "hostname": "db-server-01",
            "ip": "192.168.1.30",
            "os": "PostgreSQL 15 on Ubuntu 22.04",
            "services": ["PostgreSQL Database"],
            "critical": True
        },
        {
            "hostname": "file-server-01",
            "ip": "192.168.1.40",
            "os": "CentOS 7",
            "services": ["NFS", "FTP"],
            "critical": False
        }
    ],

    "network_devices": [
        {
            "device_name": "core-switch-01",
            "ip": "192.168.1.1",
            "type": "Layer 3 Switch",
            "vendor": "Cisco"
        },
        {
            "device_name": "firewall-01",
            "ip": "192.168.1.254",
            "type": "Next-Gen Firewall",
            "vendor": "Fortinet"
        }
    ],

    "cloud_assets": [
        {
            "provider": "AWS",
            "service": "EC2",
            "region": "us-east-1",
            "instance_type": "t3.large",
            "os": "Amazon Linux 2",
            "critical": True
        },
        {
            "provider": "AWS",
            "service": "S3",
            "region": "us-east-1",
            "bucket_name": "sentrysense-logs",
            "purpose": "Log storage",
            "critical": False
        }
    ],

    "software_stack": [
        "Python 3.9",
        "Flask",
        "PostgreSQL 15",
        "Redis",
        "Docker",
        "Nginx",
        "Ubuntu 22.04 LTS",
        "AWS EC2",
        "AWS S3",
        "Celery",
        "GitLab CI/CD"
    ]
}
