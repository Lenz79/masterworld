"""Civil-date sanity checks only; never infer astrological year boundary."""
from datetime import date, timedelta
import calendar

def inspect_february_boundary(year):
    if isinstance(year,bool) or not isinstance(year,int) or not 1900<=year<=2200:
        raise ValueError('year must be integer 1900..2200')
    leap=calendar.isleap(year)
    feb_last=date(year,2,29 if leap else 28)
    march_first=date(year,3,1)
    assert feb_last+timedelta(days=1)==march_first
    return {'year':year,'leap_year':leap,'last_february_day':feb_last.isoformat(),
            'next_day':march_first.isoformat(),'civil_calendar_validated':True,
            'astrological_year_boundary_validated':False,
            'requires':['independent calendar reference','school-specific year-boundary convention']}
