from django.db import models

from recipes.models import Recipe


class Tag(models.Model):
    name = models.TextField(verbose_name="Имя тэга", max_length=200)
    color = models.CharField(verbose_name="Цвет", max_length=7)
    slug = models.SlugField(verbose_name="Тэг")

    def __str__(self):
        return self.name


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
