import django_filters
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils import timezone
from djmoney.models.fields import MoneyField


# Create your models here.

class User(AbstractUser):
    fullname = models.CharField(max_length=32)
    thumb = models.ImageField(blank=True, null=True, upload_to='User')

    class Meta:
        db_table = 'User'


class LoginLogs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    log_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user) + ': ' + str(self.log_time)

    class Meta:
        db_table = 'LoginLogs'


class Department(models.Model):
    name = models.CharField(max_length=64, null=False, blank=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("manager:dept_detail", kwargs={"pk": self.pk})

    class Meta:
        db_table = 'Department'


class HumanInfo(models.Model):
    class Meta:
        abstract = True

    LANGUAGE = (('english', 'ENGLISH'), ('tiếng việt', 'TIẾNG VIỆT'), ('french', 'FRENCH'))
    GENDER = (('nam', 'NAM'), ('nữ', 'NỮ'), ('khác', 'KHÁC'))
    humanID = models.CharField(
        max_length=12, unique=True, default=None, null=True, blank=True
    )
    gender = models.CharField(choices=GENDER, max_length=10)
    fullname = models.CharField(max_length=50, null=False)
    dob = models.DateField(max_length=10, null=True, blank=True)
    mobile = models.CharField(max_length=16, unique=True)
    email = models.EmailField(max_length=125, null=True, blank=True)
    address = models.TextField(max_length=100, null=True, blank=True)
    language = models.CharField(choices=LANGUAGE, max_length=10, default='english')
    thumb = models.ImageField(blank=True, null=True)
    nubank = models.CharField(max_length=16, null=True, blank=True, default=None)
    bank = models.CharField(max_length=32, null=True, blank=True, default=None)

    def save(self, **kwargs):
        self.humanID = self.humanID or None
        super().save(**kwargs)


class Employee(HumanInfo):
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    joined = models.DateTimeField(default=timezone.now)
    salary = models.CharField(max_length=16, default='00,000.00')
    thumb = models.ImageField(blank=True, null=True, upload_to='Employee')

    class Meta:
        db_table = 'Employee'

    def __str__(self):
        return self.fullname

    def get_absolute_url(self):
        return reverse("manager:employee_view", kwargs={"pk": self.pk})


class CustomerSource(models.Model):
    name = models.CharField(max_length=64, null=False, blank=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("manager:cust_src_all", kwargs={"pk": self.pk})

    class Meta:
        db_table = 'CustomerSource'


class Customer(HumanInfo):
    source = models.ForeignKey(CustomerSource, on_delete=models.SET_NULL, null=True)
    yob = models.IntegerField()
    thumb = models.ImageField(blank=True, null=True, upload_to='Customer')
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.fullname

    def get_absolute_url(self):
        return reverse("manager:customer_view", kwargs={"pk": self.pk})

    class Meta:
        db_table = 'Customer'


class CustomerFilter(django_filters.FilterSet):
    mobile = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Customer
        fields = ['fullname', 'mobile']


class Service(models.Model):
    name = models.CharField(max_length=64, unique=True)
    cost = MoneyField(max_digits=16, decimal_places=0, default_currency='VND', default=0)

    # timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Service'


class Birthday(models.Model):
    table_name = models.CharField(max_length=16)
    table_id = models.SmallIntegerField()

    class Meta:
        db_table = 'Birthday'
