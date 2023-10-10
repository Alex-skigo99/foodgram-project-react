from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipes.views import RecipesViewSet, IngredientsViewSet, TagsViewSet

router = DefaultRouter()
router.register("recipes", RecipesViewSet)
router.register("ingredients", IngredientsViewSet)
router.register("tags", TagsViewSet)
# router.register(
#     r"posts/(?P<post_id>\d+)/comments", CommentViewSet, basename="comments"
# )


urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
    path("", include("djoser.urls")),
]
