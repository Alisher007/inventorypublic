from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CartView.as_view(), name='summary'),
    path('shop/', views.ProductListView.as_view(), name='product-list'),
    path('modifyprice/', views.ModifyPriceView.as_view(), name='modifyprice'),
    path('modifypercent/', views.ModifyPercentView.as_view(), name='modifypercent'),
    path('payment-create/', views.PaymentCreateView.as_view(), name='payment-create'),
    path('customer/', views.CustomerView.as_view(), name='customer'),
    path('customer-create/', views.CustomerCreateView.as_view(), name='customer-create'),
    path('customer-delete/<pk>/', views.CustomerDeleteView.as_view(), name='customer-delete'),
    path('customer-update/<pk>/', views.CustomerUpdateView.as_view(), name='customer-update'),
    path('payment-update/<pk>/', views.PaymentUpdateView.as_view(), name='payment-update'),
    path('remove-payment/<pk>/',
         views.RemovePaymentView.as_view(), name='remove-payment'),
    path('shop/<slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('product-to-order/<slug>/',
         views.ProductToOrderView.as_view(), name='product-to-order'),
    path('increase-quantity/<pk>/',
         views.IncreaseQuantityView.as_view(), name='increase-quantity'),
    path('decrease-quantity/<pk>/',
         views.DecreaseQuantityView.as_view(), name='decrease-quantity'),
    path('remove-from-cart/<pk>/',
         views.RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('thank-you/', views.ThankYouView.as_view(), name='thank-you'),
    path('orders/<pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('checkout-confirm/', views.CheckoutConfirmView.as_view(), name='checkout-confirm'),
    path('print/<pk>/', views.PrintView.as_view(), name='print'),

]
