import allure
import pytest

from src.data import HTTPStatus


class TestCreateOrder:
    @pytest.mark.parametrize(
        "auth, ingredients_type, expected_status_code, expected_success",
        [
            pytest.param(True, "valid", HTTPStatus.OK, True, id="With auth and valid ingredients"),
            pytest.param(False, "valid", HTTPStatus.UNAUTHORIZED, False, id="Without auth",
                         marks=pytest.mark.xfail(reason="Known issue: API should return 401 for unauthorized request")),
            pytest.param(True, "empty", HTTPStatus.BAD_REQUEST, False, id="Without ingredients"),
            pytest.param(True, "invalid", HTTPStatus.INTERNAL_SERVER_ERROR, False,
                         id="With auth and invalid ingredients"),
        ]
    )
    @allure.title("Проверка создания заказа в разных сценариях")
    def test_create_order(
            self,
            make_order_request,
            auth,
            ingredients_type,
            expected_status_code,
            expected_success,
            cleanup_user
    ):
        response = make_order_request(auth=auth, ingredients_type=ingredients_type)

        with allure.step("Проверяем код ответа"):
            assert response.status_code == expected_status_code, (
                f"Ожидали {expected_status_code}, получили {response.status_code}: {getattr(response, 'text', '')}"
            )
        with allure.step("Проверяем тело ответа"):
            if response.status_code < HTTPStatus.INTERNAL_SERVER_ERROR:
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
