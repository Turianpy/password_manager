import factory
from api.encryption import encrypt_password
from faker import Faker
from passwords.models import PasswordServicePair as PSP
from users.models import User

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.LazyAttribute(lambda _: fake.user_name())
    email = factory.LazyAttribute(lambda _: fake.email())
    password = factory.LazyAttribute(lambda _: fake.password())


class PSPFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PSP
        skip_postgeneration_save = True

    service_name = factory.LazyAttribute(lambda _: fake.word().lower())
    user = factory.SubFactory(UserFactory)

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return

        self.user.refresh_from_db()
        self.iv, self.encrypted_password = encrypt_password(
            extracted if extracted else fake.password(),
            self.user.password,
            self.user.salt
        )

        self.save()
