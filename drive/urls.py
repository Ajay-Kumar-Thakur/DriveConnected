# drive/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('auth/',                         views.google_auth,    name='google_auth'),
    # removed oauth2callback from here
    path('files/',                        views.file_list,      name='drive_list'),
    path('upload/',                       views.file_upload,    name='drive_upload'),
    path('download/<str:file_id>/',       views.file_download,  name='drive_download'),
    path('update/<str:file_id>/',         views.file_update,    name='drive_update'),
    path('delete/<str:file_id>/',         views.file_delete,    name='drive_delete'),
]