from core import views
from core import filter
from django.urls import path



app_name='core'

urlpatterns = [

    path("About",views.about_page,name="about"),
    path('product/<slug>/',views.Product_Page,name='product'),
    path('Add-To-cart/<slug>',views.add_to_cart,name='add_to_cart'),
    path('Remove-FROM-cart/<slug>',views.remove_from_cart,name='remove_from_cart'),
    path('Remove-Item-cart/<slug>',views.remove_single_item_from_cart,name='remove_item_cart'),
    path('order-summary',views.ordersummary.as_view(),name='order-summary'),
    path('checkout',views.CheckoutView.as_view(),name='checkout'),
    path('payment/<payment_option>',views.Paymentview.as_view(),name='payment'),
    path('payment/verify/<id>',views.verify,name='verify'),
    path('add-coupon/', views.AddCouponView.as_view(), name='add-coupon'),
    path('request-refund/',views.RequestRefundView.as_view(), name='request-refund'),
    path('add-wishlist/<id>',views.add_wishlist, name='add_wishlist'),
    path('delete-item-wishlist/<id>',views.delete_wishlist, name='delete_wishlist'),
    path('wishlist',views.wishlist,name='wishlist'),
    path('product-category/<slug:category_slug>',filter.category,name='category'),
    path('product-brand/<slug:brand_slug>',filter.brand,name='brand'),
    path('search/',filter.search,name='search'),
]