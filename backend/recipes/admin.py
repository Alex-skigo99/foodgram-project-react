from django.contrib import admin
from .models import (
    Recipe,
    Ingredient,
    IngredientsApplied,
    Tag,
    TagsApplied,
)


class IngAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("name",)


class TagAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "slug", "color")
    search_fields = ("name",)
    list_filter = ("name",)


class IngAppliedAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "ingredient",
        "recipe",
        "amount",
    )


class TagAppliedAdmin(admin.ModelAdmin):
    list_display = ("pk", "tag", "recipe")
    list_filter = ("recipe", "tag")


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "text", "author", "cooking_time", "image")
    search_fields = ("name",)
    list_filter = ("name", "author", "tags")
    empty_value_display = "-пусто-"


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngAdmin)
admin.site.register(IngredientsApplied, IngAppliedAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(TagsApplied, TagAppliedAdmin)
admin.site.register(Recipe.is_favorited.through)
admin.site.register(Recipe.is_in_shopping_cart.through)
# admin.site.register(Recipe.ingredients.through)
# admin.site.register(Recipe.tags.through)
