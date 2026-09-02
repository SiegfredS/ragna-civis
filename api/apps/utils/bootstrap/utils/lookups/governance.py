from apps.governance.models import GovernanceBody, GovernancePosition


def get_governance_body(*, organization_slug: str, name: str) -> GovernanceBody:
    try:
        return GovernanceBody.objects.get(organization__slug=organization_slug, name=name)
    except GovernanceBody.DoesNotExist as error:
        raise ValueError(
            f"Bootstrap governance body {name!r} for organization {organization_slug!r} does not exist."
        ) from error
    except GovernanceBody.MultipleObjectsReturned as error:
        raise ValueError(
            f"Bootstrap governance body {name!r} for organization {organization_slug!r} is ambiguous."
        ) from error


def get_governance_position(*, organization_slug: str, governance_body_name: str, name: str) -> GovernancePosition:
    try:
        return GovernancePosition.objects.get(
            governance_body__organization__slug=organization_slug,
            governance_body__name=governance_body_name,
            name=name,
        )
    except GovernancePosition.DoesNotExist as error:
        raise ValueError(
            f"Bootstrap governance position {name!r} in body {governance_body_name!r} "
            f"for organization {organization_slug!r} does not exist."
        ) from error
    except GovernancePosition.MultipleObjectsReturned as error:
        raise ValueError(
            f"Bootstrap governance position {name!r} in body {governance_body_name!r} "
            f"for organization {organization_slug!r} is ambiguous."
        ) from error
