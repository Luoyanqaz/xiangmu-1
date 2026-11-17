"""Shared maturity rules for scores on the 0–5 scale."""
from decimal import Decimal, InvalidOperation


MATURITY_LEVELS = (
    {'level': 'initial', 'name': '初始级', 'min': 0.0, 'max': 1.5, 'range': '[0.0, 1.5)'},
    {'level': 'growing', 'name': '成长级', 'min': 1.5, 'max': 3.0, 'range': '[1.5, 3.0)'},
    {'level': 'mature', 'name': '成熟级', 'min': 3.0, 'max': 4.0, 'range': '[3.0, 4.0)'},
    {'level': 'leading', 'name': '创新级', 'min': 4.0, 'max': 5.0, 'range': '[4.0, 5.0]'},
)
MATURITY_LABELS = {level['level']: level['name'] for level in MATURITY_LEVELS}


def determine_maturity_level(score):
    """Use inclusive lower bounds, including 5 in the final level; invalid scores have no level."""
    if score is None or isinstance(score, bool):
        return ''
    try:
        value = Decimal(str(score))
    except (InvalidOperation, ValueError, TypeError):
        return ''
    if not value.is_finite() or not Decimal('0') <= value <= Decimal('5'):
        return ''
    return next(level['level'] for level in reversed(MATURITY_LEVELS) if value >= level['min'])
