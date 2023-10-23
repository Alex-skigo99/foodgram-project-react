from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models


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
            models.UniqueConstraint(fields=["follower", "author"], name="follow")
        ]

    def clean(self):
        if self.follower == self.author:
            raise ValidationError({"errors": "нельзя подписаться на самого себя"})

    def __str__(self) -> str:
        return f"Follower: {str(self.follower)} / Author: {str(self.author)}"
