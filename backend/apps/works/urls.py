from django.urls import path

from .views import WorkDetailAPIView, WorkListAPIView

app_name = "works"

urlpatterns = [
    path("works/", WorkListAPIView.as_view(), name="api_list"),
    path("works/<str:slug>/", WorkDetailAPIView.as_view(), name="api_detail"),
]
