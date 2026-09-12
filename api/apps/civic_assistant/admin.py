from django.contrib import admin

from .models import Prompt, PromptGroup, PromptGroupPrompt


class PromptGroupPromptInline(admin.TabularInline):
    model = PromptGroupPrompt
    fk_name = "prompt_group"
    extra = 0
    show_change_link = True
    fields = ("prompt", "ordering_index")


class PromptGroupPromptForPromptInline(admin.TabularInline):
    model = PromptGroupPrompt
    fk_name = "prompt"
    extra = 0
    show_change_link = True
    fields = ("prompt_group", "ordering_index")


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ("key", "prompt_type", "created", "modified")
    list_filter = ("prompt_type",)
    search_fields = ("key",)
    readonly_fields = ("created", "modified")
    inlines = (PromptGroupPromptForPromptInline,)


@admin.register(PromptGroup)
class PromptGroupAdmin(admin.ModelAdmin):
    list_display = ("key", "created", "modified")
    search_fields = ("key",)
    readonly_fields = ("created", "modified")
    inlines = (PromptGroupPromptInline,)


@admin.register(PromptGroupPrompt)
class PromptGroupPromptAdmin(admin.ModelAdmin):
    list_display = ("prompt_group", "ordering_index", "prompt", "created", "modified")
    search_fields = ("prompt_group__key", "prompt__key")
    readonly_fields = ("created", "modified")
    ordering = ("prompt_group_id", "ordering_index")
