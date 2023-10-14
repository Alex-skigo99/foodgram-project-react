from django.contrib.auth import get_user_model
from django.db import models

# from .models import Recipe


User = get_user_model()


# class Favorite(models.Model):
#     """Избранное."""

#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#     )
#     recipe = models.ForeignKey(
#         Recipe,
#         on_delete=models.CASCADE,
#     )

#     def __str__(self):
#         return f"{self.recipe} {self.user}"


# class Shopping_cart(models.Model):
#     """Список покупок."""

#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#     )
#     recipe = models.ForeignKey(
#         Recipe,
#         on_delete=models.CASCADE,
#     )

#     def __str__(self):
#         return f"{self.recipe} {self.user}"


class Subscription(models.Model):
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
