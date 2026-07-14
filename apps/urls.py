from django.contrib import admin
from django.urls import path

from apps.views import *

urlpatterns = [
    path('login', LoginViewList.as_view(), name='login'),
    path('register', RegisterViewList.as_view(), name='register'),
    path('contact', ContactViewList.as_view(), name='contact'),
    path('about', AboutViewList.as_view(), name='about'),
    path('', HomeListView.as_view(), name='home'),
    path('products', ProductsViewList.as_view(), name='products'),
    path('products/category/<int:id>', ProductsViewList.as_view(), name='category_id'),
    path('order/<int:id>', OrderViewList.as_view(), name='order'),
    path('cart', CartViewList.as_view(), name='cart'),
    path('profile', ProfileViewList.as_view(), name='profile'),
    path('logout', Logout.as_view(), name='logout'),
    path('success', SuccessOrderViewList.as_view(), name='succces'),
    path('product/detail/<int:id>', ProductDetailViewList.as_view(), name='detail'),

]
