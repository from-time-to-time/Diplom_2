import pytest
from src.stellar_burger_api import StellarBurgerApi
import allure

class TestCreateOrder:
    @pytest.mark.parametrize(
        "auth, ingredients, expected_status_code, expected_success",
        [
            pytest.param(True, "valid", 200, True, id="With auth and valid ingredients"),
            pytest.param(False, "valid", 401, False, id="Without auth", marks=pytest.mark.xfail(reason="Known issue: API should return 401 for unauthorized request")),
            pytest.param(True, "empty", 400, False, id="Without ingredients"),
            pytest.param(True, "invalid", 500, False, id="With auth and invalid ingredients"),
        ]
    )
    @allure.title("Проверка создания заказа в разных сценариях")
    def test_create_order(
        self,
        register_new_user,
        valid_ingredients,
        invalid_ingredients,
        auth,
        ingredients,
        expected_status_code,
        expected_success,
        cleanup_user
    ):
        api_client = StellarBurgerApi()

        with allure.step("Формируем тело запроса"):
            headers = {"Authorization": register_new_user["access_token"]} if auth else {}

            if ingredients == "valid":
                body = {"ingredients": valid_ingredients}
            elif ingredients == "invalid":
                body = {"ingredients": invalid_ingredients}
            else:
                body = {"ingredients": []}

        with allure.step(f"Создаём заказ"):
            response = api_client.create_order(json=body, headers=headers)

        with allure.step("Проверяем код ответа"):
            assert response.status_code == expected_status_code, (
                f"Ожидали {expected_status_code}, получили {response.status_code}: {getattr(response, 'text', '')}"
            )
        with allure.step("Проверяем тело ответа"):
            if response.status_code < 500:
                data = response.json()
                assert data["success"] == expected_success, "Поле 'success' не соответствует ожиданию"

                if expected_success:
                    assert "order" in data, "Отсутствует ключ 'order'"
                    assert len(data["order"]["ingredients"]) > 0, "Пустой список ингредиентов"

                else:
                    allure.attach(
                        response.text,
                        name="Server error (HTML)",
                        attachment_type=allure.attachment_type.TEXT
                    )