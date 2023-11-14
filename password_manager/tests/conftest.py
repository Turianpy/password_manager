from pytest_factoryboy import register

from .factories import PSPFactory, UserFactory

register(UserFactory)
register(PSPFactory)
