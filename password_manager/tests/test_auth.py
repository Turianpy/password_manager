import pytest
from api.utils import generate_user_token
from django.core import mail

from .fixtures.user_fixtures import *  # noqa


@pytest.mark.django_db(transaction=True)
class TestAuth:

    signup_url = '/api/v1/auth/signup/'
    activate_url = '/api/v1/auth/activate/'
    token_url = '/api/v1/auth/token/'

    def test_signup(self, client):
        outbox_before = len(mail.outbox)
        data = {
            'username': 'test_user',
            'email': 'testuser@something.com',
            'password': 'test!passwordQSC'
        }
        response = client.post(self.signup_url, data=data)
        assert response.status_code == 201
        assert response.data['username'] == data['username']
        assert response.data['email'] == data['email']
        assert len(mail.outbox) == outbox_before + 1

    def test_signup_with_invalid_email(self, client):
        outbox_before = len(mail.outbox)
        data = {
            'username': 'test_user',
            'email': 'testuser',
            'password': 'test!passwordQSC'
        }
        response = client.post(self.signup_url, data=data)
        assert response.status_code == 400
        assert response.data['email'][0] == 'Enter a valid email address.'
        assert len(mail.outbox) == outbox_before

    def test_signup_with_invalid_password(self, client):
        outbox_before = len(mail.outbox)
        data = {
            'username': 'test_user',
            'email': 'testuser@something.com',
            'password': 'bad'
        }
        response = client.post(self.signup_url, data=data)
        assert response.status_code == 400
        assert response.data['password'][0] == (
            'This password is too short. '
            'It must contain at least 8 characters.'
        )
        assert len(mail.outbox) == outbox_before

    def test_signup_with_existing_credentials(self, client, user):
        outbox_before = len(mail.outbox)
        data = {
            'username': user.username,
            'email': user.email,
            'password': user.password,
        }
        response = client.post(self.signup_url, data=data)
        assert response.status_code == 400
        assert len(mail.outbox) == outbox_before
        assert outbox_before == len(mail.outbox)

    def test_activation(self, client, inactive_user):

        token = generate_user_token(inactive_user.email)
        url = f'{self.activate_url}?token={token}'
        response = client.get(url)
        assert response.status_code == 200
        assert response.data['message'] == 'Account successfully activated'

    def test_activation_invalid_token(self, client):
        url = f'{self.activate_url}?token=invalid_token'
        response = client.get(url)
        assert response.status_code == 400
        assert response.data['error'] == 'Invalid token'

    def test_activation_already_activated(self, user, client):
        token = generate_user_token(user.email)
        url = f'{self.activate_url}?token={token}'
        response = client.get(url)
        assert response.status_code == 400
        assert response.data['message'] == 'User already activated'

    def test_activation_user_does_not_exist(self, client, user_factory):
        user = user_factory.build()
        token = generate_user_token(user.email)
        url = f'{self.activate_url}?token={token}'
        response = client.get(url)
        assert response.status_code == 400
        assert response.data['error'] == 'User with given email not found'

    def test_activation_without_token(self, client):
        response = client.get(self.activate_url)
        assert response.status_code == 400
        assert response.data['error'] == 'Token not provided'

    def test_activation_link_expired(self, client, inactive_user):
        token = generate_user_token(inactive_user.email, -1)
        url = f'{self.activate_url}?token={token}'
        response = client.get(url)
        assert response.status_code == 400
        assert response.data['error'] == 'Activation link has expired'

    def test_get_token(self, user, client):
        data = {
            'email': user.email,
            'password': 'test!passwordQSC'
        }
        response = client.post(self.token_url, data=data)
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_get_token_user_does_not_exist(self, user_factory, client):
        data = {
            'email': 'idonexist@void.net',
            'password': 'test!passwordQSC'
        }
        response = client.post(self.token_url, data=data)
        assert response.status_code == 400
        assert response.data['non_field_errors'][0] == 'Invalid credentials'

    def test_get_token_with_invalid_credentials(self, user, client):
        data = {
            'email': user.email,
            'password': 'bad_password'
        }
        response = client.post(self.token_url, data=data)
        assert response.status_code == 400
        assert response.data['non_field_errors'][0] == 'Invalid credentials'

        data = {
            'email': 'bad_email',
            'password': 'test!passwordQSC'
        }
        response = client.post(self.token_url, data=data)
        assert response.status_code == 400
        assert response.data['email'][0] == 'Enter a valid email address.'

    def test_get_token_with_inactive_user(self, inactive_user, client):
        data = {
            'email': inactive_user.email,
            'password': 'test!passwordQSC'
        }
        response = client.post(self.token_url, data=data)
        assert response.status_code == 400
        expected_err = 'Account is not activated'
        assert response.data['non_field_errors'][0] == expected_err
