import os
import requests

AUTH_ADDR = os.environ.get('AUTH_SVC_ADDRESS')

def login(request):
    auth = request.authorization
    if not auth:
        return None, ("missing credentials", 401)

    response = requests.post(
        f"http://{AUTH_ADDR}/api/v1/auth/login",
        auth=(auth.username, auth.password),
    )
    if response.status_code == 200:
        return response.text, None
    return None, (response.text, response.status_code)

def register(request):
    data = request.get_json()
    response = requests.post(
        f"http://{AUTH_ADDR}/api/v1/auth/register",
        json=data,
    )
    if response.status_code in (200, 201):
        return response.text, None
    return None, (response.text, response.status_code)
