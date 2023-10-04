from django.db import models
from django.contrib.auth import get_user_model

from ingredients.models import Ingredient, IngredientsApplied
from tags.models import Tag, TagsApplied

User = get_user_model()


class Recipe(models.Model):
    name = models.TextField(verbose_name="Название", max_length=200)
    text = models.TextField(verbose_name="Текст")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    image = models.ImageField(upload_to="recipes/", null=True, blank=True)
    cooking_time = models.IntegerField(verbose_name="Время приготовления")
    ingredients = models.ManyToManyField(
        Ingredient, through="ingredients.models.IngredientsApplied"
    )
    tags = models.ManyToManyField(Tag, through="tags.models.TagsApplied")

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """Избранное."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="fav_users",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="fav_recipes",
    )

    def __str__(self):
        return f"{self.recipe} {self.user}"


class Shopping_cart(models.Model):
    """Список покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shop_users",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shop_recipes",
    )

    def __str__(self):
        return f"{self.recipe} {self.user}"
