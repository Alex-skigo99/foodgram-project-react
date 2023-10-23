from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipes.views import RecipesViewSet, IngredientsViewSet, TagsViewSet
from users.views import SubscriptionViewSet, CreateDestroySubscriptionView

router = DefaultRouter()
router.register("recipes", RecipesViewSet, "recipes")
router.register("ingredients", IngredientsViewSet)
router.register("tags", TagsViewSet)
# router.register(r"users/(?P<user_id>\d+)/subscribe", CreateDestroySubscriptionViewSet)

urlpatterns = [
    path("users/<int:user_id>/subscribe/", CreateDestroySubscriptionView.as_view()),
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
    path("users/subscriptions/", SubscriptionViewSet.as_view()),
    path("", include("djoser.urls")),
]
