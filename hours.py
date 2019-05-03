#! /usr/bin/env python

__author__ = 'Charles Ross'
__version__ = '1.0.0'
__author_email__ = 'chivalry@mac.com'

from datetime import datetime, date
from calendar import monthrange

import click


class Time(object):
    def __init__(self, minutes, hours=None, date=None):
        self.total_minutes = hours * 60 + minutes if hours else minutes

    @property
    def minutes(self):
        return self._total_minutes % 60

    @minutes.setter
    def minutes(self, minutes):
        self._total_minutes = minutes

    @property
    def hours(self):
        return self._total_minutes // 60


class Month(object):
    MAX_HOURS_PER_WEEK = 30
    MAX_MINUTES_PER_WEEK = 0
    MAX_HOURS_PER_MONTH = 120
    MAX_MINUTES_PER_MONTH = 1

    def __init__(self, month_number, hours, minutes):
        today = datetime.today()
        this_month = today.month
        self.year = today.year if month_number < this_month else today.year - 1
        self.start_weekday, self.days = monthrange(year, month)

        self.used_mins = self.mins_from_hrs_mins(hours, minutes)

        self.max_month = self.mins_from_hrs_mins(self.MAX_HOURS_PER_MONTH, MAX_MINUTES_PER_MONTH)
        self.max_week = self.mins_from_hrs_mins(self.MAX_HOURS_PER_WEEK, MAX_MINUTES_PER_WEEK)

    def mins_from_hrs_mins(hrs, mins):
        return hrs * 60 + mins


@click.command()
@click.option('-h', '--hours', default=0, required=True, prompt=True, type=int,
              help="Whole number of hours unavailable in the month\'s first week")
@click.option('-m', '--minutes', default=0, required=True, prompt=True, type=int,
              help="The number of minutes unavalable in the month's first week")
@click.option('-n', '--month', default=1, required=True, prompt=True, type=int,
              help='The month to calculate hours for')
def calculate_hours(hours, minutes, month):
    """Calculate the daily hours given the inputs."""
    today = datetime.today()
    this_month = today.month
    year = today.year if month < this_month else today.year - 1
    start_day, month_days = monthrange(year, month)

    used_week_mins = minutes_from_hrs_mins(hours, minutes)
    max_month = minutes_from_hrs_mins(MAX_HOURS_PER_MONTH, MAX_MINUTES_PER_MONTH)
    max_week = minutes_from_hrs_mins(MAX_HOURS_PER_WEEK, MAX_MINUTES_PER_WEEK)

    mins_per_day = max_month // month_days
    extra_mins = max_month - mins_per_day * month_days
    skip_days = month_days // extra_mins

    dates = [date(year, month, day) for day in range(1, month_days+1)]
    daily_times = [Time(date=date, minutes=mins_per_day) for date in dates]
    daily_mins = [{'date': date, 'mins': mins_per_day} for date in dates]

    for i in range(extra_mins):
        daily_mins[i * skip_days]['mins'] += 1

    start_week_days = (start_day * -1 - 1) % 7
    mins = [daily_min['mins'] for daily_min in daily_mins]
    first_week = used_week_mins + sum(mins[:start_week_days])
    i, j = 0, start_week_days
    while first_week > max_week:
        daily_mins[i]['mins'] -= 1
        daily_mins[j]['mins'] += 1
        i = i + 1 if i + 1 < start_week_days else 0
        j = j + 1 if j + 1 < month_days else start_week_days
        first_week -= 1

    for rec in daily_mins:
        if rec['date'].weekday() == 6:
            click.echo('\n')
        day = rec['date'].strftime('%a, %b %d').replace(' 0', ' ')
        click.echo('{}: {} hrs, {} mins'.format(day, rec['mins'] // 60, rec['mins'] % 60))

    total = sum([item['mins'] for item in daily_mins])
    click.echo('\ntotal: {} hrs, {} mins'.format(total//60, total%60))

if __name__ == '__main__':
    calculate_hours()
