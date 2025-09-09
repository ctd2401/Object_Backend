from django.urls import path
from .views import *

app_name = "products"

urlpatterns = [
    path("products", AllProduct.as_view(), name="list product"),
    path("products/<int:pk>", ProductDetailView.as_view(), name="detail product"),
]
