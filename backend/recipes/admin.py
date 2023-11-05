from django.contrib import admin

from .models import (
    Ingredient,
    IngredientsApplied,
    Recipe,
    Tag,
    Favorite,
    Shopping_cart,
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "slug", "color")
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(IngredientsApplied)
class IngredientsAppliedAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "ingredient",
        "recipe",
        "amount",
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "text", "author", "cooking_time", "image")
    search_fields = ("name",)
    list_filter = ("name", "author", "tags")
    empty_value_display = "-пусто-"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("author").prefetch_related(
            "ingredients", "tags"
        )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("pk", "customuser", "recipe")
    list_filter = ("customuser",)


@admin.register(Shopping_cart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("pk", "customuser", "recipe")
    list_filter = ("customuser",)
