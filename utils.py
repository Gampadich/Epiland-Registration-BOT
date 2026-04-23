from datetime import datetime
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU

def get_calculated_date(params):
    """Converting date_params from AI to the real date DD.MM.YYYY"""
    if not params:
        return None

    today = datetime.now()

    if params.get('exact_date'):
        return params['exact_date']

    if params.get('is_today'):
        return today.strftime("%d.%m.%Y")
    if params.get('is_tomorrow'):
        return (today + relativedelta(days=1)).strftime("%d.%m.%Y")

    days_map = {
        'monday': MO, 'tuesday': TU, 'wednesday': WE,
        'thursday': TH, 'friday': FR, 'saturday': SA, 'sunday': SU
    }

    day_name = params.get('day')

    if day_name in days_map:
        target_day = days_map[day_name]
        weeks = params.get('weeks_added', 0)
        res_date = today + relativedelta(weekday=target_day(0), weeks=weeks)
        return res_date.strftime("%d.%m.%Y")

    return None