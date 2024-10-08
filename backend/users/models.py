from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models


class CustomUser(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        ("username"),
        max_length=150,
        unique=True,
        blank=False,
        help_text=("Required. 150 characters or fewer."),
        validators=[username_validator],
        error_messages={
            "unique": ("A user with that username already exists."),
        },
    )
    first_name = models.CharField(("first name"), max_length=150, blank=False)
    last_name = models.CharField(("last name"), max_length=150, blank=False)
    email = models.EmailField(
        ("email address"), max_length=254, blank=False, unique=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta(AbstractUser.Meta):
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self) -> str:
        return super().__str__()


User = get_user_model()


class Subscription(models.Model):
    """Подписка на автора."""

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="authors",
        verbose_name="Автор",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "author"], name="follow"
            )
        ]
        verbose_name = "подписка"
        verbose_name_plural = "подписки на авторов"

    def __str__(self) -> str:
        return f"Follower: {str(self.follower)} / Author: {str(self.author)}"

    def clean(self):
        if self.follower == self.author:
            raise ValidationError(
                {"errors": "нельзя подписаться на самого себя"}
            )
