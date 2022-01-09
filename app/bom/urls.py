from django.urls import path

from bom import views


app_name = 'bom'
urlpatterns = [
    path('items/', views.ItemListAPIView.as_view(), name="item_list"),
    path('items/<id>/', views.ItemDetailsAPIView.as_view(), name="item_details"),
    path('file/validate/', views.FileValidateAPIView.as_view(), name="file_validate"),
    path('file/upload/', views.FileUploadAPIView.as_view(), name="file_upload"),
]
