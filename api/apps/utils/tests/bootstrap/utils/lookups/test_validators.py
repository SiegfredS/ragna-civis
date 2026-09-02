import pytest

from apps.governance.choices import GovernanceBodyType
from apps.utils.bootstrap.utils.lookups.validators import validate_choice


def test_validate_choice_returns_valid_value():
    assert (
        validate_choice(value=GovernanceBodyType.COUNCIL, choices=GovernanceBodyType, field_name="body type")
        == GovernanceBodyType.COUNCIL
    )


def test_validate_choice_rejects_invalid_value():
    with pytest.raises(ValueError, match="Invalid body type"):
        validate_choice(value="invalid", choices=GovernanceBodyType, field_name="body type")
