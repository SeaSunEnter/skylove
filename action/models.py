from django.db import models
from django.urls import reverse
from djmoney.models.fields import MoneyField

from inventory.models import Asset
from manager.models import Customer, Service, Employee, User


# Create your models here.

class Treatment(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    consultant = models.ForeignKey(Employee, related_name='consultant', on_delete=models.CASCADE, null=True)
    expert = models.ForeignKey(Employee, related_name='expert', on_delete=models.CASCADE, null=True)
    doctor = models.ForeignKey(Employee, related_name='doctor', on_delete=models.CASCADE, null=True)
    done = models.BooleanField(default=False)
    date_apply = models.DateField(max_length=10)
    date_end = models.DateField(max_length=10, null=True)
    note = models.CharField(max_length=128)

    def __str__(self):
        return self.service.name

    def get_absolute_url(self):
        return reverse("action:treatment_overview", kwargs={"pk": self.pk})

    class Meta:
        db_table = 'Treatment'


class TreatmentImagesTmp(models.Model):
    image = models.ImageField(upload_to='Treatments')  # Adjust upload directory as needed

    def __str__(self):
        return self.image.name

    class Meta:
        db_table = 'TreatmentImagesTmp'


class TreatmentProcessImages(models.Model):
    treat = models.IntegerField()
    treat_pro = models.IntegerField()
    thumb = models.ImageField(blank=True, null=True, upload_to='Treatments')

    class Meta:
        db_table = 'TreatmentProcessImages'


class TreatmentProcess(models.Model):
    tag = models.IntegerField()
    date = models.DateField(max_length=10)
    status = models.TextField(max_length=128)
    tmp_thumb = models.ImageField(blank=True, null=True, upload_to='Treatments')

    def __str__(self):
        return str(self.tag)

    def get_absolute_url(self):
        return reverse("action:treatment_append", kwargs={'pk': self.pk})

    class Meta:
        db_table = 'TreatmentProcess'


class TreatmentAsset(models.Model):
    timeO = models.DateTimeField(auto_now_add=True)
    userID = models.SmallIntegerField()
    treat = models.IntegerField()
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()

    def __str__(self):
        return str(self.tag)

    def get_absolute_url(self):
        return reverse("action:treatment_asset", kwargs={'pk': self.pk})

    class Meta:
        db_table = 'TreatmentAsset'


class TreatmentAssetTmp(models.Model):
    asset_id = models.SmallIntegerField()
    asset_name = models.CharField(max_length=80)
    asset_quantity = models.SmallIntegerField()
    asset_price = MoneyField(max_digits=16, decimal_places=0, default_currency='VND', default=0)
    asset_sum = MoneyField(max_digits=16, decimal_places=0, default_currency='VND', default=0)

    class Meta:
        db_table = 'TreatmentAssetTmp'


class Consulting(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    consultor = models.ForeignKey(Employee, related_name='consultor', on_delete=models.CASCADE)
    date = models.DateField(max_length=10)
    request = models.CharField(max_length=128)
    medicalhistory = models.CharField(max_length=128, null=True)
    health = models.CharField(max_length=128, null=True)

    def __str__(self):
        return str(self.pk)

    def get_absolute_url(self):
        return reverse("action:consultant_view", kwargs={'pk': self.pk})

    class Meta:
        db_table = 'Consulting'


class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    time = models.DateTimeField(null=True)

    class Meta:
        db_table = 'Invoice'


class InvoiceCommon(models.Model):
    class Meta:
        abstract = True

    PAYKIND = (('tiền mặt', 'TIỀN MẶT'), ('chuyển khoản', 'CHUYỂN KHOẢN'), ('khác', 'KHÁC'))

    tag = models.IntegerField()
    time = models.DateTimeField(null=True)
    payby = models.CharField(choices=PAYKIND, max_length=12, default='TIỀN MẶT', null=True)


class InvoicePaid(InvoiceCommon):
    payed = MoneyField(max_digits=16, decimal_places=0, default_currency='VND', default=0)
    paid = MoneyField(max_digits=16, decimal_places=0, default_currency='VND', default=0)
    discount = MoneyField(max_digits=16, decimal_places=0, default_currency='VND', default=0)
    other = MoneyField(max_digits=16, decimal_places=0, default_currency='VND', default=0)
    note = models.TextField(max_length=128, null=True)

    def __str__(self):
        return str(self.tag)

    class Meta:
        db_table = 'InvoicePaid'


class InvoiceProcess(InvoiceCommon):
    description = models.TextField()
    paid = MoneyField(max_digits=16, decimal_places=0, default_currency='VND', default=0)
    payed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.tag)

    def get_absolute_url(self):
        return reverse("action:invoice_append", kwargs={'pk': self.pk})

    class Meta:
        db_table = 'InvoiceProcess'


class InvoiceFee(models.Model):
    tag = models.IntegerField()
    service = models.TextField(null=False)
    price = MoneyField(max_digits=16, decimal_places=0, default_currency='VND', default=0)

    def __str__(self):
        return str(self.tag)

    def get_absolute_url(self):
        return reverse("action:invoice_fee", kwargs={'pk': self.pk})

    class Meta:
        db_table = 'InvoiceFee'


class DebtTmp(models.Model):
    invoice = models.SmallIntegerField()
    customer_id = models.SmallIntegerField(null=True)
    customer_name = models.CharField(max_length=40, null=True)
    inv_fee_note = models.CharField(max_length=128, null=True)
    inv_fee_paid = MoneyField(max_digits=16, decimal_places=0, default_currency='VND', default=0, null=True)
    inv_pay_note = models.CharField(max_length=128, null=True)
    inv_pay_paid = MoneyField(max_digits=16, decimal_places=0, default_currency='VND', default=0, null=True)
    debt = MoneyField(max_digits=16, decimal_places=0, default_currency='VND', default=0, null=True)

    class Meta:
        db_table = 'DebtTmp'
