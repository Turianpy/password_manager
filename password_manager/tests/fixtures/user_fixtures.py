import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def user(django_user_model):
    user = django_user_model.objects.create_user(
        username='test_user',
        email='testuser@random.org',
        is_active=True
    )
    user.set_password('test!passwordQSC')
    user.save()
    user.refresh_from_db()
    return user


@pytest.fixture
def inactive_user(user):
    user.is_active = False
    user.save()
    return user


@pytest.fixture
def user_token(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@pytest.fixture
def user_client(user_token):
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION='Bearer ' + user_token['access']
    )
    return client
