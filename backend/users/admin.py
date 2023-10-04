from django.contrib import admin
from .models import Subscribtion


class SubscribtionAdmin(admin.ModelAdmin):
    list_display = ("pk", "follower", "following")
    search_fields = ("following",)
    empty_value_display = "-пусто-"


admin.site.register(Subscribtion, SubscribtionAdmin)
