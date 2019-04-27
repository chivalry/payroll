#! /usr/bin/env python

import click
from datetime import datetime, date
from calendar import monthrange, setfirstweekday
import json


MAX_HOURS_PER_WEEK = 30
MAX_MINUTES_PER_WEEK = 0
MAX_HOURS_PER_MONTH = 120
MAX_MINUTES_PER_MONTH = 1


def minutes_from_hrs_mins(hrs, mins):
    return hrs * 60 + mins


@click.command()
@click.option('-r', '--hours', default=0, required=True, prompt=True, type=int,
              help="Whole number of hours unavailable in the month\'s first week")
@click.option('-m', '--minutes', default=0, required=True, prompt=True, type=int,
              help="The number of minutes unavalable in the month's first week")
@click.option('-o', '--month', default=1, required=True, prompt=True, type=int,
              help='The month to calculate hours for')
def calculate_hours(hours, minutes, month):
    """Calculate the daily hours given the inputs."""
    today = datetime.today()
    this_month = today.month
    year = today.year if month < this_month else today.year - 1
    start_day, month_days = monthrange(year, month)

    used_week_hrs = minutes_from_hrs_mins(hours, minutes)
    max_month = minutes_from_hrs_mins(MAX_HOURS_PER_MONTH, MAX_MINUTES_PER_MONTH)
    max_week = minutes_from_hrs_mins(MAX_HOURS_PER_WEEK, MAX_MINUTES_PER_WEEK)

    mins_per_day = max_month / month_days
    int_mins_per_day = int(mins_per_day)
    extra_mins = round((mins_per_day - int_mins_per_day) * month_days)
    skip_days = int(month_days / extra_mins)
    mins_per_day = int_mins_per_day

    dates = [date(year, month, day) for day in range(1, month_days+1)]
    daily_mins = [{'date': date, 'mins': mins_per_day} for date in dates]

    for i in range(extra_mins):
        daily_mins[i * skip_days]['mins'] += 1

    start_week_days = (start_day * -1 - 1) % 7
    mins = [daily_min['mins'] for daily_min in daily_mins]
    first_week = used_week_hrs + sum(mins[:start_week_days])
    i, j = 0, start_week_days + 0
    while first_week > max_week:
        daily_mins[i]['mins'] -= 1
        daily_mins[j]['mins'] += 1
        i = i + 1 if i + 1 < start_week_days else 0
        j = j + 1 if j + 1 < month_days else start_week_days + 0
        first_week -= 1

    daily_times = []
    for rec in daily_mins:
        daily_times.append({'date': rec['date'],
                            'hrs': rec['mins'] // 60,
                            'mins': rec['mins'] % 60})

    result = ['{}: {} hrs, {} mins'.format(rec['date'], rec['hrs'], rec['mins'])
            for rec in daily_times]
    click.echo('\n'.join(result))

if __name__ == '__main__':
    calculate_hours()
