import csv
import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Sum
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.views.generic.edit import FormMixin

from SkyLove.utils import render_to_pdf
from action.models import TreatmentAsset, Treatment
from inventory.forms import AssetCategoryForm, AssetForm, SupplierForm, AssetUnitForm, AssetFilterForm, InventoryForm
from inventory.models import AssetCategory, Asset, Supplier, AssetUnit, Inventory, Purchase, DeliveryTmp, InventoryTmp
from manager.models import Customer, Service


# Create your views here.

# AssetCategory views
class AssetCategoryAll(LoginRequiredMixin, ListView):
    template_name = 'inventory/assetcategory/index.html'
    login_url = 'manager:login'
    model = get_user_model()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assetcategories'] = AssetCategory.objects.order_by('id')
        return context


class AssetCategoryNew(LoginRequiredMixin, CreateView):
    model = AssetCategory
    template_name = 'inventory/assetcategory/create.html'
    form_class = AssetCategoryForm
    login_url = 'manager:login'
    success_url = reverse_lazy('inventory:ass_cat_all')


class AssetCategoryUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'inventory/assetcategory/edit.html'
    form_class = AssetCategoryForm
    login_url = 'manager:login'
    model = AssetCategory
    success_url = reverse_lazy('inventory:ass_cat_all')


# AssetUnit views
class AssetUnitAll(LoginRequiredMixin, ListView):
    template_name = 'inventory/assetunit/index.html'
    login_url = 'manager:login'
    model = get_user_model()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assetunits'] = AssetUnit.objects.order_by('name')
        return context


class AssetUnitNew(LoginRequiredMixin, CreateView):
    model = AssetCategory
    template_name = 'inventory/assetunit/create.html'
    form_class = AssetUnitForm
    login_url = 'manager:login'
    success_url = reverse_lazy('inventory:ass_unt_all')


class AssetUnitUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'inventory/assetunit/edit.html'
    form_class = AssetUnitForm
    login_url = 'manager:login'
    model = AssetUnit
    success_url = reverse_lazy('inventory:ass_unt_all')


# Asset views
class AssetAll(LoginRequiredMixin, ListView):
    template_name = 'inventory/asset/overview.html'
    login_url = 'manager:login'
    model = Asset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = AssetCategory.objects.order_by('id')
        context['assets'] = Asset.objects.order_by('name')
        context['asset_total'] = Asset.objects.all().count()
        return context


class AssetNew(LoginRequiredMixin, CreateView):
    model = Asset
    template_name = 'inventory/asset/create.html'
    form_class = AssetForm
    login_url = 'manager:login'
    success_url = reverse_lazy('inventory:asset_all')


class AssetUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'inventory/asset/edit.html'
    form_class = AssetForm
    login_url = 'manager:login'
    model = Asset
    success_url = reverse_lazy('inventory:asset_all')


class AssetView(LoginRequiredMixin, DetailView):
    queryset = Asset.objects.select_related('category')
    template_name = 'inventory/asset/single.html'
    context_object_name = 'asset'
    login_url = 'manager:login'


# Supplier views
class SupplierAll(LoginRequiredMixin, ListView):
    template_name = 'inventory/supplier/overview.html'
    login_url = 'manager:login'
    model = get_user_model()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suppliers'] = Supplier.objects.order_by('id')
        return context


class SupplierNew(LoginRequiredMixin, CreateView):
    model = Supplier
    template_name = 'inventory/supplier/create.html'
    form_class = SupplierForm
    login_url = 'manager:login'
    success_url = reverse_lazy('inventory:supplier_all')


class SupplierUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'inventory/supplier/edit.html'
    form_class = SupplierForm
    login_url = 'manager:login'
    model = Supplier
    success_url = reverse_lazy('inventory:supplier_all')


class SupplierView(LoginRequiredMixin, DetailView):
    queryset = Supplier.objects.order_by('id')
    template_name = 'inventory/supplier/single.html'
    context_object_name = 'supplier'
    login_url = 'manager:login'


def inv_purchases():
    return Inventory.objects.values(
        'asset_id',
        'asset__name') \
        .order_by('asset_id') \
        .annotate(quantity=Sum('quantityIO')) \
        .order_by('asset__name')


def inventory_overview(request):
    category = request.GET.get('category')
    asset_name = request.GET.get('asset_name')

    assets = Asset.objects.all().order_by('category_id')
    if category:
        if category != "0":
            assets = assets.filter(category_id=category)
    if asset_name:
        assets = assets.filter(name__contains=asset_name)

    InventoryTmp.objects.all().delete()

    cur_id = 0
    for asset in assets:
        ass_id = asset.id

        cur_purchases = Inventory.objects.all().filter(asset_id=ass_id).filter(quantityIO__gt=0)
        total_purchases = cur_purchases.count()
        if (total_purchases is None) or (total_purchases < 1):
            continue

        cur_deliveries = TreatmentAsset.objects.all().filter(asset_id=ass_id)
        total_deliveries = cur_deliveries.count()
        max_io = max(total_purchases, total_deliveries)

        sum_in = 0
        sum_out = 0
        curr = 1000

        has_sum = False

        for i in range(max_io + 1):

            ass_name = None
            cat_name = None
            cur_input = None
            cur_output = None
            cur_time_in = None
            cur_time_out = None
            cur_treat = None
            cur_stock = None

            if i == 0:
                curr = 0
                ass_name = asset.name
                cat_name = asset.category

            if max_io == 1:
                if i == 0:
                    if total_purchases == 1:
                        cur_id_in = cur_purchases[0].idIO
                        cur_time_in = Purchase.objects.get(id=cur_id_in).timeI
                        cur_input = Inventory.objects.filter(quantityIO__gt=0).get(idIO=cur_id_in).quantityIO

                    if total_deliveries == 1:
                        if (cur_deliveries is not None) and (cur_deliveries.count() > 0):
                            cur_time_out = cur_deliveries[0].timeO
                            cur_treat = cur_deliveries[0].treat
                            cur_output = cur_deliveries[0].quantity

                    if total_purchases == 1:
                        if total_deliveries == 1:
                            cur_stock = cur_input - cur_output
                        else:
                            cur_stock = cur_input
                else:
                    ass_name = None
                    cat_name = None
                    cur_input = None
                    cur_output = None
                    cur_time_in = None
                    cur_time_out = None
                    cur_treat = None
                    cur_stock = None
            else:
                if i == 0:
                    curr = 0
                    sum_in = 0
                    sum_out = 0

                if (total_purchases > 0) and (curr >= 0):
                    if curr < total_purchases:
                        cur_id_in = cur_purchases[curr].idIO
                        cur_time_in = Purchase.objects.get(id=cur_id_in).timeI
                        cur_input = Inventory.objects.filter(quantityIO__gt=0).get(idIO=cur_id_in).quantityIO
                        sum_in += cur_input

                if (total_deliveries > 0) and (curr >= 0):
                    if curr < total_deliveries:
                        cur_time_out = cur_deliveries[curr].timeO
                        cur_output = cur_deliveries[curr].quantity
                        cur_treat = cur_deliveries[curr].treat
                        sum_out += cur_output

                if (curr >= 0) and (curr == max_io):
                    ass_name = "TỔNG CỘNG"
                    cur_input = sum_in
                    cur_output = sum_out
                    cur_stock = sum_in - sum_out
                    has_sum = True

                curr += 1

            if ass_name is not None:
                ass_name = ass_name[:50]

            cur_id += 1
            InventoryTmp.objects.create(
                id=cur_id,
                timeI=cur_time_in,
                input=cur_input,
                asset_id=ass_id,
                asset_name=ass_name,
                category_id=asset.category_id,
                category_name=cat_name,
                timeO=cur_time_out,
                output=cur_output,
                treatment=cur_treat,
                stock=cur_stock
            )

        if has_sum:
            cur_id += 1
            InventoryTmp.objects.create(
                id=cur_id,
                timeI=None,
                input=None,
                asset_id=ass_id,
                asset_name=None,
                category_id=asset.category_id,
                category_name=None,
                timeO=None,
                output=None,
                treatment=None,
                stock=None
            )

    context = {
        # 'customers': Customer.objects.all(),
        'categories': AssetCategory.objects.order_by('id'),
        'inventories': InventoryTmp.objects.all(),
    }

    return render(request, 'inventory/inv/overview.html', context)


def inventory_view_pdf(request):
    data = {
        'inventories': InventoryTmp.objects.all(),
    }
    pdf = render_to_pdf('PDFs/overview.html', data)
    return HttpResponse(pdf, content_type='application/pdf')


def inventory_view_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    fn = "inventory_" + datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".csv"
    response = HttpResponse(
        content_type="text/csv",
        headers={
            "Content-Disposition":
                'attachment; filename=' + fn
        },
    )

    writer = csv.writer(response)
    for inv in InventoryTmp.objects.all():
        writer.writerow([
            inv.category_name,
            inv.asset_name,
            inv.timeI,
            inv.input,
            inv.timeO,
            inv.output,
            inv.stock
        ])
        # writer.writerow(["First row", "Foo", "Bar", "Baz"])
        # writer.writerow(["Second row", "A", "B", "C", '"Testing"', "Here's a quote"])

    return response


class PurchaseNew(LoginRequiredMixin, FormMixin, ListView):
    model = Purchase
    template_name = 'inventory/inv/create.html'
    form_class = InventoryForm
    login_url = 'manager:login'

    def get_success_url(self):
        return reverse('inventory:inv_all')

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        self.object = self.form_class
        form = self.get_form()
        if form.is_valid():
            Purchase.objects.create(
                userID=request.user.pk,
                supplier=form.cleaned_data['supplier']
            )
            Inventory.objects.create(
                idIO=Purchase.objects.all().count(),
                asset=form.cleaned_data['asset'],
                quantityIO=form.cleaned_data['quantityIO']
            )
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # Here, we would record the user's interest using the message # passed in form.cleaned_data['message']
        return super().form_valid(form)


def deliver_overview(request):
    """
    mobile = request.GET.get('mobile')
    fname = request.GET.get('fname')
    customers = Customer.objects.filter(deleted=False)
    if mobile:
        customers = customers.filter(mobile__contains=mobile)
    if fname:
        customers = customers.filter(fullname__contains=fname)

    invs = Inventory.objects.all()
    i = 0
    for inv in invs:
        i += 1
        if inv.id != i:
            break
    """

    customers = Customer.objects.filter(deleted=False)
    deliveries = TreatmentAsset.objects.all().order_by('treat')

    DeliveryTmp.objects.all().delete()
    cur_id = 0
    sum_paid = 0
    sum_count = 0
    treat_id = 0
    asst_id = 0
    for delivery in deliveries:
        cust_id = Treatment.objects.get(id=delivery.treat).customer_id
        cust_name = customers.get(id=cust_id)
        treat_id = delivery.treat
        serv_id = Treatment.objects.get(id=treat_id).service_id
        treat_name = Service.objects.get(id=serv_id).name
        asst_id = delivery.asset_id
        asst_name = Asset.objects.get(id=delivery.asset_id).name
        asst_price = Asset.objects.get(id=delivery.asset_id).price
        asst_paid = asst_price * delivery.quantity
        i_first = deliveries.first().id
        if delivery.id > i_first:
            if delivery.treat == deliveries.get(id=(delivery.id - 1)).treat:
                cust_id = cust_name = None
                treat_name = None

        cur_id += 1
        DeliveryTmp.objects.create(
            id=cur_id,
            customer_id=cust_id,
            customer_name=cust_name,
            treatment_id=treat_id,
            treatment_name=treat_name,
            asset_id=asst_id,
            asset_name=asst_name,
            asset_price=asst_price,
            quantity=delivery.quantity,
            paid=asst_paid
        )
        sum_paid += asst_paid
        sum_count += 1

        if delivery.id > i_first:
            if (
                (delivery.id < deliveries.count()) and (delivery.treat != deliveries.get(id=(delivery.id + 1)).treat)
            ):
                cust_id = cust_name = None
                treat_name = None
                asst_name = "Tổng cộng"
                asst_price = None
                asst_paid = sum_paid
                cur_id += 1
                DeliveryTmp.objects.create(
                    id=cur_id,
                    customer_id=cust_id,
                    customer_name=cust_name,
                    treatment_id=treat_id,
                    treatment_name=treat_name,
                    asset_id=asst_id,
                    asset_name=asst_name,
                    asset_price=asst_price,
                    quantity=None,
                    paid=asst_paid
                )
                sum_paid = 0
                sum_count = 0

    if sum_count > 1:
        asst_name = "Tổng cộng"
        cur_id += 1
        DeliveryTmp.objects.create(
            id=cur_id,
            customer_id=None,
            customer_name=None,
            treatment_id=treat_id,
            treatment_name=None,
            asset_id=asst_id,
            asset_name=asst_name,
            asset_price=None,
            quantity=None,
            paid=sum_paid
        )

    context = {
        'deliveries': DeliveryTmp.objects.all(),
        # 'curI': i
    }
    return render(request, 'inventory/out/overview.html', context)


def delivery_view_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    fn = "delivery_" + datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".csv"
    response = HttpResponse(
        content_type="text/csv",
        headers={
            "Content-Disposition":
                'attachment; filename=' + fn
        },
    )

    writer = csv.writer(response)
    for inv in DeliveryTmp.objects.all():
        writer.writerow([
            inv.customer_name,
            inv.treatment_name,
            inv.asset_name,
            inv.asset_price,
            inv.quantity,
            inv.paid
        ])
        # writer.writerow(["First row", "Foo", "Bar", "Baz"])
        # writer.writerow(["Second row", "A", "B", "C", '"Testing"', "Here's a quote"])

    return response
