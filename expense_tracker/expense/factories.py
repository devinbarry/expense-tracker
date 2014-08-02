import factory
from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: "test%03d" % n)
    password = factory.PostGenerationMethodCall('set_password', 'password')
    email = factory.LazyAttribute(lambda u: "{0}@test.com".format(u.username))
