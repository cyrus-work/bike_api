import requests


def get_token_balance(api_key, address, contract_address):
    url = "https://api.polygonscan.com/api"
    params = {
        "module": "account",
        "action": "tokenbalance",
        "contractAddress": contract_address,
        "address": address,
        "tag": "latest",
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] == "1":
        return int(data["result"]) / (10 ** 18)  # Assuming the token has 18 decimals
    else:
        print(f"Error: {data['message']}")
        return None
