from django.urls import path
from . import views

urlpatterns = [
    # path('', views.session_list, name='session_list'),                     # choisir / créer session
    path('', views.home, name='home'),  # page d'accueil
    path('session/create/', views.create_session, name='create_session'),  # create + upload CSV
    path('scan/<int:session_id>/', views.scan_qr, name='scan_qr'),        # scanner page (public)
    path('result/<int:session_id>/', views.checkin_result, name='checkin_result'),
    path('admin/session/<int:session_id>/', views.session_admin, name='session_admin'),  # live table
    path('session/<int:session_id>/export/', views.export_session_csv, name='export_session_csv'),
    path('session/<int:session_id>/close/', views.close_session, name='close_session'),
    path('ajax/upload_csv/', views.upload_csv_ajax, name='upload_csv_ajax'),  # upload via AJAX
    path('tableau/<int:session_id>/', views.live_table, name='live_table'),
    path('tableau/<int:session_id>/data/', views.live_table_data, name='live_table_data'),
]
