from faker import Faker

from .schemas import UserSchema


def generate_users(count: int):
    fake = Faker()

    users = []

    for _ in range(count):
        user = {
            'first_name' : fake.first_name(),
            'second_name': fake.last_name(),
            'password'   : fake.password(),
            'login'      : fake.unique.ascii_email()
        }
        users.append(UserSchema(**user))

    return users
