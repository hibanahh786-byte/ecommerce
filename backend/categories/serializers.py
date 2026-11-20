from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'created_at', 'products_count')
        read_only_fields = ('id', 'created_at')

    def get_products_count(self, obj):
        return obj.products.count()

    def validate_name(self, value):
        trimmed = value.strip()
        if not trimmed:
            raise serializers.ValidationError("Category name cannot be empty.")
        
        # Check uniqueness ignoring case, excluding current instance if updating
        qs = Category.objects.filter(name__iexact=trimmed)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("A category with this name already exists.")
        return trimmed
