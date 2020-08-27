from django.urls import path
from django.views.generic import TemplateView
from .views import (
	HomeView, 
	CheckoutView, 
	ProductDetail,
	add_to_cart,
	remove_from_cart,
	remove_single_from_cart,
	PaymentView,
	OrderSummaryView,
	payment_complete,
	DonorListView,
	DonorCreateView,
	DonorUpdateView,
	DonorDeleteView,
	OrderItemListView,
	#Dashboard,
	CustomerListView,
	CustomerDeleteView,
	DownloadPDF,
	ViewPDF,

	
	)



urlpatterns = [
	#path('', Dashboard.as_view(), name='home'),
    path('', HomeView.as_view(), name='home'),
    
    path('donor_list/', DonorListView.as_view(), name='donor_list'),
    path('new_donor/', DonorCreateView.as_view(), name= 'new_donor'),

    path('donor_update/<int:pk>/', DonorUpdateView.as_view(), name='donor_update'),
    path('donor_delete/<int:pk>/delete/', DonorDeleteView.as_view(), name='donor_delete' ),


    
    path('customer_list/', CustomerListView.as_view(), name='customer_list'),
    path('customer_delete/<int:pk>/delete/', CustomerDeleteView.as_view(), name='customer_delete' ),

    
    path('pdf_download/', DownloadPDF.as_view(), name="pdf_download"),
    path('pdf_view/',ViewPDF.as_view(), name="pdf_view"),

    path('order_list/', OrderItemListView.as_view(), name='order_list'),
    path('add-to-cart/<slug>/', add_to_cart, name='add_to_cart'),
    path('accounts/profile/' , TemplateView.as_view(template_name="home.html")),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove_from_cart'),
    path('remove-single-from-cart/<slug>/', remove_single_from_cart, name='remove_single_from_cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('product/<slug>/', ProductDetail.as_view(), name='product'),
    path('order-summary/', OrderSummaryView.as_view(), name='order_summary'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('payment-complete', payment_complete, name="payment_complete"),






]