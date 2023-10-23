from django.contrib import admin
from .models import Subscription


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("pk", "follower", "author")
    search_fields = ("author",)


admin.site.register(Subscription, SubscriptionAdmin)
