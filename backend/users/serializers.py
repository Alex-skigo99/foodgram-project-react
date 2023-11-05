from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import Recipe

RECIPES_LIMIT = 6

User = get_user_model()


class ShortRecipeResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("id", "name", "image", "cooking_time")


class CustomUserSerializer(UserSerializer):
    """Use in settings.DJOSER."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return user.followers.filter(author=obj).exists()
        return False


class CustomUserCreateSerializer(UserCreateSerializer):
    """Use in settings.DJOSER."""

    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + (
            "username",
            "first_name",
            "last_name",
        )
        read_only_fields = ("id",)


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.IntegerField(
        read_only=True, source="recipes.count"
    )

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        limit = self.context["request"].query_params.get("recipes_limit")
        if limit is None:
            limit = RECIPES_LIMIT
        limit = int(limit)
        recipes = obj.recipes.all().order_by("-create")[:limit]
        return ShortRecipeResponseSerializer(
            recipes, context=self.context, many=True
        ).data
