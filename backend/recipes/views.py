from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from distutils.util import strtobool

# from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters  # , generics, permissions
from django_filters.rest_framework import (
    DjangoFilterBackend,
    AllValuesMultipleFilter,
    FilterSet,
    NumberFilter,
    TypedChoiceFilter,
    ModelMultipleChoiceFilter,
)

from .models import Recipe, Ingredient, Tag
from .permissions import OwnerOrReadOnly
from .serializers import (
    RecipeSerializer,
    IngredientSerializer,
    TagSerializer,
    AddRecipeSerializer,
)

User = get_user_model()

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


class RecipesViewSet(viewsets.ModelViewSet):
    permission_classes = (OwnerOrReadOnly,)
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filterset_class = RecipeFilter

    def get_queryset(self):
        """Add fields is_fav & is_in_cart for authenticated"""
        user = self.request.user
        queryset = Recipe.objects.select_related("author").prefetch_related(
            "ingredients", "tags"
        )
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_fav=Exists(user.fav_recipe.filter(pk=OuterRef("pk")))
            ).annotate(is_in_cart=Exists(user.shop_recipe.filter(pk=OuterRef("pk"))))
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RecipeSerializer
        return AddRecipeSerializer

    # def get_permissions(self):
    #     if self.action == "retrieve":
    #         return (ReadOnly(),)
    #     return super().get_permissions()


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
