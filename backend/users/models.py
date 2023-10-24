from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    email = models.EmailField(unique=True)
    first_name = models.CharField("Имя", max_length=150)
    last_name = models.CharField("Фамилия", max_length=150)

    def __str__(self):
        return f'Пользователь {self.first_name}{self.last_name}'

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Follow(models.Model):
    follower = models.ForeignKey(
        CustomUser,
        verbose_name="Подписчик",
        related_name="follower",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        CustomUser,
        verbose_name="Автор",
        related_name="user",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
