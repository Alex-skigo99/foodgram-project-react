from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Sum, Value, BooleanField
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Recipe, Ingredient, Tag
from .permissions import OwnerOrReadOnly, ReadOnly
from .filters import IngredientsFilter, RecipeFilter
from .serializers import (
    RecipeSerializer,
    IngredientSerializer,
    TagSerializer,
    AddRecipeSerializer,
    AddFavoriteSerializer,
    AddShoppingCartSerializer,
    ShortRecipeResponseSerializer,
)

User = get_user_model()


class RecipesViewSet(viewsets.ModelViewSet):
    permission_classes = (OwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
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
            ).annotate(
                is_in_cart=Exists(user.shop_recipe.filter(pk=OuterRef("pk")))
            )
        else:
            queryset = queryset.annotate(
                is_fav=Value(False, output_field=BooleanField())
            ).annotate(is_in_cart=Value(False, output_field=BooleanField()))
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RecipeSerializer
        return AddRecipeSerializer

    def fav_cart_logic(self, request, serializer, pk):
        user = self.request.user
        # if not Recipe.objects.filter(pk=pk).exists():
        #     return Response(
        #         {"errors": "такого рецепта не существует"},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )
        recipe = get_object_or_404(
            Recipe, pk=pk
        )  # postman test required 400 !!!!!!! it's not right, imho
        serializer = serializer(data={"customuser": user.id, "recipe": pk})
        if request.method == "POST":
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                ShortRecipeResponseSerializer(recipe).data,
                status=status.HTTP_201_CREATED,
            )
        if not serializer.is_valid():
            if self.action == "favorite":
                recipe.is_favorited.remove(user)
            elif self.action == "shopping_cart":
                recipe.is_in_shopping_cart.remove(user)
            return Response(
                ShortRecipeResponseSerializer(recipe).data,
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {"error": "нельзя удалить отсутствующие в избранном рецепт"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=["post", "delete"])
    def favorite(self, request, pk):
        serializer = AddFavoriteSerializer
        return self.fav_cart_logic(
            request,
            serializer,
            pk,
        )

    @action(detail=True, methods=["post", "delete"])
    def shopping_cart(self, request, pk):
        serializer = AddShoppingCartSerializer
        return self.fav_cart_logic(
            request,
            serializer,
            pk,
        )

    @action(
        detail=False, methods=["get"], permission_classes=(IsAuthenticated,)
    )
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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientsFilter


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
