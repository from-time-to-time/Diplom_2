import pytest
import random
from src.stellar_burger_api import StellarBurgerApi
import allure


class TestChangeData:
    @allure.title('Проверка изменения данных пользователя с авторизацией')
    @pytest.mark.parametrize("field", ["email", "password", "name"])
    def test_change_user_data_with_auth(self, register_new_user, field, cleanup_user):
        api = StellarBurgerApi()

        with allure.step('Получаем из фикстуры данные созданного пользователя'):
            assert register_new_user, "Фикстура не создала пользователя"
            access_token = register_new_user['access_token']

            body = {
                "email": register_new_user['email'],
                "password": register_new_user['password'],
                "name": register_new_user['name']
            }
        with allure.step('Готовим новое значение для поля'):
            if field == "email":
                local, domain = body["email"].split("@", 1)
                new_value = f"{local}+upd{random.randint(1000, 9999)}@{domain}"
            elif field == "password":
                new_value = body["password"] + "12345"
            else:
                new_value = body["name"] + "_upd"
            body[field] = new_value
        with allure.step('Отправляем PATCH-запрос с токеном и изменененным значением поля'):
             response = api.update_user_data(json=body, headers={'Authorization': access_token})
        assert response.status_code == 200, f"Ожидали 200, получили {response.status_code}: {getattr(response, 'text', '')}"
        data = response.json()
        assert data.get("success") is True, f"success != true: {data}"

        with allure.step('Проверяем, что изменение применилось'):
            if field in ("email", "name"):
                assert data["user"][field] == new_value, f"{field} не обновился: {data['user'][field]} != {new_value}"
            else:
                auth = api.login_user(json={"email": body["email"], "password": new_value})
                assert getattr(auth, "ok", False), f"Логин с новым паролем не удался"

    @allure.title('Проверка изменения данных пользователя без авторизации')
    @pytest.mark.parametrize("field", ["email", "password", "name"])
    def test_change_user_data_without_auth(self, register_new_user, field, cleanup_user):
        api = StellarBurgerApi()

        with allure.step('Получаем из фикстуры данные созданного пользователя'):
            assert register_new_user, "Фикстура не создала пользователя"

            access_token = register_new_user['access_token']

            body = {
                "email": register_new_user['email'],
                "password": register_new_user['password'],
                "name": register_new_user['name']
            }
        with allure.step('Готовим новое значение для поля'):
            if field == "email":
                local, domain = body["email"].split("@", 1)
                new_value = f"{local}+upd{random.randint(1000, 9999)}@{domain}"
            elif field == "password":
                new_value = body["password"] + "12345"
            else:
                new_value = body["name"] + "_upd"
            body[field] = new_value
        with allure.step('Отправляем PATCH-запрос без токена, с измененным значением поля'):
             response = api.update_user_data(json=body)
        assert response.status_code == 401, f"Ожидали 401, получили {response.status_code}: {getattr(response, 'text', '')}"
        data = response.json()
        assert data.get("success") is False, f"success != false: {data}"

        message = response.json()['message']
        assert "You should be authorised" in message

        with allure.step('Проверяем, что изменения НЕ применились'):
            if field == "password":

                bad = api.login_user(json={"email": body["email"], "password": new_value})
                assert not getattr(bad, "ok", False), f"Ожидали отказ в авторизации с новым паролем, но получили {getattr(bad, 'status_code')}"

                ok = api.login_user(json={"email": body["email"], "password": register_new_user["password"]})
                assert getattr(ok, "ok", False), "Старый пароль перестал работать"

            elif field == "email":

                bad = api.login_user(json={"email": new_value, "password": body["password"]})
                assert not getattr(bad, "ok", False), f"Ожидали отказ в авторизации с новым email, получили {getattr(bad, 'status_code')}"

                ok = api.login_user(json={"email": register_new_user["email"], "password": body["password"]})
                assert getattr(ok, "ok", False), "Старый email перестал работать"

            else:
                user_data = api.update_user_data(headers={'Authorization': access_token})
                assert getattr(user_data, "ok", False), f"Не получили данные пользователя: {getattr(user_data, 'status_code')} {getattr(user_data, 'text', '')}"
                current_name = user_data.json()["user"]["name"]
                assert current_name == register_new_user["name"], f"Имя изменилось, а не должно было: {current_name} != {register_new_user['name']}"
