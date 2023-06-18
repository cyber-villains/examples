import requests


BASE_URL = "https://certificate.stream"
TOKEN_ENDPOINT = "https://api.villain.network/oauth2/token"


def get_token(id, secret) -> str:
    payload = f"client_secret={secret}&client_id={id}&grant_type=client_credentials"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    response = requests.request("POST", TOKEN_ENDPOINT, headers=headers, data=payload)
    response.raise_for_status()
    token = response.json()["access_token"]
    return token


def get_domains(token: str, params: dict) -> dict:
    url = f"{BASE_URL}/domains/list"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    response = requests.request("GET", url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()
