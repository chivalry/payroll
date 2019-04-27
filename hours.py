#! /usr/bin/env python

import click
from datetime import datetime, date
from calendar import monthrange, setfirstweekday


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
    used_week_hrs = hours * 60 + minutes

    max_month = minutes_from_hrs_mins(MAX_HOURS_PER_MONTH, MAX_MINUTES_PER_MONTH)
    used_week = minutes_from_hrs_mins(MAX_HOURS_PER_WEEK, MAX_MINUTES_PER_WEEK)

    mins_per_day = max_month / month_days
    int_mins_per_day = int(mins_per_day)
    extra_mins = round((mins_per_day - int_mins_per_day) * month_days)
    skip_days = int(month_days / extra_mins)
    mins_per_day = int_mins_per_day

    hrs_per_day = int(mins_per_day / 60)
    mins_per_day = mins_per_day - (hrs_per_day * 60)

    dates = [date(year, month, day) for day in range(1, month_days+1)]
    daily_hours = [{'date': date, 'hrs': hrs_per_day, 'mins': mins_per_day} for date in dates]

    for i in range(extra_mins):
        itr = i * skip_days
        daily_hours[itr]['mins'] += 1
        if daily_hours[itr] == 60:
            daily_hrs[itr]['mins'] == 0
            daily_hrs[itr]['hrs'] += 1

    click.echo(str({
        'max_month': max_month,
        'hrs_per_day': hrs_per_day,
        'mins_per_day': mins_per_day,
        'extra_mins': extra_mins,
        'start_day': start_day,
        'skip_days': skip_days,
        }))

    result = ['{}: {} hrs, {} mins'.format(rec['date'], rec['hrs'], rec['mins'])
            for rec in daily_hours]
    click.echo('\n'.join(result))

if __name__ == '__main__':
    calculate_hours()
