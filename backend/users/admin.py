from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Subscription


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("pk", "follower", "author")
    search_fields = ("author",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("author", "follower")


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(CustomUser, UserAdmin)
