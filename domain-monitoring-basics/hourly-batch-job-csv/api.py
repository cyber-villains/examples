import requests


BASE_URL = "https://certificate.stream/v1"
TOKEN_ENDPOINT = "https://api.typovillain.com/oauth2/token"


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


def get_domains_csv_streamer(token: str, date_and_hour: str):
    url = f"{BASE_URL}/domains/csv"
    params = {"date_and_hour": date_and_hour}
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    sess = requests.Session()
    with sess.get(url, headers=headers, params=params, stream=True) as response:
        for line in response.iter_lines():
            yield line
