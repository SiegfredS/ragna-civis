from django.contrib import admin
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from apps.governance.models import GovernanceBody, GovernancePositionAssignment
from apps.organizations.admin import (
    ChildOrganizationInline,
    GovernanceBodyInline,
    GovernancePositionAssignmentInline,
    OrganizationAdmin,
    OrganizationMembershipAdmin,
    OrganizationMembershipInline,
    ProjectInline,
)
from apps.organizations.models import Organization, OrganizationMembership
from apps.projects.models import Project


def admin_request():
    request = RequestFactory().get("/admin/organizations/organization/")
    request.user = AnonymousUser()
    return request


class TestOrganizationAdmin:
    def test_includes_related_editors(self):
        model_admin = OrganizationAdmin(Organization, admin.site)

        assert model_admin.inlines == (
            OrganizationMembershipInline,
            ChildOrganizationInline,
            GovernanceBodyInline,
            ProjectInline,
        )

    def test_related_editors_use_the_expected_foreign_keys(self):
        assert (OrganizationMembershipInline.model, OrganizationMembershipInline.fk_name) == (
            OrganizationMembership,
            "organization",
        )
        assert (ChildOrganizationInline.model, ChildOrganizationInline.fk_name) == (Organization, "parent")
        assert (GovernanceBodyInline.model, GovernanceBodyInline.fk_name) == (GovernanceBody, "organization")
        assert (ProjectInline.model, ProjectInline.fk_name) == (Project, "organization")

    def test_related_editors_expose_editable_fields_and_change_links(self):
        expected_fields = {
            OrganizationMembershipInline: ("user_profile", "role"),
            ChildOrganizationInline: ("name", "slug", "organization_type"),
            GovernanceBodyInline: ("name", "body_type"),
            ProjectInline: ("title", "slug", "status", "start_date", "end_date"),
        }

        for inline_class, fields in expected_fields.items():
            inline = inline_class(Organization, admin.site)
            formset = inline.get_formset(admin_request())

            assert inline.get_fields(admin_request()) == fields
            assert set(fields).issubset(formset.form.base_fields)
            assert inline.show_change_link is True


class TestOrganizationMembershipAdmin:
    def test_includes_position_assignment_editor(self):
        model_admin = OrganizationMembershipAdmin(OrganizationMembership, admin.site)

        assert model_admin.inlines == (GovernancePositionAssignmentInline,)
        assert GovernancePositionAssignmentInline.model is GovernancePositionAssignment
        assert GovernancePositionAssignmentInline.fk_name == "membership"
