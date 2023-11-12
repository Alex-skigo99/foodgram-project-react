from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("pk", "follower", "author")
    search_fields = ("follower__email",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("author", "follower")


admin.site.register(CustomUser, UserAdmin)
