from django.contrib import admin
from core.models import (Banner,Brand,Categories,Item,OrderItem,Order,Address,Coupon,
                        Payment,Refund,Wishlist)
# Register your models here.


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)




class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted',
                    'shipping_address',
                    
                    'payment',
                    'coupon'
                    ]
    list_display_links = [
        'user',
        'shipping_address',
        
        'payment',
        'coupon'
    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received',
                   'refund_requested',
                   'refund_granted'
                   ]
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]
admin.site.register(Order,OrderAdmin)

class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'name',
        'address',
        'email',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type',]
    search_fields = ['user', 'address', 'name']
admin.site.register(Address,AddressAdmin)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',]
admin.site.register(OrderItem,OrderItemAdmin)


admin.site.register(Coupon)
admin.site.register(Payment)
admin.site.register(Refund)
admin.site.register(Wishlist)
admin.site.register(Brand)


class ItemAdmin(admin.ModelAdmin):
    list_display=('title','image_tag','category','status',)
admin.site.register(Item,ItemAdmin)

class BannerAdmin(admin.ModelAdmin):
	list_display=('alt_text','image_tag')
admin.site.register(Banner,BannerAdmin)

class CategoriesAdmin(admin.ModelAdmin):
	list_display=('name','image_tag')
admin.site.register(Categories,CategoriesAdmin)