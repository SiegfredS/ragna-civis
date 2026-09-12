from django.contrib import admin
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from apps.civic_assistant.admin import (
    PromptAdmin,
    PromptGroupAdmin,
    PromptGroupPromptForPromptInline,
    PromptGroupPromptInline,
)
from apps.civic_assistant.models import Prompt, PromptGroup, PromptGroupPrompt


def admin_request():
    request = RequestFactory().get("/admin/civic_assistant/promptgroup/")
    request.user = AnonymousUser()
    return request


class TestPromptAdmin:
    def test_includes_prompt_group_prompt_inline(self):
        model_admin = PromptAdmin(Prompt, admin.site)

        assert model_admin.inlines == (PromptGroupPromptForPromptInline,)
        assert PromptGroupPromptForPromptInline.model is PromptGroupPrompt

    def test_prompt_group_prompt_inline_exposes_editable_group_and_ordering(self):
        inline = PromptGroupPromptForPromptInline(Prompt, admin.site)
        formset = inline.get_formset(admin_request())

        assert inline.get_fields(admin_request()) == ("prompt_group", "ordering_index")
        assert "prompt_group" in formset.form.base_fields
        assert "ordering_index" in formset.form.base_fields
        assert inline.show_change_link is True


class TestPromptGroupAdmin:
    def test_includes_prompt_group_prompt_inline(self):
        model_admin = PromptGroupAdmin(PromptGroup, admin.site)

        assert model_admin.inlines == (PromptGroupPromptInline,)
        assert PromptGroupPromptInline.model is PromptGroupPrompt

    def test_prompt_group_prompt_inline_exposes_prompt_and_ordering(self):
        inline = PromptGroupPromptInline(PromptGroup, admin.site)
        formset = inline.get_formset(admin_request())

        assert inline.get_fields(admin_request()) == ("prompt", "ordering_index")
        assert "prompt" in formset.form.base_fields
        assert "ordering_index" in formset.form.base_fields
        assert inline.show_change_link is True
