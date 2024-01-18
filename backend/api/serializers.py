import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientsApplied,
    Recipe,
    ShoppingCart,
    Tag,
)
from rest_framework import serializers

from foodgram.settings import HTTP_HOST

User = get_user_model()

RECIPES_LIMIT = 6


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientsAppliedSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(read_only=True, source="ingredient.name")
    measurement_unit = serializers.CharField(
        read_only=True, source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientsApplied
        fields = ("id", "name", "measurement_unit", "amount")


class AddIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=0)

    class Meta:
        model = IngredientsApplied
        fields = ("id", "amount")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


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


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientsAppliedSerializer(many=True, source="ings_recipe")
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_image(self, obj):
        if obj.image:
            return HTTP_HOST + "/".join(obj.image.url.split("/")[3:])
        return None

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        if user.is_authenticated and self.context["request"].method == "GET":
            return obj.is_fav
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        if user.is_authenticated and self.context["request"].method == "GET":
            return obj.is_in_cart
        return False


class AddRecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientsSerializer(many=True)
    tags = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())
    )
    cooking_time = serializers.IntegerField(min_value=1)
    image = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            "author",
            "name",
            "text",
            "cooking_time",
            "image",
            "ingredients",
            "tags",
        )

    def validate(self, data):
        fields_to_valid = ["ingredients", "tags"]
        fields_missing = []
        for field in fields_to_valid:
            if field not in data:
                fields_missing.append(field)
        if fields_missing:
            raise serializers.ValidationError(
                f"данные не содержат поля {fields_missing}!"
            )
        return data

    def validate_ingredients(self, value):
        if len(value) == 0:
            raise serializers.ValidationError("отсутствуют ингредиенты!")
        id_list = []
        for ingredient in value:
            amount = ingredient["amount"]
            if amount < 1:
                raise serializers.ValidationError("количество меньше допустимого!")
            id_list.append(ingredient["id"])
        if len(id_list) > len(set(id_list)):
            raise serializers.ValidationError("ингредиенты повторяются!")
        return value

    def validate_tags(self, value):
        if len(value) == 0:
            raise serializers.ValidationError("отсутствуют теги!")
        if len(value) > len(set(value)):
            raise serializers.ValidationError("теги повторяются!")
        return value

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        recipe = super().create(validated_data)
        for ingredient in ingredients:
            amount = ingredient.pop("amount")
            ingredient_id = ingredient.pop("id")
            IngredientsApplied.objects.create(
                ingredient=ingredient_id, recipe=recipe, amount=amount
            )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredients")
        instance.ingredients.clear()
        for ingredient in ingredients:
            amount = ingredient.pop("amount")
            ingredient_id = ingredient.pop("id")
            IngredientsApplied.objects.create(
                ingredient=ingredient_id, recipe=instance, amount=amount
            )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class AddFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ("user", "recipe")
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=("user", "recipe"),
            )
        ]


class AddShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=("user", "recipe"),
            )
        ]


class IngredientCartSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Ingredient
        fields = ("name", "measurement_unit", "amount")

    def get_amount(self, obj):
        return obj.amount


class ShortRecipeResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("id", "name", "image", "cooking_time")


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
    recipes_count = serializers.IntegerField(read_only=True)

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
        recipes = obj.recipes.all().order_by("-created")[:limit]
        return ShortRecipeResponseSerializer(
            recipes, context=self.context, many=True
        ).data
