from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField, PrimaryKeyRelatedField
from djoser.serializers import UserSerializer


from .models import Subscription


User = get_user_model()


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


# class SubscriptionSerializer(CustomUserSerializer):


# class SubscriptionSerializer(serializers.ModelSerializer):
#     follower = serializers.StringRelatedField(
#         read_only=True, default=serializers.CurrentUserDefault()
#     )

#     class Meta:
#         model = Subscription
#         fields = ("follower", "following")

#         validators = [
#             serializers.UniqueTogetherValidator(
#                 queryset=Subscription.objects.all(),
#                 fields=("follower", "following"),
#                 message="Вы уже подписаны на этого автора.",
#             )
#         ]

#     def validate_following(self, value):
#         if value == self.context["request"].user:
#             raise serializers.ValidationError(
#                 "Нельзя подписаться на самого себя."
#             )
#         return value
