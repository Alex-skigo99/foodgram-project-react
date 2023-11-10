from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(verbose_name="Ингридиент", max_length=200)
    measurement_unit = models.CharField(
        verbose_name="Единица измерения", max_length=200
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Имя тэга", max_length=200, unique=True
    )
    color = models.CharField(verbose_name="Цвет", max_length=7, unique=True)
    slug = models.SlugField(verbose_name="Тэг", unique=True)

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(verbose_name="Название", max_length=200)
    text = models.TextField(verbose_name="Текст")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    image = models.ImageField(upload_to="recipes/", null=True, blank=False)
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=[
            MinValueValidator(1, "значение должно быть 1 - 9999"),
            MaxValueValidator(9999, "значение должно быть 1 - 9999"),
        ],
        help_text="значение должно быть 1 - 9999",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientsApplied",
        related_name="recipes",
        verbose_name="Ингредиенты",
        blank=False,
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        blank=False,
        verbose_name="Теги",
    )
    created = models.DateTimeField(
        verbose_name="Дата создания", auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class IngredientsApplied(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ings_recipe",
        verbose_name="Рецепт",
    )
    amount = models.SmallIntegerField(
        verbose_name="Количество",
        validators=[
            MinValueValidator(1, "значение должно быть 1 - 9999"),
            MaxValueValidator(9999, "значение должно быть 1 - 9999"),
        ],
        help_text="значение должно быть 1 - 9999",
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"

    def __str__(self):
        return f"{self.recipe} {self.ingredient}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="my_favorite",
        verbose_name="пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_favorites",
        verbose_name="рецепт",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="favorite_constraints"
            )
        ]
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"

    def __str__(self):
        return f"{self.user} {self.recipe}"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="my_shopping_cart",
        verbose_name="пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_shopping_carts",
        verbose_name="рецепт",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="cart_constraints"
            )
        ]
        verbose_name = "Рецепт в корзине"
        verbose_name_plural = "Рецепты в корзинах"

    def __str__(self):
        return f"{self.user} {self.recipe}"
