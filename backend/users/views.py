from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import generics, permissions, views, mixins, status

from recipes.models import Recipe
from .models import Subscription

# from .paginations import CustomPagination
# from .permissions import OwnerOrReadOnly, ReadOnly
from .serializers import SubscriptionSerializer  # CreateDestroySubscriptionSerializer

User = get_user_model()


class SubscriptionViewSet(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    # serializer_class = CustomUserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        following = list(user.followers.all().values())
        following_list = []
        for each in following:
            following_list.append(each["author_id"])
        queryset = User.objects.filter(id__in=following_list)
        return queryset


class CreateDestroySubscriptionView(views.APIView):
    def post(self, request, user_id):
        author = get_object_or_404(User, pk=user_id)
        user = self.request.user
        if (
            Subscription.objects.filter(follower=user, author=author).exists()
            or author == user
        ):
            return Response(
                {"errors": "вы уже подписаны или пытаетесь подписаться на самого себя"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Subscription.objects.create(follower=user, author=author)
        context = {}
        context["request"] = request
        serializer = SubscriptionSerializer(instance=author, context=context)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, user_id):
        author = get_object_or_404(User, pk=user_id)
        user = self.request.user
        if Subscription.objects.filter(follower=user, author=author).exists():
            instance = Subscription.objects.get(follower=user, author=author)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "вы не подписаны на этого автора"},
            status=status.HTTP_400_BAD_REQUEST,
        )
