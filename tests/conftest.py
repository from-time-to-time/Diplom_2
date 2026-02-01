import random
import string
import pytest
import allure
from src.stellar_burger_api import StellarBurgerApi

def _rnd(n=10):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(n))

@pytest.fixture
def register_new_user():
    api = StellarBurgerApi()
    payload = {"email": f"{_rnd()}@example.com", "password": _rnd(), "name": _rnd()}

    with allure.step("Регистрируем пользователя"):
        resp = api.create_user(json=payload)
        assert resp.status_code == 200, f"Регистрация упала: {resp.status_code} {resp.text}"
        body = resp.json()

    access_token = body["accessToken"]
    assert isinstance(access_token, str) and access_token.startswith("Bearer "), "Неверный формат accessToken"

    return {
        "email": payload["email"],
        "password": payload["password"],
        "name": payload["name"],
        "access_token": access_token,
        "refresh_token": body.get("refreshToken"),
        "response": body
    }

@pytest.fixture
def cleanup_user(register_new_user):
    api = StellarBurgerApi()

    yield register_new_user

    try:
        api.delete_user(headers={"Authorization": register_new_user['access_token']})
    except Exception as e:
        print(f"[cleanup] failed for {register_new_user['email']}: {e}")

@pytest.fixture
def user_payload():
    return {
        "email": f"{_rnd()}@example.com",
        "password": _rnd(),
        "name": _rnd()
    }

@pytest.fixture
def valid_ingredients():
    return ["61c0c5a71d1f82001bdaaa6d", "61c0c5a71d1f82001bdaaa71", "61c0c5a71d1f82001bdaaa74"]


@pytest.fixture
def invalid_ingredients():
    return ["61c0c5a71d1f82001bdaaa74test", "te61c0c5a71d1f82001bdaaa74st"]

@pytest.fixture
def make_order_request(register_new_user, valid_ingredients, invalid_ingredients):

    api_client = StellarBurgerApi()

    def _make(auth=True, ingredients_type="valid"):
        with allure.step("Формируем запрос для создания заказа"):
            headers = {"Authorization": register_new_user["access_token"]} if auth else {}

            if ingredients_type == "valid":
                body = {"ingredients": valid_ingredients}
            elif ingredients_type == "invalid":
                body = {"ingredients": invalid_ingredients}
            else:
                body = {"ingredients": []}

        with allure.step("Отправляем запрос"):
            return api_client.create_order(json=body, headers=headers)

    return _make