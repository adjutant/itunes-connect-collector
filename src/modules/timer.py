from datetime import datetime
from dateutil.parser import parse as parsetime
from dateutil.relativedelta import relativedelta


def get_timeid(timestring, timeformat):
    return parsetime(timestring).strftime(timeformat)


def get_nearest_months(amount):

    months = []
    now = datetime.now()

    tomonth = now.strftime('%Y%m')
    months.append(tomonth)

    if amount > 0:
        for i in range(amount, 0, -1):
            morrow = (now + relativedelta(months=i)).strftime('%Y%m')
            months.append(morrow)

    elif amount < 0:
        for i in range(amount, 0, 1):
            yestermonth = (now + relativedelta(months=i)).strftime('%Y%m')
            months.append(yestermonth)

    return months
