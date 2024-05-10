from django import forms
from django.forms import DateInput, DateTimeInput

from manager.models import Customer, Employee
from .models import Appointment


class ApptEventForm(forms.ModelForm):
    name = \
        forms.CharField(
            label='Tên cuộc hẹn:',
            strip=True,
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mô tả'})
        )
    customer = \
        forms.ModelChoiceField(
            Customer.objects.all(),
            label='Khách hàng:',
            widget=forms.Select(attrs={'class': 'form-control'})
        )
    doctor = \
        forms.ModelChoiceField(
            Employee.objects.filter(department=3),
            label='Bác sĩ:',
            widget=forms.Select(attrs={'class': 'form-control'})
        )
    note = \
        forms.CharField(
            label='Ghi chú:',
            strip=True, required=False,
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ghi chú'})
        )
    appTime = \
        forms.DateTimeField(
            label='Thời gian:',
            widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%d %H:%M')
        )

    class Meta:
        model = Appointment
        fields = (
            'name', 'customer', 'doctor', 'note', 'appTime', 'status',
        )


class AppEventFilterForm(forms.Form):
    mobile: forms.CharField()

    """
    name = forms.CharField(label='Tên cuộc hẹn')
    customer = forms.CharField(label='Khach hang')
    class Meta:
      model = ApptEvent
      # datetime-local is a HTML5 input type, format to make date time show on fields
  
      widgets = {
        'appTime': DateTimeInput(
          attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'
        ),
      }
  
      fields = '__all__'
  
    def __init__(self, *args, **kwargs):
      super(ApptEventForm, self).__init__(*args, **kwargs)
      # input_formats parses HTML5 datetime-local input to datetime field
      self.fields['appTime'].input_formats = ('%Y-%m-%dT%H:%M',)
    """
