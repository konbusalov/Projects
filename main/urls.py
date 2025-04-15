from django.urls import path
from . import views
from .utils.decorators import role_required


urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.sign_in, name='login'),
    path('logout/', views.sign_out, name='logout'),
    path('register/', views.sign_up, name='register'),
    path('client_dashboard/', role_required('CLIENT')(views.client_dashboard), name='client dashboard'),
    path('staff_dashboard/', role_required('OPERATOR', 'MANAGER')(views.staff_dashboard), name='staff dashboard'),
    path('specialist_dashboard/', role_required('SPECIALIST')(views.specialist_dashboard), name='specialist dashboard'),
    path('admin_dashboard/', role_required('ADMIN')(views.admin_dashboard), name='admin dashboard'),
    path('create_account/', role_required('CLIENT')(views.create_account), name='create_account'),
    path('client_dashboard/make_deposit/<uuid:account_number>', role_required('CLIENT')(views.make_deposit), name='make_deposit'),
    path('client_dashboard/make_transfer/<uuid:account_number>', role_required('CLIENT')(views.make_transfer), name='make_transfer'),
    path('make_loan/', role_required('CLIENT')(views.make_loan), name='make_loan'),
    path('make_lease/', role_required('CLIENT')(views.make_lease), name='make_lease'),
    path('staff_dashboard/cancel_transaction/<int:id>', role_required('OPERATOR', 'MANAGER')(views.cancel_transaction), name='cancel_transaction'),
    path('staff_dashboard/approve_loan/<int:id>', role_required('MANAGER')(views.approve_loan), name='approve_loan'),
    path('staff_dashboard/reject_loan/<int:id>', role_required('MANAGER')(views.reject_loan), name='reject_loan'),
    path('staff_dashboard/approve_lease/<int:id>', role_required('MANAGER')(views.approve_lease), name='approve_lease'),
    path('staff_dashboard/reject_lease/<int:id>', role_required('MANAGER')(views.reject_lease), name='reject_lease'),
]