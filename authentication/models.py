from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager

SECURITY_QUESTIONS = [
    ('mother_name', "What is your mother's maiden name?"),
    ('pet_name', "What was the name of your first pet?"),
    ('school_name', "What was the name of your primary school?"),
    ('city_born', "In which city were you born?"),
    ('favourite_food', "What is your favourite food?"),
]

class User(AbstractUser):
    username = None
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True)
    country_code = models.CharField(max_length=5, default='+91')
    email = models.EmailField(blank=True, null=True)
    security_question = models.CharField(
        max_length=50,
        choices=SECURITY_QUESTIONS,
        null=True,
        blank=True
    )
    security_answer = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return f"{self.name} ({self.country_code}{self.phone_number})"