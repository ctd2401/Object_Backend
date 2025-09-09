from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from math import ceil
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import Http404


from product.models import *
from django.db.models import Q
from .serializers import *


class AllProduct(APIView):
    """
    API để xử lý danh sách sản phẩm (GET) và tạo sản phẩm (POST).
    """


    def get(self, request):
        try:
            page = request.query_params.get("page", 1)
            limit = request.query_params.get("limit", 10)
            keyword = request.query_params.get("keyword", None)
            try:
                page = int(page)
                limit = int(limit)
            except ValueError:
                return Response(
                    {"error": "Page and limit must be integers."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            products = Product.objects.filter(available=True).order_by('name')
            # Lọc theo keyword nếu có
            if keyword:
                products = products.filter(Q(name__icontains=keyword) |Q(code__icontains=keyword))

            # Tính toán phân trang
            total_items = products.count()
            total_pages = ceil(total_items / limit)
            start = (page - 1) * limit
            end = start + limit
            paginated_Product = products[start:end]

            serializer = ProductMenuSerializer(paginated_Product,many=True)   
            return Response(
                {
                    "total_items": total_items,
                    "total_pages": total_pages,
                    "current_page": page,
                    "page_size": limit,
                    "results": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        cat_name = request.data.get("name")

        try:
            if Product.objects.filter(name=cat_name).exists():
                return Response(
                    {"error": "Product with this name already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class ProductDetailView(APIView):
    """
    API để xử lý chi tiết, cập nhật và xóa sản phẩm.
    """


    parser_classes = [MultiPartParser, FormParser]


    def get(self, request, pk):
        product = Product.objects.prefetch_related('productvariant_product').get(pk=pk)
        if product.available == False:
            return Response(
                {"error": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        pvs = ProductVariant.objects.filter(product=product)
        data_variants = {key: [] for key in pvs.values_list('variant__v_type__name',flat=True).distinct()}
        for pv in pvs:
            if pv.variant.v_type.name in data_variants.keys():
                data_variants[pv.variant.v_type.name].append(
                {
                    "id": pv.variant.id,
                    "name": pv.variant.name,
                    "type": pv.variant.v_type.name,
                    "price_diff": pv.price_diff,
                    "available": pv.available,
                    "image": pv.image.url if pv.image else None
                }
            )

        data_return = {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "description": product.description,
            "code": product.code,
            "origin_price": product.origin_price,
            "category": product.category.name if product.category else None,
            "available": product.available,
            "image": product.image.url if product.image else None,
            "created_at": product.created_at,
            "updated_at": product.updated_at,
            "variants": data_variants
        }
        
        
        return Response(data_return, status=status.HTTP_200_OK)

    def put(self, request, pk):
        try:
            Product = get_object_or_404(Product, pk=pk)
            serializer = UpdateProductSerializer(
                Product, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Http404:
            return Response(
                {"error": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


    def delete(self, request, pk):
        try:
            product = get_object_or_404(Product, pk=pk)
            product.delete()
            return Response(
                {"message": "Product deleted successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


