import csv
import datetime
import io
import os
import unicodedata

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Sum
from django.http import FileResponse, HttpResponse
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
# from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from SkyLove.utils import render_to_pdf
from action.forms import TreatmentForm, TreatmentFilterForm, TreatmentAppendForm, ConsultingFilterForm, \
    ConsultingForm, TreatmentProcessForm, InvoiceForm, InvoiceAppendForm, InvoiceFilterForm, InvoiceProcessForm, \
    TreatmentAssetForm, InvoiceFeeForm, InvoiceAppendFeeForm, InvoiceFeeCopyForm
from action.models import Treatment, TreatmentProcess, Consulting, TreatmentProcessImages, Invoice, InvoiceProcess, \
    TreatmentAsset, InvoiceFee, DebtTmp, TreatmentAssetTmp, TreatmentImagesTmp
from inventory.models import Inventory
from manager.models import Customer, Service
from django.views.decorators.csrf import csrf_protect


@csrf_protect
def upload_images(request, pk):
    treat_pro = TreatmentProcess.objects.get(pk=pk)
    treat = Treatment.objects.get(id=str(treat_pro.tag))
    cust_name = str(treat.customer.pk)

    if request.method == 'POST':
        images = request.FILES.getlist('images')

        # for image in images:
        for index, image in enumerate(images):
            file_name, file_extension = os.path.splitext(image.name)
            new_filename = f"{cust_name}_{pk}_{index}{file_extension}"  # Replace with your desired naming convention
            image.name = new_filename
            TreatmentImagesTmp.objects.create(image=image)

        return redirect('action:treatment_pro_prev_img', pk)  # Redirect to preview page

    context = {
        'treat_pro': pk
    }
    return render(request, 'action/treatmentpro/upload_images.html', context)


@csrf_protect
def image_preview(request, pk):
    images = TreatmentImagesTmp.objects.all()
    if request.method == 'POST':
        treat_pro = TreatmentProcess.objects.get(pk=pk)
        # treat = Treatment.objects.get(id=str(treat_pro.tag))
        for image in images:
            st = image.image.url
            st = st.replace("/media/", '')
            TreatmentProcessImages.objects.create(
                treat=treat_pro.tag,
                treat_pro=treat_pro.id,
                thumb=st
            )

        TreatmentImagesTmp.objects.all().delete()

        return redirect('action:treatment_pro_update', pk)

    context = {
        'treat_pro': pk,
        'images': images
    }
    return render(request, 'action/treatmentpro/preview_images.html', context)


@csrf_protect
def delete_tmp_images(request, pk):
    if TreatmentImagesTmp.objects.all().count() == 0:
        return redirect('action:treatment_pro_update', pk)
    TreatmentImagesTmp.objects.all().delete()
    return redirect('action:treatment_pro_add_img', pk)
    # return render(request, 'action/treatmentpro/upload_images.html', {})


# Create your views here.
def consulting_overview(request):
    mobile = request.GET.get('mobile')
    consultings = Consulting.objects.all()
    if mobile:
        consultings = consultings.filter(customer__mobile__icontains=mobile)
    context = {
        'consult_total': Consulting.objects.all().count(),
        'consult_lookup': consultings.count(),
        'form': ConsultingFilterForm(),
        'consultings': consultings.order_by('-id')
    }
    return render(request, 'action/consultant/overview.html', context)


"""
class Consulting_All(LoginRequiredMixin, ListView):
  template_name = 'action/consultant/overview.html'
  login_url = 'manager:login'
  model = get_user_model()
  paginate_by = 10

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['consultings'] = Consulting.objects.order_by('-id')
    return context
"""


class ConsultingNew(LoginRequiredMixin, CreateView):
    model = Consulting
    form_class = ConsultingForm
    template_name = 'action/consultant/create.html'
    login_url = 'manager:login'
    success_url = reverse_lazy('action:consultant_overview')


class ConsultingView(LoginRequiredMixin, DetailView):
    queryset = Consulting.objects.select_related('consultor')
    template_name = 'action/consultant/single.html'
    context_object_name = 'consulting'
    login_url = 'manager:login'


class ConsultingUpdate(LoginRequiredMixin, UpdateView):
    model = Consulting
    form_class = ConsultingForm
    template_name = 'action/consultant/edit.html'
    login_url = 'manager:login'

    def get_success_url(self):
        return reverse('action:consultant_view', kwargs={'pk': self.kwargs['pk']})


def treatment_overview(request):
    mobile = request.GET.get('mobile')
    f_name = request.GET.get('fname')
    treatments = Treatment.objects.all().filter(customer__deleted=False)
    if mobile:
        treatments = treatments.filter(customer__mobile__icontains=mobile)
    if f_name:
        treatments = treatments.filter(customer__fullname__contains=f_name)

    context = {
        'treat_total': Treatment.objects.all().filter(customer__deleted=False).count(),
        'treat_lookup': treatments.count(),
        'form': TreatmentFilterForm(),
        'treatments': treatments.order_by('-id')
    }
    return render(request, 'action/treatment/overview.html', context)


class TreatmentAll(LoginRequiredMixin, ListView):
    template_name = 'action/treatment/overview.html'
    login_url = 'manager:login'
    model = get_user_model()
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['treatments'] = Treatment.objects.order_by('-id')
        return context


class TreatmentNew(LoginRequiredMixin, CreateView):
    model = Treatment
    form_class = TreatmentForm
    template_name = 'action/treatment/create.html'
    login_url = 'manager:login'
    success_url = reverse_lazy('action:treatment_new_add_fee')


def treatment_new(request):
    try:
        treats = Treatment.objects.all()
        serv = Service.objects.filter(id=treats.last().service_id).first()
        cust = Customer.objects.filter(id=treats.last().customer_id).first()

        if cust is not None:
            inv = Invoice.objects.filter(customer_id=cust.id).first()
            if inv is not None:
                fee = InvoiceFee.objects.filter(tag=inv.id).first()
                if fee is not None:
                    context = {
                        'treatments': treats,
                        'service': serv,
                        'customer': cust,
                        'invoice': inv,
                        'invoice_fee': fee,
                    }
                    InvoiceFee.objects.create(
                        tag=inv.id,
                        service=serv.name,
                        price=serv.cost
                    )
                    return render(request, 'action/treatment/addtofee.html', context)
        return render(request, 'action/treatment/overview.html', None)
    except ObjectDoesNotExist:
        return render(request, 'action/treatment/overview.html', None)


class TreatmentView(LoginRequiredMixin, DetailView):
    queryset = Treatment.objects.select_related('customer')
    template_name = 'action/treatment/single.html'
    context_object_name = 'treatment'
    login_url = 'manager:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["treat_pros"] = \
                TreatmentProcess.objects.filter(tag=self.object.pk).order_by('date')
            context["treat_pro_images"] = \
                TreatmentProcessImages.objects.filter(treat=self.object.pk)

            treat_assets = TreatmentAsset.objects.filter(treat=self.object.pk).order_by('asset__name')
            TreatmentAssetTmp.objects.all().delete()
            cur_id = 0
            ass_sum = 0
            for treat_ass in treat_assets:
                cur_id += 1
                ass_price = treat_ass.asset.price
                ass_quantity = treat_ass.quantity
                ass_sum += ass_price * ass_quantity
                TreatmentAssetTmp.objects.create(
                    id=cur_id,
                    asset_id=treat_ass.asset.id,
                    asset_name=treat_ass.asset.name,
                    asset_price=ass_price,
                    asset_quantity=ass_quantity,
                    asset_sum=ass_price * ass_quantity
                )

            context["treat_assets"] = TreatmentAssetTmp.objects.all()
            context["sum_price"] = ass_sum

            query_inv = None
            cur_customer = Treatment.objects.get(id=self.kwargs['pk']).customer_id
            for inv in Invoice.objects.all():
                if inv.customer_id == cur_customer:
                    query_inv = inv.id
                    break
            context["invoice_id"] = query_inv
            return context
        except ObjectDoesNotExist:
            return context


class TreatmentAppend(LoginRequiredMixin, FormMixin, ListView):
    model = TreatmentProcess
    template_name = 'action/treatment/append.html'
    form_class = TreatmentAppendForm
    login_url = 'manager:login'

    def get_success_url(self):
        return reverse('action:treatment_view', kwargs={'pk': self.kwargs['pk']})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        self.object = self.form_class
        form = self.get_form()
        if form.is_valid():
            TreatmentProcess.objects.create(
                tag=self.kwargs['pk'],
                date=form.cleaned_data['date'],
                status=form.cleaned_data['status']
            )
            TreatmentProcessImages.objects.create(
                treat=self.kwargs['pk'],
                treat_pro=TreatmentProcess.objects.all().count(),
                thumb=form.cleaned_data['thumb']
            )
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # Here, we would record the user's interest using the message # passed in form.cleaned_data['message']
        return super().form_valid(form)

    def get_context_data(self):
        context = super().get_context_data()
        if 'pk' in self.kwargs:
            context['treatment'] = Treatment.objects.get(pk=self.kwargs['pk'])
            context['treat_pros'] = TreatmentProcess.objects.filter(tag=self.kwargs['pk']).order_by('date')
            return context
        else:
            return context


class TreatmentUpdate(LoginRequiredMixin, UpdateView):
    model = Treatment
    template_name = 'action/treatment/edit.html'
    form_class = TreatmentForm
    login_url = 'manager:login'

    def get_success_url(self):
        return reverse('action:treatment_view', kwargs={'pk': self.kwargs['pk']})

    # success_url = reverse_lazy('action:treatment_overview')


class TreatmentDelete(LoginRequiredMixin, DeleteView):
    pass


class TreatmentProcessUpdate(LoginRequiredMixin, UpdateView):
    model = TreatmentProcess
    template_name = 'action/treatmentpro/edit.html'
    form_class = TreatmentProcessForm
    login_url = 'manager:login'

    # success_url = reverse_lazy('action:treatment_overview')

    def get_context_data(self):
        context = super().get_context_data()
        query = TreatmentProcess.objects.get(pk=self.kwargs['pk'])
        context['treat_pro'] = query
        context['treat'] = Treatment.objects.get(id=str(query.tag))
        context['treat_pro_images'] = TreatmentProcessImages.objects.filter(treat_pro=query.id)
        return context

    def get_success_url(self):
        treat_pro = TreatmentProcess.objects.get(pk=self.kwargs['pk'])
        treat = Treatment.objects.get(id=str(treat_pro.tag))

        # if (treat_pro.tmp_thumb != "") and (treat_pro.tmp_thumb is not None):
        #     TreatmentProcessImages.objects.create(
        #         treat=treat_pro.tag,
        #         treat_pro=treat_pro.id,
        #         thumb=treat_pro.tmp_thumb
        #     )
        #     TreatmentProcess.objects.filter(tag=treat_pro.tag).update(
        #         tmp_thumb=None
        #     )

        return reverse('action:treatment_view', kwargs={'pk': treat.pk})


def treatment_process_update_delete(request, pk, img_tag):
    img = TreatmentProcessImages.objects.get(id=img_tag)
    img.delete()

    return redirect('action:treatment_pro_update', pk)


class TreatmentAssetAdd(LoginRequiredMixin, FormMixin, ListView):
    model = TreatmentAsset
    template_name = 'action/treatment/asset.html'
    form_class = TreatmentAssetForm
    login_url = 'manager:login'

    def get_success_url(self):
        return reverse('action:treatment_view', kwargs={'pk': self.kwargs['pk']})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        self.object = self.form_class
        form = self.get_form()
        if form.is_valid():
            TreatmentAsset.objects.create(
                userID=request.user.pk,
                treat=self.kwargs['pk'],
                asset=form.cleaned_data['asset'],
                quantity=form.cleaned_data['quantity']
            )
            Inventory.objects.create(
                idIO=self.kwargs['pk'],
                asset=form.cleaned_data['asset'],
                quantityIO=-form.cleaned_data['quantity']
            )

            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # Here, we would record the user's interest using the message # passed in form.cleaned_data['message']
        return super().form_valid(form)

    def get_context_data(self):
        context = super().get_context_data()
        if 'pk' in self.kwargs:
            context['treatment'] = Treatment.objects.get(pk=self.kwargs['pk'])
            context['treat_assets'] = TreatmentAsset.objects.filter(treat=self.kwargs['pk']).order_by('id')
            return context
        else:
            return context


class TreatmentAssetUpdate(LoginRequiredMixin, UpdateView):
    model = TreatmentAsset
    template_name = 'action/treatment/assetedit.html'
    form_class = TreatmentAssetForm
    login_url = 'manager:login'

    def view(self, request):
        return HttpResponse()

    def dispatch(self, request, *args, **kwargs):
        # here you can make your custom validation for any particular user
        if not request.user.is_superuser:
            raise PermissionDenied()
        cur_pk = self.kwargs['pk']
        TreatmentAsset.objects.filter(id=cur_pk).update(userID=request.user.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        cur_pk = self.kwargs['pk']
        cur_treat = TreatmentAsset.objects.get(id=cur_pk).treat
        TreatmentAsset.objects.filter(id=cur_pk).update(timeO=datetime.datetime.now())
        # TreatmentAsset.objects.filter(id=cur_pk).update(userID=cur_user)

        return reverse('action:treatment_view', kwargs={'pk': cur_treat})


def invoice_overview(request):
    mobile = request.GET.get('mobile')
    fname = request.GET.get('fname')
    invoices = Invoice.objects.all()
    if mobile:
        invoices = invoices.filter(customer__mobile__icontains=mobile)
    if fname:
        invoices = invoices.filter(customer__fullname__contains=fname)
    context = {
        'inv_total': Invoice.objects.all().count(),
        'inv_lookup': invoices.count(),
        'form': InvoiceFilterForm(),
        'invoices': invoices.order_by('-id')
    }
    return render(request, 'action/invoice/overview.html', context)


class InvoiceAll(LoginRequiredMixin, ListView):
    template_name = 'action/invoice/overview.html'
    login_url = 'manager:login'
    model = get_user_model()
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoices'] = Invoice.objects.order_by('-id')
        return context


class InvoiceNew(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'action/invoice/create.html'
    login_url = 'manager:login'
    success_url = reverse_lazy('action:invoice_overview')


class InvoiceView(LoginRequiredMixin, DetailView):
    queryset = Invoice.objects.select_related('customer')
    template_name = 'action/invoice/single.html'
    context_object_name = 'invoice'
    login_url = 'manager:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['inv_pros'] = InvoiceProcess.objects.filter(
                tag=self.object.pk
            ).order_by('time')

            inv_pro_sum = InvoiceProcess.objects.filter(
                tag=self.object.pk
            ).aggregate(Sum('paid'))['paid__sum']

            context['inv_pro_total'] = inv_pro_sum

            context['inv_fees'] = InvoiceFee.objects.filter(
                tag=self.object.pk
            )

            inv_fee_sum = InvoiceFee.objects.filter(
                tag=self.object.pk
            ).aggregate(Sum('price'))['price__sum']

            context['inv_fee_total'] = inv_fee_sum

            if inv_fee_sum is None:
                inv_fee_sum = 0

            if inv_pro_sum is None:
                inv_pro_sum = 0

            context['inv_debt'] = inv_fee_sum - inv_pro_sum

            context['inv_debt_'] = inv_pro_sum - inv_fee_sum

            context['invoice'] = Invoice.objects.get(id=self.object.pk)

            context['services'] = Service.objects.all()

            context['treatments'] = Treatment.objects.filter(
                customer_id=Invoice.objects.get(id=self.object.pk).customer_id
            )

            return context
        except ObjectDoesNotExist:
            return context


class InvoiceViewPdf(LoginRequiredMixin, DetailView):
    queryset = Invoice.objects.select_related('customer')
    template_name = 'PDFs/invoice.html'
    context_object_name = 'invoice'
    login_url = 'manager:login'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        inv_fee_sum = InvoiceFee.objects.filter(tag=self.object.pk).aggregate(Sum('price'))['price__sum']
        inv_pro_sum = InvoiceProcess.objects.filter(tag=self.object.pk).aggregate(Sum('paid'))['paid__sum']

        if inv_fee_sum is None:
            inv_fee_sum = 0

        if inv_pro_sum is None:
            inv_pro_sum = 0

        context['inv_pros'] = InvoiceProcess.objects.filter(tag=self.object.pk).order_by('time')
        context['inv_pro_total'] = inv_pro_sum

        context['inv_fees'] = InvoiceFee.objects.filter(tag=self.object.pk)
        context['inv_fee_total'] = inv_fee_sum

        context['inv_debt'] = inv_fee_sum - inv_pro_sum

        context['inv_debt_'] = inv_pro_sum - inv_fee_sum

        context['invoice'] = Invoice.objects.get(id=self.object.pk)
        context['customer_name'] = \
            Customer.objects.get(id=Invoice.objects.get(id=self.object.pk).customer_id).fullname

        context['services'] = Service.objects.all()

        context['treatments'] = Treatment.objects.filter(
            customer_id=Invoice.objects.get(id=self.object.pk).customer_id
        )

        context['today'] = datetime.date.today()

        pdf = render_to_pdf('PDFs/invoice.html', context)
        HttpResponse(pdf, content_type='application/pdf')
        return context


class InvoiceAppend(LoginRequiredMixin, FormMixin, ListView):
    model = InvoiceProcess
    template_name = 'action/invoicepro/append.html'
    form_class = InvoiceAppendForm
    login_url = 'manager:login'

    def get_success_url(self):
        return reverse('action:invoice_view', kwargs={'pk': self.kwargs['pk']})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        self.object = self.form_class
        form = self.get_form()
        if form.is_valid():
            InvoiceProcess.objects.create(
                tag=self.kwargs['pk'],
                # time=form.cleaned_data['time'],
                time=datetime.datetime.now(),
                description=form.cleaned_data['description'],
                paid=form.cleaned_data['paid'],
                payby=form.cleaned_data['payby']
            )
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # Here, we would record the user's interest using the message # passed in form.cleaned_data['message']
        return super().form_valid(form)

    def get_context_data(self):
        context = super().get_context_data()
        if 'pk' in self.kwargs:
            context['invoice'] = Invoice.objects.get(pk=self.kwargs['pk'])
            context['inv_pros'] = InvoiceProcess.objects.filter(tag=self.kwargs['pk']).order_by('time')
            return context
        else:
            return context


class InvoiceUpdate(LoginRequiredMixin, UpdateView):
    model = Invoice
    template_name = 'action/invoice/edit.html'
    form_class = InvoiceForm
    login_url = 'manager:login'

    def get_success_url(self):
        return reverse('action:invoice_view', kwargs={'pk': self.kwargs['pk']})

    # success_url = reverse_lazy('action:treatment_overview')


class InvoiceDelete(LoginRequiredMixin, DeleteView):
    pass


class InvoiceProcessUpdate(LoginRequiredMixin, UpdateView):
    model = InvoiceProcess
    template_name = 'action/invoicepro/edit.html'
    form_class = InvoiceProcessForm
    login_url = 'manager:login'

    # success_url = reverse_lazy('action:treatment_overview')

    def get_context_data(self):
        context = super().get_context_data()
        query = InvoiceProcess.objects.get(pk=self.kwargs['pk'])
        context['inv_pro'] = query
        context['inv'] = Invoice.objects.get(id=str(query.tag))
        return context

    def get_success_url(self):
        inv_pro = InvoiceProcess.objects.get(pk=self.kwargs['pk'])
        inv = Invoice.objects.get(id=str(inv_pro.tag))
        # Invoice.objects.filter(id=str(inv_pro.tag)).update(time=inv_pro.time)

        return reverse('action:invoice_view', kwargs={'pk': inv.pk})


class InvoiceFeeInit(LoginRequiredMixin, FormMixin, ListView):
    model = InvoiceFee
    template_name = 'action/invoicefee/create.html'
    form_class = InvoiceFeeForm
    login_url = 'manager:login'

    def get_success_url(self):
        return reverse('action:invoice_view', kwargs={'pk': self.kwargs['pk']})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        self.object = self.form_class
        form = self.get_form()
        if form.is_valid():

            # cust = Treatment.objects.get(id=self.kwargs['pk']).customer_id

            InvoiceFee.objects.create(
                tag=self.kwargs['pk'],
                # time=datetime.datetime.now(),
                service=form.cleaned_data['service'],
                price=form.cleaned_data['price']
            )

            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # Here, we would record the user's interest using the message # passed in form.cleaned_data['message']
        return super().form_valid(form)

    def get_context_data(self):
        context = super().get_context_data()

        try:
            context['inv_pros'] = InvoiceProcess.objects.filter(
                tag=self.kwargs['pk']
            ).order_by('time')

            if 'pk' in self.kwargs:
                context['invoice'] = Invoice.objects.get(id=self.kwargs['pk'])

                context['services'] = Service.objects.all()

                context['treatments'] = Treatment.objects.filter(
                    customer_id=Invoice.objects.get(id=self.kwargs['pk']).customer_id
                )
            else:
                context['services'] = Service.objects.all()

            return context
        except ObjectDoesNotExist:
            return context


class InvoiceFeeCopy(LoginRequiredMixin, FormMixin, ListView):
    model = InvoiceFee
    template_name = 'action/invoicefee/create_copy.html'
    form_class = InvoiceFeeCopyForm
    login_url = 'manager:login'

    def get_success_url(self):
        return reverse('action:invoice_view', kwargs={'pk': self.kwargs['pk']})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        self.object = self.form_class
        form = self.get_form()
        if form.is_valid():

            inv_pros = InvoiceProcess.objects.filter(tag=self.kwargs['pk'])

            des = ""

            for inv_pro in inv_pros:
                des = des + " + " + inv_pro.description

            sum_paid = InvoiceProcess.objects.filter(
                tag=self.kwargs['pk']).aggregate(Sum('paid'))['paid__sum']

            InvoiceFee.objects.create(
                tag=self.kwargs['pk'],
                # time=datetime.datetime.now(),
                service=des,  # inv_pros.first().description,
                price=sum_paid
            )

            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # Here, we would record the user's interest using the message # passed in form.cleaned_data['message']
        return super().form_valid(form)

    def get_context_data(self):
        context = super().get_context_data()

        try:
            inv_pros = InvoiceProcess.objects.filter(tag=self.kwargs['pk'])

            des = ""

            for inv_pro in inv_pros:
                des = des + " + " + inv_pro.description

            context['inv_pros'] = inv_pros
            context['sum_description'] = des
            context['sum_paid'] = InvoiceProcess.objects.filter(
                tag=self.kwargs['pk']).aggregate(Sum('paid'))['paid__sum']

            if 'pk' in self.kwargs:
                context['invoice'] = Invoice.objects.get(id=self.kwargs['pk'])

            return context
        except ObjectDoesNotExist:
            return context


class InvoiceFeeUpdate(LoginRequiredMixin, UpdateView):
    model = InvoiceFee
    template_name = 'action/invoicefee/edit.html'
    form_class = InvoiceFeeForm
    login_url = 'manager:login'

    # success_url = reverse_lazy('action:treatment_overview')

    def get_context_data(self):
        context = super().get_context_data()
        query = InvoiceFee.objects.get(pk=self.kwargs['pk'])
        context['inv_fee'] = query
        context['inv'] = Invoice.objects.get(id=str(query.tag))
        return context

    def get_success_url(self):
        inv_fee = InvoiceFee.objects.get(pk=self.kwargs['pk'])
        inv = Invoice.objects.get(id=str(inv_fee.tag))
        # Invoice.objects.filter(id=str(inv_pro.tag)).update(time=inv_pro.time)

        return reverse('action:invoice_view', kwargs={'pk': inv.pk})


class InvoiceAppendFee(LoginRequiredMixin, FormMixin, ListView):
    model = InvoiceFee
    template_name = 'action/invoicefee/append.html'
    form_class = InvoiceAppendFeeForm
    login_url = 'manager:login'

    def get_success_url(self):
        return reverse('action:invoice_view', kwargs={'pk': self.kwargs['pk']})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        self.object = self.form_class
        form = self.get_form()
        if form.is_valid():
            InvoiceFee.objects.create(
                tag=self.kwargs['pk'],
                # time=datetime.datetime.now(),
                service=form.cleaned_data['service'],
                price=form.cleaned_data['price']
            )
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # Here, we would record the user's interest using the message # passed in form.cleaned_data['message']
        return super().form_valid(form)

    def get_context_data(self):
        context = super().get_context_data()
        if 'pk' in self.kwargs:
            context['invoice'] = Invoice.objects.get(pk=self.kwargs['pk'])
            context['inv_fees'] = InvoiceFee.objects.filter(tag=self.kwargs['pk'])
            return context
        else:
            return context


def invoice_debt(request):
    # inv_grp_fees = InvoiceFee.objects.values('tag').annotate(total_fee=Sum('price'))
    # inv_grp_pros = InvoiceProcess.objects.values('tag').annotate(total_paid=Sum('paid'))

    invoices = Invoice.objects.all().order_by('id')
    inv_fees = InvoiceFee.objects.all().order_by('tag')
    inv_pros = InvoiceProcess.objects.all().order_by('tag')

    customers = \
        Customer.objects.filter(deleted=False).filter(id__in=Invoice.objects.values('customer_id'))

    if customers is None:
        return render(request, 'action/invoice/overview.html', None)

    if customers.count() < 1:
        return render(request, 'action/invoice/overview.html', None)

    DebtTmp.objects.all().delete()

    cur_id = 0

    for inv in invoices:
        inv_tag = inv.id
        total_inv_fees = inv_fees.filter(tag=inv_tag).count()
        if total_inv_fees == 0:
            continue
        total_inv_pros = inv_pros.filter(tag=inv_tag).count()
        max_total = max(total_inv_fees, total_inv_pros)

        curr = 1000
        cur_inv_fees = None
        cur_inv_pros = None
        sum_fee = 0
        sum_pay = 0

        has_sum = False

        for i in range(max_total + 1):
            customer_id = None
            customer_name = None
            if i == 0:
                customer_id = invoices.get(id=inv_tag).customer_id
                customer_name = customers.get(id=customer_id).fullname

            cur_service = None
            cur_fee = None
            cur_description = None
            cur_paid = None
            cur_debt = None

            if max_total == 1:
                if i == 0:
                    if total_inv_fees == 1:
                        cur_service = inv_fees.get(tag=inv_tag).service
                        cur_fee = inv_fees.get(tag=inv_tag).price

                    if total_inv_pros == 1:
                        cur_description = inv_pros.get(tag=inv_tag).description
                        cur_paid = inv_pros.get(tag=inv_tag).paid

                    if (total_inv_fees == 1) and (total_inv_pros == 1):
                        cur_debt = cur_paid - cur_fee
                else:
                    cur_service = None
                    cur_fee = None
                    cur_description = None
                    cur_paid = None
                    cur_debt = None
            else:
                if i == 0:
                    curr = 0
                    sum_fee = 0
                    sum_pay = 0
                    cur_inv_fees = inv_fees.filter(tag=inv_tag)
                    cur_inv_pros = inv_pros.filter(tag=inv_tag)
                    total_inv_fees = cur_inv_fees.count()
                    total_inv_pros = cur_inv_pros.count()

                if (total_inv_fees > 0) and (curr >= 0):
                    if curr < total_inv_fees:
                        cur_service = cur_inv_fees[curr].service
                        cur_fee = cur_inv_fees[curr].price
                        sum_fee += cur_fee

                if (total_inv_pros > 0) and (curr >= 0):
                    if curr < total_inv_pros:
                        cur_description = cur_inv_pros[curr].description
                        cur_paid = cur_inv_pros[curr].paid
                        sum_pay += cur_paid

                if (curr >= 0) and (curr == max_total):
                    cur_service = "Tổng chi phí:"
                    cur_fee = sum_fee
                    cur_description = "Tổng chi trả:"
                    cur_paid = sum_pay
                    cur_debt = sum_fee - sum_pay
                    has_sum = True

                curr += 1

            if customer_name is not None:
                customer_name = customer_name[:24]

            if cur_service is not None:
                cur_service = cur_service[:64]

            if cur_description is not None:
                cur_description = cur_description[:64]

            cur_id += 1
            DebtTmp.objects.create(
                id=cur_id,
                invoice=inv_tag,
                customer_id=customer_id,
                customer_name=customer_name,
                inv_fee_note=cur_service,
                inv_fee_paid=cur_fee,
                inv_pay_note=cur_description,
                inv_pay_paid=cur_paid,
                debt=cur_debt,
            )
        if has_sum:
            cur_id += 1
            DebtTmp.objects.create(
                id=cur_id,
                invoice=inv_tag,
                customer_id=None,
                customer_name=None,
                inv_fee_note=None,
                inv_fee_paid=None,
                inv_pay_note=None,
                inv_pay_paid=None,
                debt=None,
            )
    context = {
        'customers': Customer.objects.all(),
        'invoices': invoices.order_by('id'),
        'inv_fees': inv_fees,
        'inv_pros': inv_pros,
        'debts': DebtTmp.objects.all(),
    }

    return render(request, 'action/invoice/debt.html', context)


def debt_view_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    fn = "debt_" + datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".csv"
    response = HttpResponse(
        content_type="text/csv",
        headers={
            "Content-Disposition":
                'attachment; filename=' + fn
        },
    )

    writer = csv.writer(response)

    for inv in DebtTmp.objects.all():

        if inv.inv_fee_note is not None:
            if ';' in inv.inv_fee_note:
                inv.inv_fee_note = inv.inv_fee_note.replace(';', ' -')

        if inv.inv_pay_note is not None:
            if ';' in inv.inv_pay_note:
                inv.inv_pay_note = inv.inv_pay_note.replace(';', ' -')

        writer.writerow([
            inv.customer_name,
            inv.inv_fee_note,
            inv.inv_fee_paid,
            inv.inv_pay_note,
            inv.inv_pay_paid,
            inv.debt
        ])
        # writer.writerow(["First row", "Foo", "Bar", "Baz"])
        # writer.writerow(["Second row", "A", "B", "C", '"Testing"', "Here's a quote"])

    return response


def some_view(request):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="hello.pdf")


def invoice_exp_pdf(request):
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    # p = canvas.Canvas(buffer)

    # w, h = A4
    p = canvas.Canvas(buffer, pagesize=A4)

    p.setFont("Times-Roman", 14, leading=None)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    # p.drawString(100, 100, "Hello world.")
    img = ImageReader("media/_Images/SkyLove-Logo-128x128.jpg")
    p.drawImage(img, 20, 720, width=80, height=80, mask=None)
    p.drawString(200, 740, "PHIẾU THANH TOÁN")

    def get_context_data(self, **kwargs):
        context = get_context_data(**kwargs)
        try:
            query = InvoiceProcess.objects.filter(tag=self.object.pk)  # .order_by('time')
            context["inv_pros"] = query
            return context
        except ObjectDoesNotExist:
            return context

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="hello.pdf")
