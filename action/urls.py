from django.urls import path
from . import views

app_name = 'action'

urlpatterns = [

  # Treatment Routes
  path('treatment/overview', views.treatment_overview, name='treatment_overview'),
  path('treatment/new/', views.TreatmentNew.as_view(), name='treatment_new'),
  path('treatment/newaddfee/', views.treatment_new, name='treatment_new_add_fee'),
  path('treatment/<int:pk>/view/', views.TreatmentView.as_view(), name='treatment_view'),
  path('treatment/<int:pk>/update/', views.TreatmentUpdate.as_view(), name='treatment_update'),
  path('treatment/<int:pk>/append/', views.TreatmentAppend.as_view(), name='treatment_append'),
  # path('treatment/<int:pk>/delete/', views.TreatmentTag_Delete.as_view(), name='treatment_delete'),

  path('treatmentpro/<int:pk>/update/', views.TreatmentProcessUpdate.as_view(), name='treatment_pro_update'),
  path('treatmentpro/<int:pk>/addimg/', views.upload_images, name='treatment_pro_add_img'),
  path('treatmentpro/<int:pk>/preimg/', views.image_preview, name='treatment_pro_prev_img'),
  path('treat_img_delete/<int:pk>/<int:img_tag>',
       views.treatment_process_update_delete,
       name='treatment_pro_update_delete'),

  path('treatment/<int:pk>/asset/', views.TreatmentAssetAdd.as_view(), name='treatment_asset'),
  path('treatment/<int:pk>/assetedit/', views.TreatmentAssetUpdate.as_view(), name='treatment_asset_edit'),

  # Consulting Routes
  path('consultant/overview', views.consulting_overview, name='consultant_overview'),
  path('consultant/new/', views.ConsultingNew.as_view(), name='consultant_new'),
  path('consultant/<int:pk>/view/', views.ConsultingView.as_view(), name='consultant_view'),
  path('consultant/<int:pk>/update/', views.ConsultingUpdate.as_view(), name='consultant_update'),

  # Invoice
  path('invoice/overview', views.invoice_overview, name='invoice_overview'),
  path('invoice/new/', views.InvoiceNew.as_view(), name='invoice_new'),
  path('invoice/<int:pk>/view/', views.InvoiceView.as_view(), name='invoice_view'),
  path('invoice/<int:pk>/viewpdf/', views.InvoiceViewPdf.as_view(), name='invoice_view_pdf'),
  path('invoice/<int:pk>/update/', views.InvoiceUpdate.as_view(), name='invoice_update'),
  path('invoice/<int:pk>/append/', views.InvoiceAppend.as_view(), name='invoice_append'),

  path('invoice/debt', views.invoice_debt, name='invoice_debt'),
  path('invoice/debt/csv', views.debt_view_csv, name='invoice_debt_csv'),

  path('invoicepro/<int:pk>/update/', views.InvoiceProcessUpdate.as_view(), name='invoice_pro_update'),
  path('invoicefee/<int:pk>/init/', views.InvoiceFeeInit.as_view(), name='invoice_fee_init'),
  path('invoicefee/<int:pk>/copy/', views.InvoiceFeeCopy.as_view(), name='invoice_fee_copy'),
  path('invoicefee/<int:pk>/update/', views.InvoiceFeeUpdate.as_view(), name='invoice_fee_update'),
  path('invoicefee/<int:pk>/append/', views.InvoiceAppendFee.as_view(), name='invoice_fee_append'),

  path('invoice/<int:pk>/prt', views.invoice_exp_pdf, name='invoice_prt_demo'),

]
