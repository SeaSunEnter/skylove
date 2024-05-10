from datetime import datetime
from calendar import HTMLCalendar
from .models import Appointment


class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    # formats a day as a td
    # filter events by day
    def formatday(self, day, events):
        events_per_day = events.filter(appTime__day=day)
        dlink = ''
        for event in events_per_day:
            dlink += f'<li> {event.get_html_url} '
            match event.status:
                case '1':
                    # Done
                    dlink += '<i class="mdi mdi-check"></i>'

                case '2':
                    # Cancel
                    dlink += '<i class="mdi mdi-cancel"></i>'

                case '3':
                    # Delay
                    dlink += '<i class="mdi mdi-watch-import"></i>'

                case _:
                    # Waiting
                    dlink += '<i class="mdi mdi-clock"></i>'

            dlink += '</li>'

        dateistoday = "td"
        curday = str(day)
        if (datetime.now().year == self.year) and (datetime.now().month == self.month) and (datetime.now().day == day):
            curday += " [Hôm nay]"
            dateistoday = "td style='background-color:LightGreen'"

        if day != 0:
            if datetime(self.year, self.month, day).isoweekday() == 6:
                return f"<{dateistoday}>" \
                       f"<span class='date'; style='color:Fuchsia'>" \
                       f"{curday}" \
                       f"</span>" \
                       f"<ul> {dlink} </ul>" \
                       f"</td>"
            else:
                if datetime(self.year, self.month, day).isoweekday() == 7:
                    return f"<{dateistoday}>" \
                           f"<span class='date'; style='color:Red'>" \
                           f"{curday}" \
                           f"</span>" \
                           f"<ul> {dlink} </ul>" \
                           f"</td>"
                else:
                    return f"<{dateistoday}>" \
                           f"<span class='date'; style='color:Black'>" \
                           f"{curday}" \
                           f"</span>" \
                           f"<ul> {dlink} </ul>" \
                           f"</td>"
        else:
            return '<td></td>'

    # formats a week as a table_row
    def formatweek(self, theweek, events):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, events)
        return f'<tr> {week} </tr>'

    # formats a month as a table
    # filter events by year and month
    def formatmonth(self, withyear=True):
        events = Appointment.objects.filter(appTime__year=self.year, appTime__month=self.month)

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, events)}\n'
        return cal

    def formatweekheader(self):
        return f'<th style="background-color:LightGrey"> Thứ Hai </th>' \
               f'<th style="background-color:LightGrey"> Thứ Ba </th>' \
               f'<th style="background-color:LightGrey"> Thứ Tư </th>' \
               f'<th style="background-color:LightGrey"> Thứ Năm </th>' \
               f'<th style="background-color:LightGrey"> Thứ Sáu </th>' \
               f'<th style="background-color:LightGrey"> <span style="color:Fuchsia"> Thứ Bảy </span></th>' \
               f'<th style="background-color:LightGrey"> <span style="color:Red">Chủ Nhật </span></th>'

    def formatmonthname(self, theyear: int, themonth: int, withyear: bool = ...):
        return f"<tr><th><span class='month'>Tháng {themonth} / {theyear}</span><th></tr>"
