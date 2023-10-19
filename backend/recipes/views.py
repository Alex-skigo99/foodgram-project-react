from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Sum
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from distutils.util import strtobool

# from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, status
from django_filters.rest_framework import (
    DjangoFilterBackend,
    AllValuesMultipleFilter,
    FilterSet,
    NumberFilter,
    TypedChoiceFilter,
)

from .models import Recipe, Ingredient, Tag, IngredientsApplied
from .permissions import OwnerOrReadOnly, ReadOnly
from .serializers import (
    RecipeSerializer,
    IngredientSerializer,
    TagSerializer,
    AddRecipeSerializer,
    AddFavoriteSerializer,
    AddShoppingCartSerializer,
    ShortRecipeResponseSerializer,
    IngredientCartSerializer,
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

    def fav_cart_logic(self, request, user, recipe, field_for_del, serializer):
        if request.method == "POST":
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                ShortRecipeResponseSerializer(recipe).data,
                status=status.HTTP_201_CREATED,
            )
        if not serializer.is_valid():
            field_for_del.remove(user)
            return Response(
                ShortRecipeResponseSerializer(recipe).data,
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {"errors": "этого рецепта нет в избранном"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=["post", "delete"])
    def favorite(self, request, pk):
        user = self.request.user
        serializer = AddFavoriteSerializer(data={"user": user.id, "recipe": pk})
        recipe = Recipe.objects.get(pk=pk)
        field_for_del = recipe.is_favorited
        return self.fav_cart_logic(request, user, recipe, field_for_del, serializer)

    @action(detail=True, methods=["post", "delete"])
    def shopping_cart(self, request, pk):
        user = self.request.user
        serializer = AddShoppingCartSerializer(data={"user": user.id, "recipe": pk})
        recipe = Recipe.objects.get(pk=pk)
        field_for_del = recipe.is_in_shopping_cart
        return self.fav_cart_logic(request, user, recipe, field_for_del, serializer)

    @action(detail=False, methods=["get"], permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = self.request.user
        recipes_in_cart = user.shop_recipe.all()
        queryset = Ingredient.objects.filter(
            ingredientsapplied__recipe__in=recipes_in_cart
        ).annotate(amount=Sum("ingredientsapplied__amount"))
        list_ing = queryset.values_list()
        with open("temp/Ingredients.txt", "w") as file:
            file.write("Список ингредиентов для покупки:" + "\n")
            for ing in list_ing:
                file.write(f"- {ing[1]} ({ing[2]}): {ing[3]}" + "\n")

        with open("temp/Ingredients.txt", "r") as file:
            response = HttpResponse(file, content_type="text/csv")
            response[
                "Content-Disposition"
            ] = "attachment; filename=temp/Ingredients.txt"
            return response

    def get_permissions(self):
        if self.action == "retrieve":
            return (ReadOnly(),)
        return super().get_permissions()


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
