from models import User
from datetime import datetime
import factory
import random


class UserFactory(factory.DjangoModelFactory):
    id = factory.Sequence(lambda n: n + 1)
    gender = random.choice([1,2])
    registered_date = datetime.now()

    class Meta:
        model = User
