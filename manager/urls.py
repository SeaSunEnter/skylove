from django.urls import path
from . import views

app_name = 'manager'

urlpatterns = [
    # Authentication Routes
    path('', views.Index.as_view(), name='index'),
    path('register/', views.Register.as_view(), name='reg'),
    path('login/', views.LoginViewer.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('user/<int:pk>/update', views.UserUpdate.as_view(), name='user_update'),
    path('user/password_change', views.password_change, name='user_password_change'),

    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('birthday/', views.BirthdayView.as_view(), name='birthday'),

    # Employee Routes
    path('employee/', views.EmployeeAll.as_view(), name='employee_all'),
    path('employee/new/', views.EmployeeNew.as_view(), name='employee_new'),
    path('employee/<int:pk>/view/', views.EmployeeView.as_view(), name='employee_view'),
    path('employee/<int:pk>/update/', views.EmployeeUpdate.as_view(), name='employee_update'),
    path('employee/<int:pk>/delete/', views.EmployeeDelete.as_view(), name='employee_delete'),

    # Department Routes
    path('department/all/', views.DepartmentAll.as_view(), name='dept_all'),
    path('department/add/', views.DepartmentNew.as_view(), name='dept_new'),
    path('department/<int:pk>/update/', views.DepartmentUpdate.as_view(), name='dept_update'),

    # path('customer/dashboard', views.Dashboard.as_view(), name='dashboard'),
    path('customer/overview', views.customer_overview, name='customer_overview'),
    path('customer/all', views.CustomerAll.as_view(), name='customer_all'),
    path('customer/new/', views.CustomerNew.as_view(), name='customer_new'),
    path('customer/<int:pk>/view/', views.CustomerView.as_view(), name='customer_view'),
    path('customer/<int:pk>/update/', views.CustomerUpdate.as_view(), name='customer_update'),
    path('customer/<int:pk>/delete/', views.CustomerDelete.as_view(), name='customer_delete'),

    # Customer Source Routes
    path('customer/source/', views.CustomerSourceAll.as_view(), name='cust_src_all'),
    path('customer/source/add/', views.CustomerSourceNew.as_view(), name='cust_src_new'),
    path('customer/source/<int:pk>/update/', views.CustomerSourceUpdate.as_view(), name='cust_src_update'),

    # Service Routes
    path('service/', views.ServiceAll.as_view(), name='app_srv_all'),
    path('service/add/', views.ServiceNew.as_view(), name='app_srv_new'),
    path('service/<int:pk>/update/', views.ServiceUpdate.as_view(), name='app_srv_update'),

]
