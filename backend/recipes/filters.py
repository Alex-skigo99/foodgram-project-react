from distutils.util import strtobool
from django_filters.rest_framework import (
    AllValuesMultipleFilter,
    FilterSet,
    NumberFilter,
    TypedChoiceFilter,
    CharFilter,
)

from recipes.models import Ingredient, Recipe

BOOLEAN_CHOICES = (
    (0, "False"),
    (1, "True"),
)


class RecipeFilter(FilterSet):
    tags = AllValuesMultipleFilter(field_name="tags__slug")
    author = NumberFilter(lookup_expr="id__exact")
    is_favorited = TypedChoiceFilter(
        field_name="is_fav", choices=BOOLEAN_CHOICES, coerce=strtobool
    )
    is_in_shopping_cart = TypedChoiceFilter(
        field_name="is_in_cart", choices=BOOLEAN_CHOICES, coerce=strtobool
    )

    class Meta:
        model = Recipe
        fields = []


class IngredientsFilter(FilterSet):
    name = CharFilter(lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = []
