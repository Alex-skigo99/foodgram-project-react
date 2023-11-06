from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import (
    CreateDestroySubscriptionView, CustomUserViewSet, SubscriptionViewSet,
)

from .views import IngredientsViewSet, RecipesViewSet, TagsViewSet

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
