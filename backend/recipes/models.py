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
    ingredients = models.ManyToManyField(
        Ingredient, through="IngredientsApplied", related_name="ing_recipes"
    )
    tags = models.ManyToManyField(
        Tag, through="TagsApplied", related_name="tag_recipes"
    )
    is_favorited = models.ManyToManyField(
        User, db_table="Favorite", related_name="fav_recipe"
    )
    is_in_shopping_cart = models.ManyToManyField(
        User, db_table="Shopping_cart", related_name="shop_recipe"
    )

    def __str__(self):
        return self.name


class IngredientsApplied(models.Model):
    inrgredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ings_recipe"
    )
    amount = models.IntegerField(verbose_name="Количество")

    def __str__(self):
        return f"{self.recipe} {self.inrgredient}"


class TagsApplied(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.recipe} {self.tag}"
