from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Subscribtion(models.Model):
    """Подписка на автора."""

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers",
        verbose_name="Подписчик",
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followings",
        verbose_name="Автор",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["follower", "following"], name="follow")
        ]

    def __str__(self) -> str:
        return str(self.following)
