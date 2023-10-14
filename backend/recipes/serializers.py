import base64
from django.contrib.auth import get_user_model

# from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from rest_framework import serializers


from .models import Recipe, Ingredient, Tag, IngredientsApplied

from users.serializers import CustomUserSerializer

User = get_user_model()


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
        fields = "__all__"


class IngredientAppliedSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="inrgredient.id")
    name = serializers.CharField(read_only=True, source="inrgredient.name")
    measurement_unit = serializers.CharField(
        read_only=True, source="inrgredient.measurement_unit"
    )

    class Meta:
        model = IngredientsApplied
        fields = ("id", "name", "measurement_unit", "amount")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientAppliedSerializer(many=True, source="ings_recipe")
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    # image = Base64ImageField(required=False, allow_null=True)
    # image_url = serializers.SerializerMethodField(
    #     "get_image_url",
    #     read_only=True,
    # )

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
            return obj.image.url
        return None

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.is_fav
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.is_in_cart
        return False
