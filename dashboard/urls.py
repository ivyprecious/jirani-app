from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('tenants/', views.tenants_view, name='tenants'),
    path('tenants/add/', views.add_tenant_view, name='add_tenant'),
    path('tenants/edit/<int:resident_id>/', views.edit_tenant_view, name='edit_tenant'),
    path('tenants/delete/<int:resident_id>/', views.delete_tenant_view, name='delete_tenant'),
    path('parking/', views.parking_view, name='parking'),
    path('parking/assign/', views.assign_parking_view, name='assign_parking'),
    path('parking/unassign/<int:slot_id>/', views.unassign_parking_view, name='unassign_parking'),
    path('subcontractors/', views.subcontractors_view, name='subcontractors'),
    path('subcontractors/add/', views.add_subcontractor_view, name='add_subcontractor'),
    path('subcontractors/edit/<int:subcontractor_id>/', views.edit_subcontractor_view, name='edit_subcontractor'),
    path('subcontractors/delete/<int:subcontractor_id>/', views.delete_subcontractor_view, name='delete_subcontractor'),
]