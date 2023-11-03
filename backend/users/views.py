from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response

from .models import Subscription
from .serializers import SubscriptionSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    def get_permissions(self):
        if self.action == "me" and self.request.user.is_anonymous:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()


class SubscriptionViewSet(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        following = list(user.followers.all().values())
        following_list = []
        for follow in following:
            following_list.append(follow["author_id"])
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
                {"errors": "Нельзя подписаться на самого себя"},
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
        if Subscription.objects.filter(follower=user, author=author).delete():
            # instance = Subscription.objects.get(follower=user, author=author)
            # instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "вы не подписаны на этого автора"},
            status=status.HTTP_400_BAD_REQUEST,
        )
