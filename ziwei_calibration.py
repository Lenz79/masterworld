"""Calibration gate: never mark year-only mapping as validated at a solar/lunar boundary."""
def boundary_status(year, school=None, birth_date=None):
    if isinstance(year,bool) or not isinstance(year,int) or not 1900<=year<=2200:
        raise ValueError('year must be an integer 1900..2200')
    return {'year':year,'verified':False,'basis':'Gregorian-year approximation','boundary':'unknown','school':school,'requires':['birth_date','boundary convention','independent verified source'] }


def inspect_civil_date(value):
    """Validate ISO civil date only; do not assert any astrology year boundary."""
    from datetime import date
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError('civil_date must be ISO YYYY-MM-DD')
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError('civil_date must be ISO YYYY-MM-DD')
    return {'civil_date':value,'verified':False,'stem_branch_finalized':False,
            'requires_independent_ephemeris':True,
            'note':'Gregorian civil-date validation does not establish lunar or solar-term year boundary'}
