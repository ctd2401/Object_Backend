from django.db import models
from cloudinary.models import CloudinaryField
from cloudinary.uploader import destroy
import logging
# from django.db import transaction
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
import cloudinary
logger = logging.getLogger("Category")
def parse_path(url):
    public_id = url.split('/')[-1].rsplit('.', 1)[0]
    return public_id


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

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True,verbose_name="Tên danh mục")
    slug = models.SlugField(max_length=255, unique=True,verbose_name="Đường dẫn")
    description = models.TextField(blank=True, null=True,verbose_name="Mô tả")
    code = models.CharField(max_length=100, unique=True,verbose_name="Mã danh mục")
    image = CloudinaryField(blank=True, null=True,verbose_name="Hình ảnh")
    active = models.BooleanField(default=True,verbose_name='Trạng thái')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):

        old_image_public_id = None
        
        if self.pk:
            try:
                # Lấy instance gốc từ DB
                original = Category.objects.select_for_update().get(pk=self.pk)
                
                # Lấy public_id của ảnh cũ (từ DB)
                original_public_id = get_public_id(original.image)
                
                # Kiểm tra xem có thay đổi image field không
                # Trường hợp 1: Xóa ảnh (self.image = None hoặc '')
                if original.image and not self.image:
                    old_image_public_id = original_public_id
                    logger.info(
                        f"Image removed for Category {self.pk}. "
                        f"Will delete: {old_image_public_id}"
                    )
                
                # Trường hợp 2: Upload ảnh mới
                elif is_new_upload(self.image):
                    # Đây là file mới upload, chưa có public_id
                    # Sau khi save, Django-Cloudinary sẽ tự động upload lên Cloudinary
                    if original_public_id:
                        old_image_public_id = original_public_id
                        logger.info(
                            f"New image uploaded for Category {self.pk}. "
                            f"Will delete old: {old_image_public_id}"
                        )
                
                # Trường hợp 3: Thay đổi từ ảnh này sang ảnh khác (cả 2 đều đã có trên Cloudinary)
                else:
                    current_public_id = get_public_id(self.image)
                    
                    if original_public_id and current_public_id:
                        if original_public_id != current_public_id:
                            old_image_public_id = original_public_id
                            logger.info(
                                f"Image changed for Category {self.pk}. "
                                f"Old: {original_public_id}, New: {current_public_id}"
                            )
            
            except Category.DoesNotExist:
                logger.warning(f"Category {self.pk} not found in database")
        

        super().save(*args, **kwargs)

        if old_image_public_id:
            try:
                result = Category.uploader.destroy(
                    old_image_public_id,
                    invalidate=True,
                    resource_type='image'
                )
                logger.info(
                    f"Deleted old image {old_image_public_id} "
                    f"for Category {self.pk}: {result}"
                )
            except Exception as e:
                # Chỉ log lỗi, không raise exception
                logger.error(
                    f"Failed to delete old image {old_image_public_id} "
                    f"for Category {self.pk}: {e}"
                )
        
        # Log ảnh hiện tại
        if self.image:
            current_id = get_public_id(self.image)
            if current_id:
                logger.info(
                    f"Current image for Product {self.pk}: "
                    f"{current_id} - {self.image.url}"
                )
            else:
                logger.info(
                    f"New image uploaded for Product {self.pk}, "
                    f"will have public_id after save"
                )

    def delete(self, *args, **kwargs):
        """
        Xóa sản phẩm và ảnh trên Cloudinary
        """
        image_public_id = get_public_id(self.image)
        
        if image_public_id:
            logger.info(
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
                logger.info(
                    f"Deleted image {image_public_id} "
                    f"for Category {self.pk}: {destroy_result}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to delete image {image_public_id} "
                    f"for Category {self.pk}: {e}"
                )
        
        return result

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ['-image','name']