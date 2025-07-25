from django.urls import path
from . import views, views_users

app_name = 'students'

urlpatterns = [
    # مسارات إدارة المستخدمين
    path('users/', views_users.UserListView.as_view(), name='user_list'),
    path('users/add/', views_users.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', views_users.UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', views_users.UserDeleteView.as_view(), name='user_delete'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Batch Management
    path('batches/', views.BatchListView.as_view(), name='batch_list'),
    path('batches/add/', views.BatchCreateView.as_view(), name='batch_add'),
    path('batches/<int:pk>/edit/', views.BatchUpdateView.as_view(), name='batch_edit'),
    path('batches/<int:pk>/delete/', views.BatchDeleteView.as_view(), name='batch_delete'),

    # Student Management
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/add/', views.StudentCreateView.as_view(), name='student_add'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('students/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_edit'),
    path('students/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student_delete'),
    path('students/export/', views.export_students, name='export_students'),
    path('students/import/', views.import_students, name='import_students'),
    path('students/bulk-import/', views.import_students, name='bulk_import_students'),
    path('students/search/', views.search_student, name='search_student'),
    path('students/delete-all/', views.delete_all_students, name='delete_all_students'),
    path('students/<int:pk>/certificate/', views.print_student_certificate, name='print_certificate'),
    path('students/<int:pk>/export-results/', views.export_student_results, name='export_student_results'),
    path('students/<int:pk>/print-result/', views.print_student_result, name='print_student_result'),

    # Comprehensive Results (New System)
    path('comprehensive-results/list/', views.comprehensive_results_list, name='comprehensive_results_list'),
    path('comprehensive-results/upload/', views.bulk_upload_comprehensive_results, name='bulk_upload_comprehensive_results'),
    path('comprehensive-results/export/<int:level_id>/', views.export_comprehensive_results_view, name='export_comprehensive_results'),
    path('comprehensive-results/print/<int:pk>/', views.print_student_result, name='print_student_result'),
    path('comprehensive-results/terms/export/', views.export_application_terms_view, name='export_terms'),

    # Student Results & Promotion
    path('final-results/', views.StudentResultListView.as_view(), name='results_list'),
    path('final-results/<int:pk>/delete/', views.StudentResultDeleteView.as_view(), name='result_delete'),
    path('final-results/delete-all/', views.delete_all_results, name='delete_all_results'),
    path('final-results/bulk-delete/', views.bulk_delete_results, name='bulk_delete_results'),
    path('promotion/', views.promote_students, name='promote_students'),
    
    # صفحة النتائج العامة
    path('public-results/', views.public_results, name='public_results'),

    # AJAX
    path('ajax/load-levels/', views.load_levels, name='ajax_load_levels'),
]