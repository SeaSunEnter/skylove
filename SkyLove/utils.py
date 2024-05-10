import datetime
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.urls import reverse

from xhtml2pdf import pisa

from manager.models import Birthday, Customer, Employee


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()

    # pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result, encoding='UTF-8')
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result, encoding='UTF-8')

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def check_birthday():
    today = datetime.datetime.now()
    Birthday.objects.all().delete()
    i = 0
    for customer in Customer.objects.all().filter(deleted=False):
        if customer.dob is not None:
            # if (customer.dob.month == today.month) and (customer.dob.day == today.day):
            if customer.dob.month == today.month:
                i += 1
                Birthday.objects.create(
                    id=i,
                    table_name='Customer',
                    table_id=customer.id
                )

    for employee in Employee.objects.all():
        if employee.dob is not None:
            # if (employee.dob.month == today.month) and (employee.dob.day == today.day):
            if employee.dob.month == today.month:
                i += 1
                Birthday.objects.create(
                    id=i,
                    table_name='Employee',
                    table_id=employee.id
                )
    return
