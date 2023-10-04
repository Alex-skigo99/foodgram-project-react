from django.db import models

from recipes.models import Recipe


class Ingredient(models.Model):
    name = models.TextField(verbose_name="Ингридиент", max_length=200)
    measurement_unit = models.TextField(
        verbose_name="Единица измерения", max_length=200
    )

    def __str__(self):
        return self.name


class IngredientsApplied(models.Model):
    inrgredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredients",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ing_recipes",
    )
    amount = models.IntegerField(verbose_name="Количество")

    def __str__(self):
        return f"{self.recipe} {self.inrgredient}"
