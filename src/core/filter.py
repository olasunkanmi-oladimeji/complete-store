from itertools import product
from webbrowser import get
from django.shortcuts import render,get_object_or_404
from .models import (Brand,Categories,Item,
                        OrderItem,Order)
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def search(request):
    categorys = Categories.objects.all().order_by('name')
    brands = Brand.objects.all().order_by('name')

    #Search
    query = request.GET.get('q','')
    #The empty string handles an empty "request"
    if query:
        queryset = (Q(title__icontains=query)|
            Q(description__icontains=query)|
            Q(category__name__icontains=query)|
            Q(brand__name__icontains=query))
        results =  Item.objects.filter(queryset).distinct()

    else:
       results = []

    return render(request, 'shop.html',{        'brands':brands,
                                                'query':query,
                                                'results':results,
                                                'categorys' : categorys,
   } )


def category(request,category_slug):
    #Category
    categorys = Categories.objects.all().order_by('name')
    category = None

    items=Item.objects.all().order_by('-id')
    brands = Brand.objects.all().order_by('name')
    minprice = request.GET.get('minPrice')
    maxprice = request.GET.get('maxPrice')

    if category_slug:
        category = get_object_or_404(categorys,slug=category_slug)
        item = Item.objects.filter(category=category)
        itemed=item.filter( Q(price__range=(minprice,maxprice))|
                            Q(discount_price__range=(minprice,maxprice))
                            )
        
    #pagination and item
   

    page = request.GET.get('page', 1)

    if maxprice:

        paginator = Paginator(itemed, 12)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
    else:
        paginator = Paginator(item, 12)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)


    return render(request,'shop.html',{   
                                                    'category':category,
                                                    'page_obj':page_obj,
                                                    'brands':brands,
                                                    'categorys' : categorys,
                                                    
                                                    

                                                   } )

def brand(request,brand_slug):
    #Category
    categorys = Categories.objects.all().order_by('name')
    brand = None


    brands = Brand.objects.all().order_by('name')
    minprice = request.GET.get('minPrice')
    maxprice = request.GET.get('maxPrice')

    if brand_slug:
        brand = get_object_or_404(brands,slug=brand_slug)
        item = Item.objects.filter(brand=brand).order_by('-id')
        itemed=item.filter( Q(price__range=(minprice,maxprice))|
                            Q(discount_price__range=(minprice,maxprice))
                            )
        
    #pagination and item
   

    page = request.GET.get('page', 1)

    if maxprice:

        paginator = Paginator(itemed, 12)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
    else:
        paginator = Paginator(item, 12)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)


    return render(request,'shop.html',{   
                                                    'category':category,
                                                    'page_obj':page_obj,
                                                    'brands':brands,
                                                    'categorys' : categorys,
                                                    
                                                    

                                                   } )

