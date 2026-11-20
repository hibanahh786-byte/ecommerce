from rest_framework import serializers
from .models import Product
from categories.models import Category
from categories.serializers import CategorySerializer

class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    category = CategorySerializer(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'price',
            'stock',
            'image',
            'image_url',
            'category',
            'category_id',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'image_url')
        extra_kwargs = {
            'image': {'required': False, 'allow_null': True}
        }

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value

    def validate_image(self, value):
        if value:
            # Max 5MB
            max_size = 5 * 1024 * 1024
            if value.size > max_size:
                raise serializers.ValidationError("Image file size cannot exceed 5MB.")
            # Check content type / extension
            allowed_extensions = ['jpg', 'jpeg', 'png', 'webp', 'gif']
            ext = value.name.split('.')[-1].lower()
            if ext not in allowed_extensions:
                raise serializers.ValidationError(f"Unsupported image format. Allowed: {', '.join(allowed_extensions)}")
        return value
