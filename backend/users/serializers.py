from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField, PrimaryKeyRelatedField
from djoser.serializers import UserSerializer


from recipes.models import Recipe
from .models import Subscription

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

    class Meta:
        model = User
        fields = (
            "email",
            "id",
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


class CustomUserCreateSerializer(UserSerializer):
    """Use in settings.DJOSER."""

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        read_only_fields = ("id",)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        del data["password"]
        return data


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.IntegerField(read_only=True, source="recipes.count")

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ("recipes", "recipes_count")

    def get_recipes(self, obj):
        limit = self.context["request"].query_params.get("recipes_limit")
        if limit == None:
            limit = RECIPES_LIMIT
        limit = int(limit)
        recipes = obj.recipes.all()[:limit]
        return ShortRecipeResponseSerializer(
            recipes, context=self.context, many=True
        ).data
