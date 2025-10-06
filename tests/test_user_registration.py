import pytest
from src.stellar_burger_api import StellarBurgerApi
import allure


class TestUserRegistration:
    @allure.title('Проверка создания нового пользователя')
    def test_create_new_user(self, user_payload, cleanup_user):
        api = StellarBurgerApi()
        with allure.step("Отправляем запрос на создание пользователя со всеми полями незарегистрированного пользователя из фикстуры"):
            resp = api.create_user(json=user_payload)

        with allure.step("Проверяем, что пользователь успешно создан: есть статус-код и тело ответа"):
            assert resp.status_code == 200, f"Ожидали 200, получили {resp.status_code}: {resp.text}"

            body = resp.json()
            assert body.get("success") is True, f"Ожидали success=true, получили: {body.get('success')}"

            assert body["user"].get("email") == user_payload["email"], f"email не совпадает: {body['user'].get('email')} != {user_payload['email']}"

            assert body["user"].get("name") == user_payload["name"], f"name не совпадает: {body['user'].get('name')} != {user_payload['name']}"

            assert "accessToken" in body, "Нет accessToken в ответе"

            assert "refreshToken" in body, "Нет refreshToken в ответе"

    @allure.title('Проверка создания пользователя, который уже зарегистрирован')
    def test_cant_create_existing_user(self, register_new_user, cleanup_user):
        api = StellarBurgerApi()
        with allure.step('Создаем пользователя и берем его данные'):

            assert register_new_user, "Фикстура не создала пользователя"

            existing_email, existing_password, existing_name = register_new_user['email'], register_new_user['password'], register_new_user['name']

        with allure.step('Готовим тело запроса для создания с теми же полями'):
            body = {
                "email": existing_email,
                "password": existing_password,
                "name": existing_name,
            }
        with allure.step('Отправляем POST-запрос с теми же данными, что и у ранее созданного курьера'):
            response = api.create_user(json=body)

        with allure.step('Проверяем, что в ответе получили ошибку 403'):
            assert response.status_code == 403

            message = response.json()['message']
            assert "User already exists" in message


    @allure.title('Проверка получения ошибки при создании пользователя без одного из обязательных полей')
    @pytest.mark.parametrize("missing_field", ["email", "password", "name"], ids=["no_email", "no_password", "no_name"])
    def test_create_user_with_missing_required_field(self, user_payload, missing_field, cleanup_user):
        api = StellarBurgerApi()
        with allure.step('Берем поля незарегистрированного курьера из фикстуры и копируем для безопасного изменения'):
            body = user_payload.copy()

        with allure.step('Удаляем одно из обязательных полей'):
            body.pop(missing_field)

        with allure.step('Отправляем POST-запрос только с одним обязательным полем'):
            response = api.create_user(json=body)

        with allure.step('Проверяем, что в ответ получена ошибка 403'):
            assert response.status_code == 403, f"{response.status_code}: {response.text}"

            message = response.json().get('message', '')
            assert "Email, password and name are required fields" in message