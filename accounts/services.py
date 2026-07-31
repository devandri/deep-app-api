from django.contrib.auth.hashers import make_password

from .models import User


def get_users():
    return User.objects.all()


def get_user(user_id: int):
    return User.objects.get(id=user_id)


def create_user(data):

    return User.objects.create(
        username=data.username,
        email=data.email,
        password=make_password(data.password),
    )


def update_user(user_id, data):

    user = User.objects.get(id=user_id)

    user.username = data.username
    user.email = data.email

    user.save()

    return user


def delete_user(user_id):

    user = User.objects.get(id=user_id)

    user.delete()