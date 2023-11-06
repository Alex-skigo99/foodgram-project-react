from io import StringIO

from django.contrib.auth import get_user_model
from django.db.models import BooleanField, Exists, OuterRef, Sum, Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, Tag
from users.serializers import ShortRecipeResponseSerializer

from .filters import IngredientsFilter, RecipeFilter
from .permissions import OwnerOrReadOnly, ReadOnly
from .serializers import (
    AddFavoriteSerializer, AddRecipeSerializer, AddShoppingCartSerializer,
    IngredientSerializer, RecipeSerializer, TagSerializer,
)

User = get_user_model()


def shopping_cart_file(user):
    basket = user.shop_recipe.all()
    queryset = Ingredient.objects.filter(
        ingredientsapplied__recipe__in=basket
    ).annotate(amount=Sum("ingredientsapplied__amount"))
    file_buffer = StringIO()
    file_buffer.write("Список ингредиентов для покупки:\n")
    queryset_list = queryset.values_list()
    for ingredient in queryset_list:
        file_buffer.write(
            f"- {ingredient[1]} ({ingredient[2]}): {ingredient[3]}\n"
        )
    file_content = file_buffer.getvalue()
    file_buffer.close()
    return file_content


class RecipesViewSet(viewsets.ModelViewSet):
    permission_classes = (OwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        """Add fields is_fav & is_in_cart for authenticated."""
        user = self.request.user
        queryset = (
            Recipe.objects.select_related("author")
            .prefetch_related("ingredients", "tags")
            .order_by("-created")
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
        recipe = get_object_or_404(Recipe, pk=pk)
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
        return self.fav_cart_logic(
            request,
            AddFavoriteSerializer,
            pk,
        )

    @action(detail=True, methods=["post", "delete"])
    def shopping_cart(self, request, pk):
        return self.fav_cart_logic(
            request,
            AddShoppingCartSerializer,
            pk,
        )

    @action(
        detail=False, methods=["get"], permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = self.request.user
        response = HttpResponse(
            shopping_cart_file(user), content_type="text/plain"
        )
        response[
            "Content-Disposition"
        ] = "attachment; filename='ingredients.txt'"
        return response

    def get_permissions(self):
        if self.action == "retrieve":
            return (ReadOnly(),)
        return super().get_permissions()


class IngredientsViewSet(
    viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin
):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientsFilter

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        if not is_many:
            return super(IngredientsViewSet, self).create(
                request, *args, **kwargs
            )
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
