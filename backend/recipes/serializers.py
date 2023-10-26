import base64
from django.contrib.auth import get_user_model
from django.db import transaction

# from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from rest_framework import serializers


from .models import Recipe, Ingredient, Tag, IngredientsApplied, TagsApplied

from users.serializers import CustomUserSerializer, ShortRecipeResponseSerializer

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


class AddTagsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())

    class Meta:
        model = TagsApplied
        fields = "id"


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
            return obj.image.url
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
    image = Base64ImageField(required=False, allow_null=True)

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
        fields_to_valid = ["ingredients", "tags", "image"]
        for field in fields_to_valid:
            if not field in data:
                raise serializers.ValidationError(f"данные не содержит поле {field}!")
        return data

    def validate_ingredients(self, value):
        if len(value) == 0:
            raise serializers.ValidationError("отсутствуют ингредиенты!")
        id_list = []
        for ing in value:
            amount = ing["amount"]
            if amount < 1:
                raise serializers.ValidationError("количество меньше допустимого!")
            id_list.append(ing["id"])
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
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            TagsApplied.objects.create(tag=tag, recipe=recipe)
        for ingredient in ingredients:
            amount = ingredient.pop("amount")
            current_ing = ingredient.pop("id")
            IngredientsApplied.objects.create(
                ingredient=current_ing, recipe=recipe, amount=amount
            )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        instance.image = validated_data.get("image", instance.image)
        instance.tags.clear()
        for tag in tags:
            TagsApplied.objects.create(tag=tag, recipe=instance)
        instance.ingredients.clear()
        for ingredient in ingredients:
            amount = ingredient.pop("amount")
            current_ing = ingredient.pop("id")
            IngredientsApplied.objects.create(
                ingredient=current_ing, recipe=instance, amount=amount
            )
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class AddFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe.is_favorited.through
        fields = ("customuser", "recipe")


class AddShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe.is_in_shopping_cart.through
        fields = ("customuser", "recipe")


class IngredientCartSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Ingredient
        fields = ("name", "measurement_unit", "amount")

    def get_amount(self, obj):
        return obj.amount
