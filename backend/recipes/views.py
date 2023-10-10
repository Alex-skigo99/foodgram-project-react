from django.contrib.auth import get_user_model

# from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters  # , generics, permissions
from django_filters.rest_framework import DjangoFilterBackend

from .models import Recipe, Ingredient, Tag
from .serializers import RecipeSerializer, IngredientSerializer, TagSerializer

User = get_user_model()


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related("author")
    serializer_class = RecipeSerializer
    # permission_classes = (OwnerOrReadOnly,)
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filterset_fields = ("name", "author", "tags__slug")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # def get_queryset(self):
    #     queryset = self.queryset
    #     if self.request.query_params.get("is_favorited"):
    #         queryset = self.request.user.fav_recipes
    #     if self.request.query_params.get("is_in_shopping_cart"):
    #         queryset = queryset.filter(shop_users=self.request.user)
    #     return queryset

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
