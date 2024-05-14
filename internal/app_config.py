import json

with open("configs/platform.json", "r") as f:
    platform_env = json.load(f)
    f.close()

with open("configs/auth.json", "r") as f:
    auth = json.load(f)
    f.close()

with open("configs/db.json", "r") as f:
    database = json.load(f)
    f.close()

with open("configs/mail.json", "r") as f:
    mail_config = json.load(f)
    f.close()


def scanapi_parse(scanapi):
    polygon_scan_api_key = scanapi["polygon_scan_api_key"]
    polygon_scan_api_url = scanapi["polygon_scan_api_url"]
    return polygon_scan_api_key, polygon_scan_api_url
