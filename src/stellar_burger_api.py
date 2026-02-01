import allure
import requests

BASE_URL = "https://stellarburgers.education-services.ru/"


class StellarBurgerApi:
    def __init__(self, base_url=BASE_URL, default_headers=None):
        self.base_url = base_url
        self.default_headers = default_headers or {}

    @allure.step('POST create user')
    def create_user(self, **kwargs):
        return requests.post(f'{BASE_URL}/api/auth/register', **kwargs)

    @allure.step('POST login user')
    def login_user(self, **kwargs):
        return requests.post(f'{BASE_URL}/api/auth/login', **kwargs)

    @allure.step('PATCH update user')
    def update_user_data(self, **kwargs):
        return requests.patch(f'{BASE_URL}/api/auth/user', **kwargs)

    @allure.step('POST create order')
    def create_order(self, **kwargs):
        return requests.post(f'{BASE_URL}/api/orders', **kwargs)

    @allure.step('GET user orders')
    def get_user_orders(self, **kwargs):
        return requests.get(f'{BASE_URL}/api/orders', **kwargs)

    @allure.step('DELETE user')
    def delete_user(self, **kwargs):
        return requests.delete(f'{BASE_URL}/api/auth/user', **kwargs)
