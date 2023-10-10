from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Ingredient(models.Model):
    name = models.TextField(verbose_name="Ингридиент", max_length=200)
    measurement_unit = models.TextField(
        verbose_name="Единица измерения", max_length=200
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.TextField(verbose_name="Имя тэга", max_length=200, unique=True)
    color = models.CharField(verbose_name="Цвет", max_length=7, unique=True)
    slug = models.SlugField(verbose_name="Тэг", unique=True)

    def __str__(self):
        return self.name


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
    ingredients = models.ManyToManyField(Ingredient, through="IngredientsApplied")
    tags = models.ManyToManyField(Tag, through="TagsApplied")

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


class TagsApplied(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="tags",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="tag_recipes",
    )

    def __str__(self):
        return f"{self.recipe} {self.tag}"


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
