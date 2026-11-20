from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem
from products.models import Product
from products.serializers import ProductSerializer
from accounts.serializers import UserSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price', 'line_total')
        read_only_fields = ('id', 'product', 'product_name', 'price', 'line_total')

    def get_line_total(self, obj):
        return round(float(obj.price * obj.quantity), 2)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data.get('product'):
            data['product'] = {
                'id': None,
                'name': instance.product_name or 'Archived Product',
                'price': str(instance.price),
                'stock': 0,
                'image_url': None,
                'category': {'name': 'Archived'}
            }
        return data

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer = UserSerializer(source='user', read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'customer',
            'total_amount',
            'status',
            'created_at',
            'items'
        )
        read_only_fields = ('id', 'customer', 'total_amount', 'created_at', 'items')

class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)

class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True, required=False)
    product_id = serializers.IntegerField(min_value=1, required=False)
    quantity = serializers.IntegerField(min_value=1, required=False, default=1)

    def validate(self, attrs):
        items = attrs.get('items', [])
        single_pid = attrs.get('product_id')
        single_qty = attrs.get('quantity', 1)

        normalized_items = []
        if single_pid is not None:
            normalized_items.append({'product_id': single_pid, 'quantity': single_qty})
        elif items:
            normalized_items.extend(items)
        else:
            raise serializers.ValidationError("Order must include at least one product.")

        attrs['normalized_items'] = normalized_items
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        items_data = validated_data['normalized_items']

        with transaction.atomic():
            calculated_total = 0
            order_items_to_create = []

            for item_spec in items_data:
                product_id = item_spec['product_id']
                requested_qty = item_spec['quantity']

                try:
                    product = Product.objects.select_for_update().get(id=product_id)
                except Product.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Product with ID {product_id} does not exist."
                    )

                if product.stock < requested_qty:
                    raise serializers.ValidationError(
                        f"Insufficient stock available for '{product.name}'. Available: {product.stock}, Requested: {requested_qty}."
                    )

                unit_price = product.price
                item_total = unit_price * requested_qty
                calculated_total += item_total

                product.stock -= requested_qty
                product.save(update_fields=['stock'])

                order_items_to_create.append({
                    'product': product,
                    'quantity': requested_qty,
                    'price': unit_price
                })

            order = Order.objects.create(
                user=user,
                total_amount=calculated_total,
                status='Placed'
            )

            for item_spec in order_items_to_create:
                OrderItem.objects.create(
                    order=order,
                    product=item_spec['product'],
                    product_name=item_spec['product'].name,
                    quantity=item_spec['quantity'],
                    price=item_spec['price']
                )

            return order

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('status',)

    def validate_status(self, value):
        if value not in ['Placed', 'Completed']:
            raise serializers.ValidationError("Status must be either 'Placed' or 'Completed'.")
        return value
