from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipes.views import RecipesViewSet, IngredientsViewSet, TagsViewSet
from users.views import (
    SubscriptionViewSet,
    CreateDestroySubscriptionView,
    CustomUserViewSet,
)

router = DefaultRouter()
router.register("recipes", RecipesViewSet, "recipes")
router.register("ingredients", IngredientsViewSet)
router.register("tags", TagsViewSet)
router.register("users", CustomUserViewSet)

urlpatterns = [
    path(
        "users/<int:user_id>/subscribe/",
        CreateDestroySubscriptionView.as_view(),
    ),
    path("auth/", include("djoser.urls.authtoken")),
    path("users/subscriptions/", SubscriptionViewSet.as_view()),
    path("", include(router.urls)),
]
