import factory
from factory.django import DjangoModelFactory
from accounts.models import User, Company, CompanyDriver


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
