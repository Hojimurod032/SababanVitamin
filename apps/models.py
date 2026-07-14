from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db.models import *
from parler.models import TranslatedFields, TranslatableModel


class CustomUserManager(BaseUserManager):
    def _create_user(self, phone_number, password, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number kiritilishi shart")

        user = self.model(phone_number=phone_number, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser uchun is_staff=True bo‘lishi kerak")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser uchun is_superuser=True bo‘lishi kerak")

        return self._create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    username = None
    phone_number = CharField(max_length=20, unique=True)
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.phone_number


class Category(TranslatableModel):
    translations = TranslatedFields(
        title=CharField(max_length=255),
    )

    def __str__(self):
        return self.safe_translation_getter('title', any_language=True)


class News(Model):
    bg_image = ImageField(upload_to='news/')


class Brand(TranslatableModel):
    photo = ImageField(upload_to='brand/')

    translations = TranslatedFields(
        name=CharField(max_length=255),
    )

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True)


class Product(TranslatableModel):
    cate = ForeignKey(Category, on_delete=CASCADE)
    brand = ForeignKey(Brand, on_delete=CASCADE)

    translations = TranslatedFields(
        title=CharField(max_length=255),
        level=CharField(max_length=40),
    )

    def __str__(self):
        return self.safe_translation_getter('title', any_language=True)


class ProductItem(TranslatableModel):
    product = ForeignKey(Product, on_delete=CASCADE, related_name='items')
    stock = SmallIntegerField()
    amount = IntegerField()
    price = DecimalField(max_digits=17, decimal_places=2, default=0.0)

    translations = TranslatedFields(
        desc=TextField(),
    )

    def __str__(self):
        return self.product.safe_translation_getter('title', any_language=True)


class ProductItemImage(Model):
    product_item = ForeignKey(ProductItem, on_delete=CASCADE, related_name='images')
    image = ImageField(upload_to='product_items/', null=True, blank=True)

    def __str__(self):
        return f"Image for {self.product_item.id}"


# class Carts(Model):
#     user = ForeignKey(User, on_delete=CASCADE)
#     product = ForeignKey(Product, on_delete=CASCADE)
#     quanty = SmallIntegerField()
#     created_at = DateTimeField(auto_now_add=True)


class Order(Model):
    class StatusType(TextChoices):
        PENDING = 'pending', 'Kutilmoqda'
        CONFIRMED = 'confirmed', 'Tasdiqlandi'
        REJECTED = 'rejected', 'Rad etildi'
        DELIVERING = 'delivering', 'Yetkazilmoqda'
        DELIVERED = 'delivered', 'Yetkazib berilgan'

    product = ForeignKey(Product, on_delete=CASCADE)
    user = ForeignKey(User, on_delete=CASCADE)
    quanty = SmallIntegerField(default=1)
    first_name = CharField(max_length=55)
    created_at = DateTimeField(auto_now_add=True)
    all_price = DecimalField(max_digits=17, decimal_places=2)
    last_name = CharField(max_length=55, blank=True, null=True)
    phone_number = CharField(max_length=55)
    second_number = CharField(max_length=55, blank=True, null=True)
    region = CharField(max_length=55)
    city = CharField(max_length=55)
    address = CharField(max_length=155)
    status = CharField(max_length=55, choices=StatusType, default=StatusType.PENDING)
    desc = TextField(blank=True, null=True)
    payment_check = ImageField(upload_to='payment/')
    message = TextField(blank=True, null=True)
    promo_code = CharField(max_length=50, blank=True, null=True)
    discount_amount = DecimalField(max_digits=10, decimal_places=2, default=0)
    def __str__(self):
        return f"{self.first_name} - {self.phone_number}"

class PromoCode(Model):
    code = CharField(max_length=50, unique=True)
    discount = DecimalField(max_digits=10, decimal_places=2)
    is_active = BooleanField(default=True)

    def __str__(self):
        return self.code