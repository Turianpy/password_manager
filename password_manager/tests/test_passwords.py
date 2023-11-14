import pytest

from .fixtures.user_fixtures import *  # noqa

from passwords.models import PasswordServicePair as PSP


@pytest.mark.django_db(transaction=True)
class TestPasswords:

    psp_url = '/api/v1/password/{service_name}'
    psp_list_url = '/api/v1/password/'

    def test_psp_create(self, user_client, user):
        data = {
            'password': 'verysecretpass'
        }
        service = 'yundex'

        response = user_client.post(
            self.psp_url.format(service_name=service),
            data=data
        )
        assert response.status_code == 201
        last = PSP.objects.last()
        assert last is not None
        assert last.service_name == service
        assert last.encrypted_password != data['password']
        assert last.user == user

    def test_psp_create_without_service_name(self, user_client):
        data = {
            'password': 'verysecretpass'
        }
        service = ''

        response = user_client.post(
            self.psp_url.format(service_name=service),
            data=data
        )
        assert response.status_code == 405
        assert response.data['detail'] == 'Method "POST" not allowed.'
        # this behavior is expected because if we ommit service name,
        # we are trying to POST to list endpoint, which doesn't allow POST

    def test_psp_create_without_password(self, user_client):
        service = 'yundex'
        response = user_client.post(
            self.psp_url.format(service_name=service),
            data={}
        )
        assert response.status_code == 400
        assert response.data['password'][0] == "This field is required."

    def test_psp_create_with_empty_password(self, user_client):
        data = {'password': ''}
        service = 'yundex'
        response = user_client.post(
            self.psp_url.format(service_name=service),
            data=data
        )
        assert response.status_code == 400
        assert response.data['password'][0] == "This field may not be blank."

    def test_psp_update(self, user_client, user, psp_factory):
        oldpass = 'oldpassword'
        psp = psp_factory.create(user=user, password=oldpass)
        data = {
            'password': 'newpassword'
        }
        service = psp.service_name
        response = user_client.post(
            self.psp_url.format(service_name=service),
            data=data
        )
        assert response.status_code == 201
        psp.refresh_from_db()
        newpass = psp.get_password()
        assert psp.encrypted_password != data['password']
        assert psp.user == user
        assert psp.service_name == service
        assert newpass != 'oldpassword'
        assert newpass == 'newpassword'

    def test_psp_retrieve(self, user_client, user, psp_factory):
        psp = psp_factory.create(user=user)
        service = psp.service_name
        response = user_client.get(
            self.psp_url.format(service_name=service)
        )
        assert response.status_code == 200
        assert response.data['password'] == psp.get_password()
        assert response.data['service_name'] == service

    def test_psp_list(self, user_client, user, psp_factory):
        psps = psp_factory.create_batch(10, user=user)
        response = user_client.get(self.psp_list_url)
        assert response.status_code == 200
        assert len(response.data) == len(psps)

    def test_psp_list_empty(self, user_client):
        response = user_client.get(self.psp_list_url)
        assert response.status_code == 200
        assert len(response.data) == 0

    def test_psp_list_with_filter(self, user_client, user, psp_factory):
        service_names = ['yundex', 'yundex2', 'yundex3', 'gugle', 'bong']
        for name in service_names:
            psp_factory.create(user=user, service_name=name)
        response = user_client.get(
            self.psp_list_url + '?service_name=yun'
        )
        assert response.status_code == 200
        assert len(response.data) == 3
        for psp in response.data:
            assert 'yun' in psp['service_name']

    def test_psp_get_only_own_passwords(
            self, user_client,
            user, user_factory,
            psp_factory
    ):
        another_user = user_factory.create()
        psp_factory.create_batch(10, user=another_user)
        another_users_passwords = [
            p.get_password() for p in PSP.objects.filter(user=another_user)
        ]
        psp_factory.create_batch(10, user=user)
        response = user_client.get(self.psp_list_url)
        assert response.status_code == 200
        assert len(response.data) == 10
        for psp in response.data:
            assert psp['password'] not in another_users_passwords
