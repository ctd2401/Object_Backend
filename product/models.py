from django.db import models
from django.core.exceptions import ValidationError
from cloudinary.models import CloudinaryField
from cloudinary.uploader import destroy
def parse_path(url):
    public_id = url.split('/')[-1].rsplit('.', 1)[0]
    return public_id

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True,verbose_name="Tên sản phẩm")
    slug = models.SlugField(max_length=255, unique=True,verbose_name="Đường dẫn")
    description = models.TextField(blank=True, null=True,verbose_name="Mô tả")
    code = models.CharField(max_length=100, unique=True,verbose_name="Mã sản phẩm")
    origin_price = models.FloatField(blank=True,verbose_name="Giá gốc",default=0)
    category = models.ForeignKey('category.Category',null=True,blank=True, on_delete=models.CASCADE, related_name='products',verbose_name="Danh mục")
    available = models.BooleanField(default=True,verbose_name="Còn hàng")### tình trạng còn hàng hay không
    image = CloudinaryField(blank=True, null=True,verbose_name="Hình ảnh")

    ### df column
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.pk:  # Check if the instance already exists (i.e., not a new object)
            original_instance = Product.objects.get(pk=self.pk)
            if original_instance.image != self.image:
                print("Cloudinary image field has changed!")
                if original_instance.image:
                    destroy(parse_path(original_instance.image.url), invalidate=True)
                else:
                    pass
        
        super().save(*args, **kwargs)
        
    
    def delete(self):
        destroy(parse_path(self.image.url), invalidate=True)
        return super().delete()
    

class VariantType(models.Model):
    name = models.CharField(max_length=255, unique=True,verbose_name="Tên loại biến thể")

    ### loại variant ví dụ như màu sắc,kích thước,chất liệu
    def __str__(self):
        return self.name

class Variant(models.Model):
    name = models.CharField(max_length=255,verbose_name="Tên biến thể")
    v_type = models.ForeignKey(VariantType, on_delete=models.CASCADE, related_name='variants',verbose_name="Loại biến thể")

    ### biến thể cụ thể như size S,M chất liệu cotton,...
    def __str__(self):
        return f"{self.name} - {self.v_type.name}"
    
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='productvariant_product',verbose_name="Sản phẩm")
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='productvariant_variant',verbose_name="Biến thể")
    price_diff = models.FloatField(blank=True,verbose_name="Giá thay đổi",default=0)### thay đổi giá so với giá gốc
    available = models.BooleanField(default=True,verbose_name="Còn hàng")### tình trạng còn hàng để order hay không
    image = CloudinaryField(blank=True, null=True,verbose_name="Hình ảnh")

    class Meta:
        unique_together = ('product', 'variant')

    def __str__(self):
        return f"{self.product.name} - {self.variant.name} - {self.variant.v_type.name} - {"Còn hàng" if self.available else "Hết hàng"}"
    

    def save(self, *args, **kwargs):
        if self.pk:  # Check if the instance already exists (i.e., not a new object)
            original_instance = ProductVariant.objects.get(pk=self.pk)
            if original_instance.image != self.image:
                print("Cloudinary image field has changed!")
                if original_instance.image:
                    destroy(parse_path(original_instance.image.url), invalidate=True)
                else:
                    pass
        
        super().save(*args, **kwargs)
        
    
    def delete(self):
        destroy(parse_path(self.image.url), invalidate=True)
        return super().delete()