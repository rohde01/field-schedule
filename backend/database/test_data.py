from .constraints import Constraint

def get_test_constraints() -> list[Constraint]:
    """Returns a list of test constraints for development and testing."""
    return [
        Constraint(
            team_id=14,
            club_id=1,
            required_size='11v11',
            subfield_type='full',
            sessions=2,
            length=4
        ),
        Constraint(
            team_id=15,
            club_id=1,
            required_size='11v11',
            subfield_type='half',
            sessions=3,
            length=4
        )
    ]
