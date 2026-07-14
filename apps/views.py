from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Model, Min
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, CreateView, FormView, DetailView

from apps.forms import RegisterForm, LoginForm, CreateOrderForm
from apps.models import Product, Category, Order, ProductItem, News, PromoCode


class ProfileViewList(LoginRequiredMixin, TemplateView):
    template_name = 'Profile.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['order_data'] = Order.objects.filter(user=self.request.user).order_by('-created_at')
        return data


class Logout(View):
    def get(self, request):
        messages.success(request, 'Siz bizni tark etdingiz')
        logout(request)
        return redirect('home')


class SuccessOrderViewList(TemplateView):
    template_name = 'Success.html'


class LoginViewList(FormView):
    form_class = LoginForm
    template_name = 'Login.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, "Hush kelibsiz hurmatli Mijoz")
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_invalid(self, form):
        for i in form.errors.values():
            messages.error(self.request, i)
        return super().form_invalid(form)


class RegisterViewList(CreateView):
    form_class = RegisterForm
    template_name = 'Register.html'
    success_url = reverse_lazy('login')

    def form_invalid(self, form):
        for i in form.errors.values():
            messages.error(self.request, i)
        return super().form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, "Siz muffaqiyatli ro'yxatdan o'tingiz")
        return super().form_valid(form)


class HomeListView(TemplateView):
    template_name = 'Home.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        first_item_ids = ProductItem.objects.values('product').annotate(
            first_id=Min('id')
        ).values_list('first_id', flat=True)

        data['pro_data'] = ProductItem.objects.filter(id__in=first_item_ids).select_related('product__cate')
        data['cate_data'] = Category.objects.all()
        data['news_data'] = News.objects.all()

        return data

@method_decorator(csrf_exempt, name='dispatch')
class CheckPromoView(View):
    def get(self, request):
        code = request.GET.get('code', '')
        try:
            promo = PromoCode.objects.get(code=code, is_active=True)
            return JsonResponse({'valid': True, 'discount': float(promo.discount)})
        except PromoCode.DoesNotExist:
            return JsonResponse({'valid': False})


class ProductDetailViewList(DetailView):
    model = ProductItem
    template_name = "Detail.html"
    pk_url_kwarg = 'id'
    context_object_name = "data"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_item = self.object
        product = current_item.product

        context["items"] = product.items.all().prefetch_related("images")
        context["product"] = product

        return context


class AboutViewList(TemplateView):
    template_name = 'About.html'


class ContactViewList(TemplateView):
    template_name = 'Contact.html'


class ProductsViewList(TemplateView):
    template_name = 'Products.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        cate_id = kwargs.get('id')
        search_value = self.request.GET.get('q')

        first_item_ids = ProductItem.objects.values('product').annotate(
            first_id=Min('id')
        ).values_list('first_id', flat=True)

        items = ProductItem.objects.filter(id__in=first_item_ids).select_related('product__cate', 'product')

        if search_value:
            items = items.filter(product__translations__title__icontains=search_value).distinct()
        if cate_id:
            items = items.filter(product__cate_id=cate_id)

        data['pro_data'] = items
        data['pro_data_count'] = items.count()
        data['cate_data'] = Category.objects.all()
        data['selected_category_id'] = cate_id

        return data


class OrderViewList(CreateView):
    form_class = CreateOrderForm
    model = Order
    template_name = 'Order.html'
    success_url = reverse_lazy('succces')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        item_id = self.kwargs.get('id')
        item = ProductItem.objects.filter(id=item_id).first()

        qty = int(self.request.GET.get('qty', 1))

        if item:
            all_price = item.price * qty
        else:
            all_price = 0

        data['pro_data'] = item
        data['quanty'] = qty
        data['all_price'] = all_price

        return data

    def form_valid(self, form):
        item_id = self.kwargs.get('id')
        item = ProductItem.objects.get(id=item_id)
        qty = int(self.request.POST.get('quanty', 1))
        discount = float(self.request.POST.get('discount_amount', 0))

        total_price = float(item.price * qty) - discount

        form.instance.product = item.product
        form.instance.user = self.request.user
        form.instance.all_price = total_price
        form.instance.promo_code = self.request.POST.get('promo_code', '')
        form.instance.discount_amount = discount

        messages.success(self.request, "Buyurtma yaratildi 🚀")
        return super().form_valid(form)

    def form_invalid(self, form):
        print("FORM ERRORS:", form.errors)
        return super().form_invalid(form)


class CartViewList(TemplateView):
    template_name = 'Carts.html'
