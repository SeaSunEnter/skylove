from django.db import models
from django.urls import reverse

from manager.models import Customer, Employee


# Create your models here.

class Appointment(models.Model):
    name = models.CharField(max_length=32)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Employee, on_delete=models.CASCADE)
    note = models.TextField(null=True)
    appTime = models.DateTimeField()
    STATUS_CHOICES = (
        ('0', 'Waiting'),
        ('1', 'Done'),
        ('2', 'Cancel'),
        ('3', 'Delay')
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='0')
    REMARK_CHOICES = (
        ('1', 'Accepted'),
        ('0', 'Rejected'),
    )
    remark = models.CharField(max_length=1, choices=REMARK_CHOICES)

    def __str__(self):
        return self.name

    @property
    def re_time(self):
        if self.appTime.hour > 12:
            stime = str(self.appTime.hour - 12) + ":" + str(self.appTime.minute) + " PM"
        else:
            stime = str(self.appTime.hour) + ":" + str(self.appTime.minute) + " AM"
        return stime

    @property
    def get_html_url(self):
        url = reverse('apptevent:event_edit', args=(self.id,))
        return f'<a href="{url}"> {self.re_time}: {self.name}</a>'

    def get_absolute_url(self):
        return reverse("apptevent:app_overview", kwargs={"pk": self.pk})

    class Meta:
        db_table = 'Appointment'
