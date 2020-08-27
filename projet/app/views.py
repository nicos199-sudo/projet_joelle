from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import (
     TemplateView,
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
    View,
)
from django.contrib.auth.models import User
from .forms import AddressForm, DonorCreateForm
from .models import Item, Order, OrderItem, Address, Payment, Donor
from django.utils import timezone
import json



class HomeView(ListView):
    model = Item
    template_name = 'home.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_customers'] = User.objects.all().count()
        context['total_donors'] = Donor.objects.all().count()
        context['total_orders'] = Order.objects.all().count()
        return context

class CustomerListView(ListView):
    template_name = 'customer.html'
    model = User

class CustomerDeleteView (DeleteView):
    template_name = 'confirm_delete.html'
    model = User
    success_url = reverse_lazy('customer_list')


class DonorListView(ListView):
    template_name = 'donor_list.html'
    model = Donor

class DonorCreateView(CreateView):
    form_class = DonorCreateForm
    template_name = 'new_donor.html'
    success_url = reverse_lazy('home')

class DonorUpdateView(UpdateView):
    model = Donor
    template_name = 'new_donor.html'
    fields = ['name', 'blood_group', 'age' , 'phone', 'address']
    success_url = reverse_lazy('donor_list')

class DonorDeleteView (DeleteView):
    template_name = 'confirm_delete.html'
    model = Donor
    success_url = reverse_lazy('donor_list')


class OrderItemListView(ListView):
    template_name = 'order_list.html'
    model = OrderItem


class ProductDetail(DetailView):
    model = Item
    template_name = 'product.html'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'order': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.success(self.request, "You dont have an active order")
            return redirect('home')


class CheckoutView(View):
    def get(self, *args, **kwargs):
        #address = Address.objects.get(user=self.request.user, default=True)
        form = AddressForm()
        context = {
            'form': form,
            #'address': address
        }
        return render(self.request, 'checkout.html', context)


    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = AddressForm(self.request.POST or None)
        if form.is_valid():
            street_address = form.cleaned_data.get('street_address')
            apartment_address = form.cleaned_data.get('apartment_address')
            country = form.cleaned_data.get('country')
            zip = form.cleaned_data.get('zip')
            save_info = form.cleaned_data.get('save_info')
            use_default = form.cleaned_data.get('use_default')
            payment_option = form.cleaned_data.get('payment_option')

            address = Address(
                user=self.request.user,
                street_address=street_address,
                apartment_address=apartment_address,
                country=country,
                zip=zip,
            )
            address.save()
            if save_info:
                address.default = True
                address.save()

            order.address = address
            order.save()

            if use_default:
                address = Address.objects.get(
                    user=self.request.user, default=True)
                order.address = address
                order.save()

            if payment_option == "I":
                return redirect('payment', payment_option="Ihéla")

            if payment_option == "P":
                return redirect('payment', payment_option="paypal")
            messages.info(self.request, "Invalid payment option")
            return redirect('checkout')
        else:
            print('form invalid')
            return redirect('checkout')


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)

        context = {
            'order': order
        }
        return render(self.request, 'payment.html', context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        try:
            customer = stripe.Customer.create(
                email=self.request.user.email,
                description=self.request.user.username,
                source=self.request.POST['stripeToken']
            )
            amount = order.get_total()
            charge = stripe.Charge.create(
                amount=amount * 100,
                currency="usd",
                customer=customer,
                description="Test payment for buteks online",
            )
            payment = Payment(
                user=self.request.user,
                stripe_charge_id=charge['id'],
                amount=amount
            )
            payment.save()

            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, "Payment was successful")
            return redirect('home')
        except stripe.error.CardError as e:
            messages.info(self.request, f"{e.error.message}")
            return redirect('home')
        except stripe.error.InvalidRequestError as e:
            messages.success(self.request, "Invalid request")
            return redirect('home')
        except stripe.error.AuthenticationError as e:
            messages.success(self.request, "Authentication error")
            return redirect('home')
        except stripe.error.APIConnectionError as e:
            messages.success(self.request, "Check your connection")
            return redirect('home')
        except stripe.error.StripeError as e:
            messages.success(
                self.request, "There was an error please try again")
            return redirect('home')
        except Exception as e:
            messages.success(
                self.request, "A serious error occured we were notified")
            return redirect('home')
    
            

def payment_complete(request):
    body = json.loads(request.body)
    order = Order.objects.get(
        user=request.user, ordered=False, id=body['orderID'])
    payment = Payment(
        user=request.user,
        stripe_charge_id=body['payID'],
        amount=order.get_total()
    )
    payment.save()

    # assign the payment to order
    order.payment = payment
    order.ordered = True
    order.save()
    messages.success(request, "Payment was successful")
    return redirect('home')


def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.success(request, f"{item}'s quantity was updated")
            return redirect('order_summary')
        else:
            order.items.add(order_item)
            messages.success(request, f"{item} was added to your cart")
            return redirect('order_summary')

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered=False, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.success(request, f"{item} was added to your cart")
        return redirect('order_summary')


def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order.items.remove(order_item)
            order.save()
            messages.success(
                request, f"{item.title} was removed from your cart")
            return redirect('order_summary')
        else:
            messages.info(request, f"{item.title} was not in your cart")
            return redirect('order_summary')
    else:
        messages.info(request, "You don't have an active order!")
        return redirect('order_summary')

def remove_single_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
                order.save()
            messages.success(request, f"{item}'s quantity was updated")
            return redirect('order_summary')
        else:
            messages.info(request, f"{item.title} was not in your cart")
            return redirect('order_summary')
    else:
        messages.info(request, "You don't have an active order!")
        return redirect('order_summary')



############################ xhtml ##############################################################


from django.shortcuts import render
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


data = {
    "company": "Blood Bank Company",
    "address": "Bld NDADAYE Melchior",
    "city": "Bujumbura",
    "state": "Burundi",
    "zipcode": "257 75972708",


    "phone": "xxx-xxx-xxx-xxx",
    "email": "info@bloodbank.com",
    "website": "bloodbank.com",

     "order_item" : OrderItem.objects.all(),
     
    }

#Opens up page as PDF
class ViewPDF(View):
    def get(self, request, *args, **kwargs):

        pdf = render_to_pdf('invoice.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


#Automaticly downloads to PDF file
class DownloadPDF(View):
    def get(self, request, *args, **kwargs):
        
        pdf = render_to_pdf('invoice.html', data)

        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Invoice_%s.pdf" %("12341231")
        content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response