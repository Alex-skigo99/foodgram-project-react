from django.contrib import admin
from .models import Subscription


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("pk", "follower", "following")
    search_fields = ("following",)


admin.site.register(Subscription, SubscriptionAdmin)
