from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.shortcuts import reverse


CATEGORY_CHOICES = (
    ('B', 'Blood'),
    ('P', 'Plasma'),
    ('C', 'Cells')
)

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'Paypal'),
)

class Item(models.Model):
    title = models.CharField(max_length=200)
    price = models.IntegerField()
    discount_price = models.IntegerField(blank=True, null=True)
    slug = models.SlugField()
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    

    def __str__(self):
        return self.title

    def get_add_to_cart_url(self):
        return reverse('add_to_cart', kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse('remove_from_cart', kwargs={'slug': self.slug})

    def get_remove_single_from_cart_url(self):
        return reverse('remove_single_from_cart', kwargs={'slug': self.slug})





class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_item_discount_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_final_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_item_discount_price()
        return self.get_total_item_price()

    

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    address = models.ForeignKey("Address", on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey("Payment", on_delete=models.SET_NULL, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=200)
    apartment_address = models.CharField(max_length=200)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=200)
    save_info = models.BooleanField(default=False)
    default = models.BooleanField(default=False)
    use_default = models.BooleanField(default=False)
    payment_option = models.CharField(choices=PAYMENT_CHOICES, max_length=2)

    class Meta:
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return self.user.username


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stripe_charge_id = models.CharField(max_length=100)
    amount = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username



class Donor(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    blood_group = models.ForeignKey(Item, on_delete = models.CASCADE)
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.name


