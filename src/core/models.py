from distutils.command.upload import upload
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.html import mark_safe
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

LABEL_CHOICES = (
    ('b','primary'),
    ('r','danger'),
    ('y','warning')
)

class Item(models.Model):
    status=models.BooleanField(default=True)
    title = models.CharField(max_length=200,unique=True)
    slug = models.SlugField(max_length=400)
    category =models.ForeignKey('Categories',on_delete=models.CASCADE)
    brand =models.ForeignKey('Brand',on_delete=models.CASCADE,null=True,blank=True)
    description =models.TextField(default="Lorem")
    price=models.PositiveIntegerField(default=500)
    discount_price=models.PositiveIntegerField(default=0,null=True,blank=True)
    image=models.ImageField(upload_to="product_imgs/",null=True)
    label = models.CharField(choices=LABEL_CHOICES,max_length=2,null=True,blank=True)
    label_text=models.CharField(blank=True,null=True,max_length=10)

    
    def image_tag(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
    def get_absolute_url(self):
        return reverse('core:product', kwargs={'slug': self.slug})
    def get_add_to_cart_url(self):
        return reverse('core:add_to_cart', kwargs={'slug': self.slug})
    def get_remove_from_cart_url(self):
        return reverse('core:remove_from_cart', kwargs={'slug': self.slug})
    def get_remove_item_cart_url(self):
        return reverse('core:remove_item_cart', kwargs={'slug': self.slug})
    def get_discount(self):
        y = 100 * ( self.price - self.discount_price) / self.price
        x = round(y)
        return x
    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural='.4 Products'

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"
    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

    def get_discount_percentage(self):
        if self.item.discount_price:
            a= 100*(self.item.price -self.item.discount_price)/self.item.price
            return a

    
    class Meta:
        verbose_name_plural='.5 orderd Items'

#cart
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    items = models.ManyToManyField(OrderItem)
    ordered = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    

    def __str__(self):
        return self.user.username
    
    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total
    class Meta:
        verbose_name_plural='.6 Order'

class Categories(models.Model):
    name = models.CharField(max_length=20)
    img = models.ImageField(upload_to = "categories/")
    slug = models.SlugField()
    
    def image_tag(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.img.url))

    def get_absolute_url(self):
        return reverse('core:category', args=[self.slug])

    class Meta:
        verbose_name_plural='.2 Categories'

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=20)
    img = models.ImageField(upload_to = "Brands/")
    slug = models.SlugField()
    
    def image_tag(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.img.url))

    def get_absolute_url(self):
        return reverse('core:brand', args=[self.slug])

    class Meta:
        verbose_name_plural='.3 Brand'

    def __str__(self):
        return self.name
class Banner(models.Model):
    img=models.ImageField(upload_to="banner_imgs/")
    alt_text=models.CharField(max_length=300)

    class Meta:
        verbose_name_plural='.1 Banners'

    def image_tag(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.img.url))

    def __str__(self):
        return self.alt_text





ADDRESS_CHOICES = (
    ('P','Pickup'),
    ('S', 'Delivery'),
)

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    address = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)
    phone_no =PhoneNumberField()
    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'
    
    class Meta:
        verbose_name_plural='8. Adddress'

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural='9. Payment'


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=9, decimal_places=2,blank=True,null=True)

    def __str__(self):
        return self.code
    class Meta:
        verbose_name_plural='10. Coupon'



class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"
    
    class Meta:
        verbose_name_plural='11 Refund'

class Wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Item,on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural='Wishlist'