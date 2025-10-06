import pytest
from src.stellar_burger_api import StellarBurgerApi
import allure


class TestLogin:
    @allure.title('Проверка авторизации зарегистрированного пользователя')
    def test_login_existing_user(self, register_new_user, cleanup_user):
        api = StellarBurgerApi()
        with allure.step('Получаем из фикстуры данные созданного пользователя'):

            assert register_new_user, "Фикстура не создала пользователя"

            email, password = register_new_user['email'], register_new_user['password']

            body = {
                "email": email,
                "password": password
            }
        with allure.step('Отправляем POST-запрос с данными зарегистрированного пользователя'):
            response = api.login_user(json=body)

        with allure.step("Проверяем, что пользователь успешно залогинен: получен статус 200 и тело ответа"):
            assert response.status_code == 200, f"Ожидали 200, получили {response.status_code}: {response.text}"

            body = response.json()
            assert body.get("success") is True, f"Ожидали success=true, получили: {body.get('success')}"

            assert "email" in body["user"], "Нет email в ответе"

            assert "name" in body["user"], "Нет name в ответе"

            assert "accessToken" in body, "Нет accessToken в ответе"

            assert "refreshToken" in body, "Нет refreshToken в ответе"


    @allure.title('Проверка получения ошибки, если неправильно указать логин или пароль')
    @pytest.mark.parametrize("wrong_field", ["email", "password"])
    def test_login_user_with_wrong_data(self, register_new_user, wrong_field, cleanup_user):
        api = StellarBurgerApi()
        with allure.step('Берем из фикстуры логин и пароль зарегистрированного пользователя'):

            assert register_new_user, "Фикстура не создала пользователя"

            email, password = register_new_user['email'], register_new_user['password']

            body = {
                "email": email,
                "password": password
            }
        with allure.step('Искажаем значение поля'):
            body[wrong_field] = body[wrong_field] + "123"

        with allure.step('Отправляем POST-запрос с некорректным значением в поле'):
            response = api.login_user(json = body)

        with allure.step('Проверяем, что вернулась ошибка 401'):

            assert response.status_code == 401, f"{response.status_code}: {response.text}"

            message = response.json()['message']
            assert "email or password are incorrect" in message
