import allure

from src.data import Messages as M
from src.data import HTTPStatus
from src.stellar_burger_api import StellarBurgerApi


class TestGetUserOrders:
    @allure.title('Проверка получения заказов пользователя с авторизацией')
    def test_get_user_orders_auth(self, register_new_user, valid_ingredients, cleanup_user):
        api = StellarBurgerApi()
        with allure.step("Получаем токен для авторизации из фикстуры"):
            assert register_new_user, "Фикстура не создала пользователя"
            access_token = register_new_user['access_token']

        with allure.step('Отправляем GET-запрос на получение заказов пользователя'):
            response = api.get_user_orders(headers={"Authorization": access_token})

        with allure.step("Проверяем, что возвращается пустой список заказов"):
            assert response.status_code == HTTPStatus.OK, f"Ожидали 200, получили {response.status_code}: {response.text}"
            body = response.json()
            assert body.get("success") is True, f"Ожидали success=true, получили: {body.get('success')}"
            assert body.get("orders") == []

        with allure.step('Отправляем POST-запрос на создание заказа'):
            payload = {"ingredients": valid_ingredients}
            response = api.create_order(json=payload, headers={"Authorization": access_token})
            assert response.status_code == HTTPStatus.OK, f"Ожидали 200, получили {response.status_code}: {getattr(response, 'text', '')}"

        with allure.step('Снова отправляем GET-запрос на получение заказов пользователя'):
            response = api.get_user_orders(headers={"Authorization": access_token})

        with allure.step("Проверяем, что в списке возвращается созданный заказ"):
            assert response.status_code == HTTPStatus.OK, f"Ожидали 200, получили {response.status_code}: {response.text}"
            data = response.json()
            assert data.get("success") is True, f"Ожидали success=true, получили: {data.get('success')}"

            assert len(data["orders"]) > 0, "Пустой список заказов"

    @allure.title('Проверка получения заказов пользователя без авторизации')
    def test_get_user_orders_without_auth(self, register_new_user, valid_ingredients, cleanup_user):
        api = StellarBurgerApi()
        with allure.step("Получаем токен для авторизации из фикстуры"):
            assert register_new_user, "Фикстура не создала пользователя"

        with allure.step('Отправляем GET-запрос на получение заказов пользователя'):
            response = api.get_user_orders()
        with allure.step('Проверяем, что в ответе получили ошибку 401'):
            assert response.status_code == HTTPStatus.UNAUTHORIZED

            message = response.json()['message']
            assert M.UNAUTHORISED in message
