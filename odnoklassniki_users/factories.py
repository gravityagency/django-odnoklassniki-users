from models import User
import factory
import random

class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User

    id = factory.Sequence(lambda n: n)
#    sex = random.choice([1,2])