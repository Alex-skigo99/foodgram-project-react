# from django.shortcuts import get_object_or_404
# from rest_framework import filters, generics, permissions, viewsets

# from posts.models import Comment, Follow, Group, Post

# from .paginations import CustomPagination
# from .permissions import OwnerOrReadOnly, ReadOnly
# from .serializers import (
#     CommentSerializer,
#     FollowSerializer,
#     GroupSerializer,
#     PostSerializer,
# )


# class SubscribtionViewSet(generics.ListCreateAPIView):
#     serializer_class = FollowSerializer
#     permission_classes = (permissions.IsAuthenticated,)
#     filter_backends = (filters.SearchFilter,)
#     search_fields = ("following__username",)

#     def get_queryset(self):
#         queryset = Follow.objects.filter(
#             user=self.request.user
#         ).select_related("following")
#         return queryset

#     def perform_create(self, serializer):
#         author = get_object_or_404(
#             User, username=self.request.data["following"]
#         )
#         serializer.save(user=self.request.user, following=author)
