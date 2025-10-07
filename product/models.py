from django.db import models
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from cloudinary.models import CloudinaryField
from cloudinary.uploader import destroy
import cloudinary
import logging
from django.db import transaction
loggerP = logging.getLogger('Product')
loggerPV = logging.getLogger('ProductVariant')


def parse_path(url):
    """
    Parse Cloudinary URL to get public_id
    """
    try:
        if not url:
            return None
        
        # Tách lấy phần sau '/upload/'
        parts = url.split('/upload/')
        if len(parts) < 2:
            return None
        
        # Lấy phần path sau version (v1234567890)
        path_parts = parts[1].split('/')
        
        # Bỏ version number (vxxxxxxxx) nếu có
        if path_parts[0].startswith('v') and path_parts[0][1:].isdigit():
            path_parts = path_parts[1:]
        
        # Join lại và bỏ extension
        public_id = '/'.join(path_parts)
        
        # Bỏ extension (.jpg, .png, etc.)
        if '.' in public_id:
            public_id = public_id.rsplit('.', 1)[0]
        
        return public_id
    except Exception as e:
        loggerP.error(f"Error parsing Cloudinary URL {url}: {e}")
        return None
    

def is_new_upload(image_field):
        """
        Kiểm tra xem có phải là file mới upload không
        (chưa có trên Cloudinary)
        """
        if not image_field:
            return False
        
        # Kiểm tra xem có phải là uploaded file không
        is_uploaded_file = isinstance(
            image_field, 
            (InMemoryUploadedFile, TemporaryUploadedFile)
        )
        
        # Hoặc là CloudinaryResource nhưng chưa có public_id
        if hasattr(image_field, 'public_id'):
            return False  # Đã có trên Cloudinary
        
        return is_uploaded_file

def get_public_id(image_field):
    """
    Lấy public_id an toàn
    Trả về None nếu:
    - image_field là None
    - image_field là file mới upload (chưa có public_id)
    """
    if not image_field:
        return None
    
    # Nếu là file mới upload, chưa có public_id
    if is_new_upload(image_field):
        return None
    
    # Nếu là CloudinaryResource có public_id
    if hasattr(image_field, 'public_id'):
        return image_field.public_id
    
    return None

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True,verbose_name="Tên sản phẩm")
    slug = models.SlugField(max_length=255, unique=True,verbose_name="Đường dẫn")
    description = models.TextField(blank=True, null=True,verbose_name="Mô tả")
    code = models.CharField(max_length=100, unique=True,verbose_name="Mã sản phẩm")
    origin_price = models.FloatField(blank=True,verbose_name="Giá gốc",default=0)
    category = models.ForeignKey('category.Category',null=True,blank=True, on_delete=models.SET_NULL, related_name='products',verbose_name="Danh mục")
    available = models.BooleanField(default=True,verbose_name="Còn hàng")### tình trạng còn hàng hay không
    image = CloudinaryField(blank=True, null=True,verbose_name="Hình ảnh")

    ### df column
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    

    def save(self, *args, **kwargs):

        old_image_public_id = None
        
        if self.pk:
            try:
                # Lấy instance gốc từ DB
                original = Product.objects.select_for_update().get(pk=self.pk)
                
                # Lấy public_id của ảnh cũ (từ DB)
                original_public_id = get_public_id(original.image)
                
                # Kiểm tra xem có thay đổi image field không
                # Trường hợp 1: Xóa ảnh (self.image = None hoặc '')
                if original.image and not self.image:
                    old_image_public_id = original_public_id
                    loggerP.info(
                        f"Image removed for Product {self.pk}. "
                        f"Will delete: {old_image_public_id}"
                    )
                
                # Trường hợp 2: Upload ảnh mới
                elif is_new_upload(self.image):
                    # Đây là file mới upload, chưa có public_id
                    # Sau khi save, Django-Cloudinary sẽ tự động upload lên Cloudinary
                    if original_public_id:
                        old_image_public_id = original_public_id
                        loggerP.info(
                            f"New image uploaded for Product {self.pk}. "
                            f"Will delete old: {old_image_public_id}"
                        )
                
                # Trường hợp 3: Thay đổi từ ảnh này sang ảnh khác (cả 2 đều đã có trên Cloudinary)
                else:
                    current_public_id = get_public_id(self.image)
                    
                    if original_public_id and current_public_id:
                        if original_public_id != current_public_id:
                            old_image_public_id = original_public_id
                            loggerP.info(
                                f"Image changed for Product {self.pk}. "
                                f"Old: {original_public_id}, New: {current_public_id}"
                            )
            
            except Product.DoesNotExist:
                loggerP.warning(f"Product {self.pk} not found in database")
        

        super().save(*args, **kwargs)

        if old_image_public_id:
            try:
                result = cloudinary.uploader.destroy(
                    old_image_public_id,
                    invalidate=True,
                    resource_type='image'
                )
                loggerP.info(
                    f"Deleted old image {old_image_public_id} "
                    f"for Product {self.pk}: {result}"
                )
            except Exception as e:
                # Chỉ log lỗi, không raise exception
                loggerP.error(
                    f"Failed to delete old image {old_image_public_id} "
                    f"for Product {self.pk}: {e}"
                )
        
        # Log ảnh hiện tại
        if self.image:
            current_id = get_public_id(self.image)
            if current_id:
                loggerP.info(
                    f"Current image for Product {self.pk}: "
                    f"{current_id} - {self.image.url}"
                )
            else:
                loggerP.info(
                    f"New image uploaded for Product {self.pk}, "
                    f"will have public_id after save"
                )

    def delete(self, *args, **kwargs):
        """
        Xóa sản phẩm và ảnh trên Cloudinary
        """
        image_public_id = get_public_id(self.image)
        
        if image_public_id:
            loggerP.info(
                f"Preparing to delete image for Product {self.pk}: {image_public_id}"
            )
        
        # Xóa record trước
        result = super().delete(*args, **kwargs)
        
        # Sau đó xóa ảnh trên Cloudinary
        if image_public_id:
            try:
                destroy_result = cloudinary.uploader.destroy(
                    image_public_id,
                    invalidate=True,
                    resource_type='image'
                )
                loggerP.info(
                    f"Deleted image {image_public_id} "
                    f"for Product {self.pk}: {destroy_result}"
                )
            except Exception as e:
                loggerP.error(
                    f"Failed to delete image {image_public_id} "
                    f"for Product {self.pk}: {e}"
                )
        
        return result

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"
        ordering = ['-image']
    

class VariantType(models.Model):
    name = models.CharField(max_length=255, unique=True,verbose_name="Tên loại biến thể")

    ### loại variant ví dụ như màu sắc,kích thước,chất liệu
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Loại biến thể"
        verbose_name_plural = "Loại biến thể"
        ordering = ['name']

class Variant(models.Model):
    name = models.CharField(max_length=255,verbose_name="Tên biến thể")
    v_type = models.ForeignKey(VariantType, on_delete=models.CASCADE, related_name='variants',verbose_name="Loại biến thể")

    ### biến thể cụ thể như size S,M chất liệu cotton,...
    def __str__(self):
        return f"{self.name} - {self.v_type.name}"
    
    class Meta:
        verbose_name = "Biến thể"
        verbose_name_plural = "Biến thể"
        ordering = ['name','v_type']
    
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

        old_image_public_id = None
        
        if self.pk:
            try:
                # Lấy instance gốc từ DB
                original = ProductVariant.objects.select_for_update().get(pk=self.pk)
                
                # Lấy public_id của ảnh cũ (từ DB)
                original_public_id = get_public_id(original.image)
                
                # Kiểm tra xem có thay đổi image field không
                # Trường hợp 1: Xóa ảnh (self.image = None hoặc '')
                if original.image and not self.image:
                    old_image_public_id = original_public_id
                    loggerP.info(
                        f"Image removed for Product Variant {self.pk}. "
                        f"Will delete: {old_image_public_id}"
                    )
                
                # Trường hợp 2: Upload ảnh mới
                elif is_new_upload(self.image):
                    # Đây là file mới upload, chưa có public_id
                    # Sau khi save, Django-Cloudinary sẽ tự động upload lên Cloudinary
                    if original_public_id:
                        old_image_public_id = original_public_id
                        loggerP.info(
                            f"New image uploaded for Product Variant {self.pk}. "
                            f"Will delete old: {old_image_public_id}"
                        )
                
                # Trường hợp 3: Thay đổi từ ảnh này sang ảnh khác (cả 2 đều đã có trên Cloudinary)
                else:
                    current_public_id = get_public_id(self.image)
                    
                    if original_public_id and current_public_id:
                        if original_public_id != current_public_id:
                            old_image_public_id = original_public_id
                            loggerP.info(
                                f"Image changed for Product Variant {self.pk}. "
                                f"Old: {original_public_id}, New: {current_public_id}"
                            )
            
            except ProductVariant.DoesNotExist:
                loggerP.warning(f"Product Variant {self.pk} not found in database")
        

        super().save(*args, **kwargs)

        if old_image_public_id:
            try:
                result = cloudinary.uploader.destroy(
                    old_image_public_id,
                    invalidate=True,
                    resource_type='image'
                )
                loggerP.info(
                    f"Deleted old image {old_image_public_id} "
                    f"for Product Variant {self.pk}: {result}"
                )
            except Exception as e:
                # Chỉ log lỗi, không raise exception
                loggerP.error(
                    f"Failed to delete old image {old_image_public_id} "
                    f"for Product Variant {self.pk}: {e}"
                )
        
        # Log ảnh hiện tại
        if self.image:
            current_id = get_public_id(self.image)
            if current_id:
                loggerP.info(
                    f"Current image for Product {self.pk}: "
                    f"{current_id} - {self.image.url}"
                )
            else:
                loggerP.info(
                    f"New image uploaded for Product {self.pk}, "
                    f"will have public_id after save"
                )

    def delete(self, *args, **kwargs):
        """
        Xóa sản phẩm và ảnh trên Cloudinary
        """
        image_public_id = get_public_id(self.image)
        
        if image_public_id:
            loggerP.info(
                f"Preparing to delete image for Product {self.pk}: {image_public_id}"
            )
        
        # Xóa record trước
        result = super().delete(*args, **kwargs)
        
        # Sau đó xóa ảnh trên Cloudinary
        if image_public_id:
            try:
                destroy_result = cloudinary.uploader.destroy(
                    image_public_id,
                    invalidate=True,
                    resource_type='image'
                )
                loggerP.info(
                    f"Deleted image {image_public_id} "
                    f"for Product Variant {self.pk}: {destroy_result}"
                )
            except Exception as e:
                loggerP.error(
                    f"Failed to delete image {image_public_id} "
                    f"for Product Variant {self.pk}: {e}"
                )
        
        return result

    class Meta:
        verbose_name = "Biến thể SP"
        verbose_name_plural = "Biến thể SP"
        ordering = ['-image','product']