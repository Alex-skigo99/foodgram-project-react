from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Subscription, CustomUser

# class CustomUserAdmin(UserAdmin):
#     ...
#     fieldsets = UserAdmin.fieldsets + (
#         (None, {'fields': ('custom_field',)}),
#     )
#     add_fieldsets = UserAdmin.add_fieldsets + (
#         (None, {'fields': ('custom_field',)}),
#     )


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("pk", "follower", "author")
    search_fields = ("author",)


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(CustomUser, UserAdmin)
