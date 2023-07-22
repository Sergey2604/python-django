from django.urls import path

from .views import process_get_view, file_download, user_form, handle_file_upload

app_name = 'requestdataapp'

urlpatterns = [
    path('get/', process_get_view, name='get-view'),
    path('file/', file_download, name='file-upload'),
    path("bio/", user_form, name="user-form"),
    path("upload/", handle_file_upload, name="file-upload-form"),
]
