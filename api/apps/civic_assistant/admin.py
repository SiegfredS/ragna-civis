from django.contrib import admin

from .models import Prompt, PromptGroup, PromptGroupPrompt


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ("key", "prompt_type", "created", "modified")
    list_filter = ("prompt_type",)
    search_fields = ("key",)
    readonly_fields = ("created", "modified")


@admin.register(PromptGroup)
class PromptGroupAdmin(admin.ModelAdmin):
    list_display = ("key", "created", "modified")
    search_fields = ("key",)
    readonly_fields = ("created", "modified")


@admin.register(PromptGroupPrompt)
class PromptGroupPromptAdmin(admin.ModelAdmin):
    list_display = ("prompt_group", "ordering_index", "prompt", "created", "modified")
    search_fields = ("prompt_group__key", "prompt__key")
    readonly_fields = ("created", "modified")
    ordering = ("prompt_group_id", "ordering_index")
