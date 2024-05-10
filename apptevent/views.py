from datetime import date, datetime, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.safestring import mark_safe
from django.views.generic import ListView

from .forms import ApptEventForm, AppEventFilterForm
from .models import *
from .utils import Calendar

import calendar


# Create your views here.


class CalendarView(ListView):
    model = Appointment
    template_name = 'apptevent/eventcalendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context


def get_date(req_month):
    if req_month:
        year, month = (int(x) for x in req_month.split('-'))
        return date(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prevmonth = first - timedelta(days=1)
    month = 'month=' + str(prevmonth.year) + '-' + str(prevmonth.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    nextmonth = last + timedelta(days=1)
    month = 'month=' + str(nextmonth.year) + '-' + str(nextmonth.month)
    return month


def event(request, event_id=None):
    instance = Appointment()
    if event_id:
        instance = get_object_or_404(Appointment, pk=event_id)

    form = ApptEventForm(request.POST or None, instance=instance)
    if request.POST and form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('apptevent:calendar'))
    return render(request, 'apptevent/event.html', {'form': form})


def appointment_overview(request):
    mobile = request.GET.get('mobile')
    appointments = Appointment.objects.all()
    if mobile:
        appointments = appointments.filter(customer__mobile__icontains=mobile)
    context = {
        'app_total': Appointment.objects.all().count(),
        'app_lookup': appointments.count(),
        'form': AppEventFilterForm(),
        'appointments': appointments.order_by('-appTime')
    }
    return render(request, 'apptevent/overview.html', context)


class AppointmentAll(LoginRequiredMixin, ListView):
    template_name = 'apptevent/overview.html'
    login_url = 'manager:login'
    model = get_user_model()
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointments'] = Appointment.objects.order_by('appTime')
        return context


class AppointmentDoctor(ListView):
    queryset = Appointment.objects.select_related('doctor')
    template_name = 'apptevent/doctor.html'
    model = Appointment
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointments'] = Appointment.objects.order_by('doctor_id', 'appTime')
        return context
