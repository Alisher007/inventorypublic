from django.contrib import admin
from .models import (
    Product, OrderItem, Order, Customer,
    Category, Payment, PaymentMethod, Diamond, Gold, Tax, Logo
)

class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 5
	max_num = 5

class OrderAdmin(admin.ModelAdmin):
	model = Order
	inlines = [OrderItemInline]
	extra = 5

class GoldInline(admin.TabularInline):
	model = Gold
	extra = 1
	max_num = 1

class DiamondInline(admin.TabularInline):
	model = Diamond
	extra = 5
	max_num = 5

class ProductAdmin(admin.ModelAdmin):
	model = Product
	inlines = [GoldInline, DiamondInline]
	prepopulated_fields = {"slug": ("title",)}


admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product, ProductAdmin)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Diamond)
admin.site.register(Gold)
admin.site.register(Payment)
admin.site.register(PaymentMethod)
admin.site.register(Tax)
admin.site.register(Logo)