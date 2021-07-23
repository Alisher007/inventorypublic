from django.http import HttpResponse
import datetime
import json
from num2words import num2words
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, reverse, redirect, render
from django.utils import timezone
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from .forms import AddToCartForm, PaymentForm, CustomerForm
from .models import Product, OrderItem, Order, Category, Payment, Customer, Tax, Logo
from .utils import get_or_set_order_session



class ProductListView(generic.ListView):
    template_name = 'cart/product_list.html'

    def get_queryset(self):
        print(' ProductListView')
        qs = Product.objects.filter(active=True)
        category = self.request.GET.get('category', None)
        print(category, ' category')
        if category:
            qs = qs.filter(Q(primary_category__name=category) |
                           Q(secondary_categories__name=category)).distinct()
            return qs

        title = self.request.GET.get('title', None)
        print(title, ' title')
        if title:
            qs = qs.filter(title__icontains=title).distinct()
        print(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context.update({
            "categories": Category.objects.values("name")
        })
        return context


class ProductDetailView(generic.DetailView):
    template_name = 'cart/product_detail2.html'
    def get_queryset(self):
        return Product.objects.filter(active=True, slug=self.kwargs["slug"])

class CustomerView(generic.TemplateView):
    template_name = "cart/customer_view.html"

    def get_context_data(self, **kwargs):
        context = super(CustomerView, self).get_context_data(**kwargs)
        order = get_or_set_order_session(self.request)
        customer = Customer.objects.filter(order=order)
        context["customer"] = customer.first()
        return context

class CustomerDeleteView(generic.View):
    def get(self, request, *args, **kwargs):
        order_item = get_object_or_404(Customer, id=kwargs['pk'])
        order_item.delete()
        return redirect("cart:customer")

class CustomerCreateView(generic.CreateView):
    template_name = 'cart/customer.html'
    form_class = CustomerForm

    def get_success_url(self):
        return reverse("cart:customer")

    def form_valid(self, form):
        order = get_or_set_order_session(self.request)

        item_filter = Customer.objects.filter(
            order=order,
        )

        if item_filter.exists():
            messages.info(request,'You can create only one customer per order')
            return reverse("cart:customer")
        else:
            new_item = form.save(commit=False)
            new_item.order = order
            new_item.save()

        return super(CustomerCreateView, self).form_valid(form)

class CustomerUpdateView(generic.UpdateView):
    template_name = 'cart/customer.html'
    form_class = CustomerForm

    def get_success_url(self):
        return reverse("cart:customer")
    
    def get_queryset(self):
        return Customer.objects.filter(pk=self.kwargs["pk"])

    def form_valid(self, form):
        form.save()
        return super(CustomerUpdateView, self).form_valid(form)

class PaymentCreateView(generic.CreateView):
    template_name = 'cart/payment.html'
    form_class = PaymentForm

    def get_success_url(self):
        return reverse("cart:checkout")

    def form_valid(self, form):
        order = get_or_set_order_session(self.request)

        new_item = form.save(commit=False)
        new_item.order = order
        amount = int(str(form.cleaned_data['price']).replace('.',''))
        new_item.price = form.cleaned_data['price'] * 100
        new_item.save()

        return super(PaymentCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(PaymentCreateView, self).get_context_data(**kwargs)
        context['order'] = get_or_set_order_session(self.request)
        return context

class PaymentUpdateView(generic.UpdateView):
    template_name = 'cart/payment.html'
    form_class = PaymentForm
    
    def get_object(self):
        return get_object_or_404(Payment, pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse("cart:checkout")
    
    def get_initial(self, *args, **kwargs):
        initial = super(PaymentUpdateView, self).get_initial(**kwargs)
        payment = self.get_object()
        initial['method'] = payment.method
        initial['price'] = payment.get_price()
        return initial

    def form_valid(self, form):
        new_item = form.save(commit=False)
        amount = int(str(form.cleaned_data['price']).replace('.',''))
        new_item.price = form.cleaned_data['price'] * 100
        new_item.save()

        return super(PaymentUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(PaymentUpdateView, self).get_context_data(**kwargs)
        context['order'] = get_or_set_order_session(self.request)
        return context

class CartView(generic.TemplateView):
    template_name = "cart/cart.html"

    def get_context_data(self, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)
        context["order"] = get_or_set_order_session(self.request)
        return context


class IncreaseQuantityView(generic.View):
    def get(self, request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        if order_item.quantity + 1 > order_item.product.stock:
            messages.info(request,'you don\'t have so much in stock')
            return redirect("cart:summary")
        order_item.quantity += 1
        order_item.save()
        return redirect("cart:summary")

class ModifyPriceView(generic.View):
    def post(self, request, *args, **kwargs):
        pk = self.request.POST.get('pk', None)
        price = self.request.POST.get('price', None)

        if price:
            price = int( ( float(price.strip()) * 100 ) )
        else:
            return redirect("cart:summary")

        order_item = get_object_or_404(OrderItem, id=pk)
        order_item.discount = int((order_item.product.price - price) / order_item.product.price * 100)
        order_item.price = price
        order_item.save()
        return redirect("cart:summary")

class ModifyPercentView(generic.View):
    def post(self, request, *args, **kwargs):
        pk = self.request.POST.get('pk', None)
        discount = self.request.POST.get('discount', None)

        if discount:
            discount = int(  float(discount.strip() ) )
        else:
            return redirect("cart:summary")

        order_item = get_object_or_404(OrderItem, id=pk)
        order_item.price = int((100 - discount) / 100 * order_item.product.price)
        order_item.discount = discount
        order_item.save()
        return redirect("cart:summary")


class ProductToOrderView(generic.View):
    def get(self, request, *args, **kwargs):
        order = get_or_set_order_session(self.request)
        product = get_object_or_404(Product, slug=self.kwargs["slug"])

        item_filter = order.items.filter(
            product=product,
        )

        if item_filter.exists():
            return redirect("cart:summary")
        else:
            new_item = OrderItem()
            new_item.product = product
            new_item.order = order
            new_item.quantity = 1
            new_item.price = product.price
            new_item.save()
        return redirect("cart:summary")

class DecreaseQuantityView(generic.View):
    def get(self, request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        if order_item.quantity <= 1:
            order_item.delete()
        else:
            order_item.quantity -= 1
            order_item.save()
        return redirect("cart:summary")


class RemoveFromCartView(generic.View):
    def get(self, request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        order_item.delete()
        return redirect("cart:summary")

class RemovePaymentView(generic.View):
    def get(self, request, *args, **kwargs):
        order_item = get_object_or_404(Payment, id=kwargs['pk'])
        order_item.delete()
        return redirect("cart:checkout")


class ThankYouView(generic.TemplateView):
    template_name = 'cart/thanks.html'


class OrderDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'order.html'
    queryset = Order.objects.all()
    context_object_name = 'order'

class CheckoutConfirmView(generic.View):
    def get(self, request, *args, **kwargs):
        order = get_or_set_order_session(request)

        if order.get_total_payment_minus_raw() != 0:
            messages.info(request,'You should pay first')
            return redirect('cart:checkout')

        order_item = OrderItem.objects.filter(order=order)
        for oo in order_item:
            product = Product.objects.get(id=oo.product.id)
            if product.stock - oo.quantity == 0:
                product.stock = 0
                product.active = False
            else:
                product.stock -= oo.quantity
        product.save()
        order.ordered = True
        order_id = order.id
        order.save()
        return redirect('cart:print', order_id)

class CheckoutView(generic.TemplateView):
    template_name = 'cart/checkout.html'

    def get_context_data(self, **kwargs):
        context = super(CheckoutView, self).get_context_data(**kwargs)
        order = get_or_set_order_session(self.request)
        payment = Payment.objects.filter(order=order)
        customer = Customer.objects.filter(order=order)
        tax = Tax.objects.filter(active=True)
        context["customer"] = customer.first()
        context["order"] = order
        context["payment"] = payment
        context["tax"] = tax.first()
        return context

class PrintView(generic.TemplateView):
    template_name = 'cart/print.html'

    def get_context_data(self, **kwargs):
        context = super(PrintView, self).get_context_data(**kwargs)
        order = get_object_or_404(Order, id=kwargs['pk'])
        customer = Customer.objects.filter(order=order)
        tax = Tax.objects.filter(active=True)
        total = num2words(order.get_total())
        context["customer"] = customer.first()
        context["order"] = order
        context["total"] = total
        context["tax"] = tax.first()
        return context


