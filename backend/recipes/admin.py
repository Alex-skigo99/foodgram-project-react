from admin_auto_filters.filters import AutocompleteFilter
from django.contrib import admin

from .models import (
    Favorite, Ingredient, IngredientsApplied, Recipe, ShoppingCart, Tag,
)


class AuthorFilter(AutocompleteFilter):
    title = "author"
    field_name = "author"


class UserFilter(AutocompleteFilter):
    title = "user"
    field_name = "user"


class TagFilter(AutocompleteFilter):
    title = "tag"
    field_name = "tags"


class IngredientFilter(AutocompleteFilter):
    title = "ingredient"
    field_name = "ingredient"


class RecipeFilter(AutocompleteFilter):
    title = "recipe"
    field_name = "recipe"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "measurement_unit")
    list_display_links = ("pk", "name")
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "slug", "color")
    list_display_links = ("pk", "name")
    search_fields = ("name",)


@admin.register(IngredientsApplied)
class IngredientsAppliedAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "ingredient",
        "recipe",
        "amount",
    )
    list_display_links = ("pk", "ingredient")
    list_filter = [IngredientFilter, RecipeFilter]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("ingredient", "recipe")


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "text", "author", "cooking_time", "image")
    list_display_links = ("pk", "name", "text")
    search_fields = ("name",)
    list_filter = [AuthorFilter, TagFilter]
    empty_value_display = "-пусто-"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("author").prefetch_related(
            "ingredients", "tags"
        )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "recipe")
    list_display_links = ("pk", "user", "recipe")
    list_filter = [UserFilter]
    search_fields = ("user",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user", "recipe")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "recipe")
    list_display_links = ("pk", "user", "recipe")
    list_filter = [UserFilter]
    search_fields = ("user",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user", "recipe")
