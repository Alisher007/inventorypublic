from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save
from django.shortcuts import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

User = get_user_model()

class Logo(models.Model):
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to='product_images')

    def __str__(self):
        return self.name

class Tax(models.Model):
    name = models.CharField(max_length=100)
    percent = models.IntegerField(default=0)
    active = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Taxes"

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Payment(models.Model):
    order = models.ForeignKey(
        "Order", related_name='pays', on_delete=models.CASCADE)
    method = models.ForeignKey(
        "PaymentMethod", related_name='payment_method', on_delete=models.CASCADE)
    price = models.IntegerField(default=0)

    def __str__(self):
        return str(self.pk)
    
    def get_absolute_url(self):
        return reverse("cart:payment-update", kwargs={'pk': self.pk})
    
    def get_delete_url(self):
        return reverse("cart:remove-payment", kwargs={'pk': self.pk})
    
    def get_price(self):
        return "{:.2f}".format(self.price / 100)

class Diamond(models.Model):
    SHAPE_DIAMOND = (
        ('ROUND', 'ROUND'),
        ('OVAL', 'OVAL'),
        ('PRINCESS', 'PRINCESS'),
    )
    QUALITY_DIAMOND = (
        ('GH/VS', 'GH/VS'),
        ('F.Y/VSI', 'F.Y/VSI'),
    )
    shape = models.CharField(max_length=20, choices=SHAPE_DIAMOND)
    quality = models.CharField(max_length=20, choices=QUALITY_DIAMOND)
    quantity = models.PositiveIntegerField(default=1)
    weight = models.IntegerField(default=0)
    product = models.ForeignKey(
        "Product", related_name='diamond', on_delete=models.CASCADE, blank=True, null=True,)

    def __str__(self):
        return str(self.pk)
    
    def get_weight(self):
        return "{:.2f}".format(self.weight / 100)

class Gold(models.Model):
    caliber = models.PositiveIntegerField(default=1)
    weight = models.IntegerField(default=0)
    product = models.ForeignKey(
        "Product", related_name='gold', on_delete=models.CASCADE, blank=True, null=True,)

    def __str__(self):
        return str(self.pk)
    
    def get_weight(self):
        return "{:.2f}".format(self.weight / 100)

class Customer(models.Model):
    name = models.CharField(max_length=50)
    order = models.ForeignKey(
        "Order", related_name='customer_order', on_delete=models.CASCADE)
    lastname = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    email = models.EmailField(_('email address'), unique=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("cart:customer-update", kwargs={'pk': self.pk})
    
    def get_delete_url(self):
        return reverse("cart:customer-delete", kwargs={'pk': self.pk})


class Product(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    barcode = models.CharField(max_length=150, default='n1016')
    image = models.ImageField(upload_to='product_images')
    description = models.TextField()
    price = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)
    primary_category = models.ForeignKey(
        Category, related_name='primary_products', blank=True, null=True, on_delete=models.CASCADE)
    secondary_categories = models.ManyToManyField(Category, blank=True)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def get_weight(self):
        total = 0
        for diamond in self.diamond.all():
            total += diamond.weight
        for gold in self.gold.all():
            total += gold.weight
        return total

    def get_absolute_url(self):
        return reverse("cart:product-detail", kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse("staff:product-update", kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse("staff:product-delete", kwargs={'pk': self.pk})

    def get_price(self):
        return "{:.2f}".format(self.price / 100)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Product,self).save(*args, **kwargs)

    @property
    def in_stock(self):
        return self.stock > 0


class OrderItem(models.Model):
    order = models.ForeignKey(
        "Order", related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.IntegerField(default=0)
    discount = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"

    def get_discount_price(self):
        return (self.product.price - self.price) / 100

    def get_raw_total_item_price(self):
        return self.quantity * self.price

    def get_raw_total_original_item_price(self):
        return self.quantity * self.product.price

    def get_total_original_item_price(self):
        price = self.get_raw_total_original_item_price() 
        return "{:.2f}".format(price / 100)

    def get_total_item_price(self):
        price = self.get_raw_total_item_price() 
        return "{:.2f}".format(price / 100)
    
    def get_tax_raw(self):
        subtotal = self.get_raw_total_item_price()
        tax = Tax.objects.filter(active=True)
        return subtotal * (tax.first().percent / 100)

    def get_tax(self):
        subtotal = self.get_tax_raw()
        return "{:.2f}".format(subtotal / 100)
    
    def get_total_item_price_tax(self):
        price = self.get_raw_total_item_price()  + self.get_tax_raw()
        return "{:.2f}".format(price / 100)
    
    def get_price(self):
        return "{:.2f}".format(self.price / 100)
    
    def get_absolute_url(self):
        return reverse("cart:certificate-detail", kwargs={'pk': self.pk})


class Order(models.Model):
    user = models.ForeignKey(
        User, related_name='order_user', blank=True, null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.reference_number

    @property
    def reference_number(self):
        return f"ORDER-{self.pk}"

    def get_customer(self):
        return self.customer_order.exists()

    def get_customer_name(self):
        return self.customer_order.first()

    def get_raw_subtotal(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_raw_total_item_price()
        return total

    def get_qty(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.quantity
        return total

    def get_weight(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.product.get_weight()
        return total

    def get_subtotal(self):
        subtotal = self.get_raw_subtotal()
        return "{:.2f}".format(subtotal / 100)

    def get_tax_raw(self):
        subtotal = self.get_raw_subtotal()
        tax = Tax.objects.filter(active=True)
        return subtotal * (tax.first().percent / 100)

    def get_tax(self):
        subtotal = self.get_tax_raw()
        return "{:.2f}".format(subtotal / 100)

    def get_raw_total(self):
        subtotal = self.get_raw_subtotal()
        # add tax, add delivery, subtract discounts
        # total = subtotal - discounts + tax + delivery
        return subtotal + self.get_tax_raw()

    def get_total(self):
        total = self.get_raw_total()
        return "{:.2f}".format(total / 100)
    
    def get_raw_subtotal_payment(self):
        total = 0
        for pay in self.pays.all():
            total += pay.price
        return total

    def get_total_payment(self):
        total = self.get_raw_subtotal_payment()
        return "{:.2f}".format(total / 100)
    
    def get_total_payment_minus_raw(self):
        total = self.get_raw_total() - self.get_raw_subtotal_payment()
        return total

    def get_total_payment_minus(self):
        total = self.get_raw_total() - self.get_raw_subtotal_payment()
        return "{:.2f}".format(total / 100)


def pre_save_product_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)


pre_save.connect(pre_save_product_receiver, sender=Product)
