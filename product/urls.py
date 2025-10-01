from django.urls import path
from .views import *
from .log import *

app_name = "products"

urlpatterns = [
    path("products", AllProduct.as_view(), name="list product"),
    path("products/<int:pk>", ProductDetailView.as_view(), name="detail product"),


    ### log
    path("log/image_product",view_Product_logs,name='product log view'),
    path("log/image_product_variant",view_Product_Variant_logs,name='product variant log view'),
    path("log/image_product/del",delete_logs_product,name='product log delete'),
    path("log/image_product_variant/del",delete_logs_product_variant,name='product variant log delete')
]
