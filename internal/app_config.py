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

with open("configs/reward.json", "r") as f:
    reward = json.load(f)
    f.close()

# blockchain config for polygon
with open("configs/blockchain/mainnet.json", "r") as f:
    mainnet = json.load(f)
    f.close()

# blockchain config for amoy
with open("configs/blockchain/testnet.json", "r") as f:
    testnet = json.load(f)
    f.close()

# blockchain config for token abi
with open("configs/blockchain/token_abi.json", "r") as f:
    token_abi = json.load(f)
    f.close()

# blockchain config for setting
with open("configs/blockchain/setting.json", "r") as f:
    setting = json.load(f)
    f.close()


def scanapi_parse(scanapi):
    polygon_scan_api_key = scanapi["polygon_scan_api_key"]
    polygon_scan_api_url = scanapi["polygon_scan_api_url"]
    return polygon_scan_api_key, polygon_scan_api_url


def network_config_parse(netconfig):
    polygon_rpc_url = netconfig["polygon_rpc_url"]
    private_key = netconfig["owner_private_key"]
    token_address = netconfig["token_address"]
    chain_id = netconfig["chain_id"]
    return polygon_rpc_url, private_key, token_address, chain_id
