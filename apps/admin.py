from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib.humanize.templatetags.humanize import intcomma

from parler.admin import TranslatableAdmin, TranslatableTabularInline

from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    RangeDateFilter,
    RangeNumericFilter,
    ChoicesDropdownFilter,
)
from unfold.decorators import display

from .models import (
    User,
    Category,
    News,
    Brand,
    Product,
    ProductItem,
    ProductItemImage,
    Order,
    PromoCode,
)


# ---------------------------------------------------------------------------
# FOYDALANUVCHI
# ---------------------------------------------------------------------------

@admin.register(User)
class CustomUserAdmin(DjangoUserAdmin, ModelAdmin):
    model = User

    list_display = (
        "phone_number",
        "first_name",
        "last_name",
        "faollik",
        "date_joined",
    )
    list_display_links = ("phone_number",)
    search_fields = ("phone_number", "first_name", "last_name")
    ordering = ("-date_joined",)
    readonly_fields = ("last_login", "date_joined")

    fieldsets = (
        (_("Telefon va parol"), {"fields": ("phone_number", "password")}),
        (_("Shaxsiy ma'lumotlar"), {"fields": ("first_name", "last_name")}),
        (_("Kirish huquqlari"), {
            "fields": ("is_active", "is_staff", "is_superuser"),
            "classes": ["tab"],
        }),
        (_("Sanalar"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (_("Yangi foydalanuvchi"), {
            "classes": ("wide",),
            "fields": ("phone_number", "password1", "password2"),
        }),
    )

    @display(description=_("Holati"), label=True)
    def faollik(self, obj):
        if obj.is_superuser:
            return "Boshqaruvchi", "danger"
        if obj.is_staff:
            return "Xodim", "warning"
        if obj.is_active:
            return "Faol", "success"
        return "Bloklangan", "danger"


# ---------------------------------------------------------------------------
# KATEGORIYA
# ---------------------------------------------------------------------------

@admin.register(Category)
class CategoryAdmin(TranslatableAdmin, ModelAdmin):
    list_display = ("id", "nomi", "mahsulotlar_soni")
    search_fields = ("translations__title",)
    list_per_page = 25

    @display(description=_("Nomi"))
    def nomi(self, obj):
        return obj.safe_translation_getter("title", any_language=True) or "—"

    @display(description=_("Mahsulotlar soni"))
    def mahsulotlar_soni(self, obj):
        return obj.product_set.count()


# ---------------------------------------------------------------------------
# YANGILIKLAR (Banner rasmlar)
# ---------------------------------------------------------------------------

@admin.register(News)
class NewsAdmin(ModelAdmin):
    list_display = ("id", "rasm_korinishi")
    list_per_page = 25

    @display(description=_("Rasm"))
    def rasm_korinishi(self, obj):
        if obj.bg_image:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:8px;object-fit:cover;" />',
                obj.bg_image.url,
            )
        return "Rasm yo'q"


# ---------------------------------------------------------------------------
# BREND
# ---------------------------------------------------------------------------

@admin.register(Brand)
class BrandAdmin(TranslatableAdmin, ModelAdmin):
    list_display = ("id", "logotip", "nomi")
    search_fields = ("translations__name",)
    list_per_page = 25

    @display(description=_("Logotip"))
    def logotip(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:6px;" />',
                obj.photo.url,
            )
        return "—"

    @display(description=_("Nomi"))
    def nomi(self, obj):
        return obj.safe_translation_getter("name", any_language=True) or "—"


# ---------------------------------------------------------------------------
# MAHSULOT RASMLARI (inline)
# ---------------------------------------------------------------------------

class MahsulotRasmInline(TabularInline):
    model = ProductItemImage
    extra = 1
    fields = ("image", "korinish")
    readonly_fields = ("korinish",)
    verbose_name = "Rasm"
    verbose_name_plural = "Rasmlar"

    @display(description=_("Ko'rinish"))
    def korinish(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="height:70px;border-radius:6px;object-fit:contain;" />',
                obj.image.url,
            )
        return "—"


# ---------------------------------------------------------------------------
# MAHSULOT VARIANTLARI (Product ichida inline)
# ---------------------------------------------------------------------------

class MahsulotVariantInline(TranslatableTabularInline, TabularInline):
    model = ProductItem
    extra = 0
    fields = ("desc", "stock", "amount", "price")
    show_change_link = True
    verbose_name = "Variant"
    verbose_name_plural = "Variantlar"


# ---------------------------------------------------------------------------
# MAHSULOT VARIANTI (alohida sahifa)
# ---------------------------------------------------------------------------

@admin.register(ProductItem)
class ProductItemAdmin(TranslatableAdmin, ModelAdmin):
    list_display = (
        "id",
        "mahsulot_nomi",
        "miqdor",
        "ombor_holati",
        "narxi",
    )
    list_filter = (
        ("price", RangeNumericFilter),
        ("stock", RangeNumericFilter),
    )
    search_fields = ("product__translations__title",)
    autocomplete_fields = ("product",)
    inlines = [MahsulotRasmInline]
    list_per_page = 25

    fieldsets = (
        (_("Mahsulot"), {"fields": ("product",)}),
        (_("Ma'lumotlar"), {"fields": ("desc", "amount", "price", "stock")}),
    )

    @display(description=_("Mahsulot"))
    def mahsulot_nomi(self, obj):
        return obj.product.safe_translation_getter("title", any_language=True) or "—"

    @display(description=_("Miqdor"))
    def miqdor(self, obj):
        return f"{obj.amount} mg"

    @display(description=_("Narxi"))
    def narxi(self, obj):
        return f"{intcomma(int(obj.price))} so'm"

    @display(description=_("Ombor"), label=True)
    def ombor_holati(self, obj):
        if obj.stock <= 0:
            return "Tugagan", "danger"
        if obj.stock < 10:
            return f"Kam qoldi ({obj.stock} ta)", "warning"
        return f"Mavjud ({obj.stock} ta)", "success"


# ---------------------------------------------------------------------------
# MAHSULOT
# ---------------------------------------------------------------------------

@admin.register(Product)
class ProductAdmin(TranslatableAdmin, ModelAdmin):
    list_display = (
        "id",
        "nomi",
        "kategoriya",
        "brend",
        "daraja",
        "variantlar_soni",
    )
    list_filter = ("cate", "brand")
    search_fields = (
        "translations__title",
        "cate__translations__title",
        "brand__translations__name",
    )
    autocomplete_fields = ("cate", "brand")
    list_select_related = ("cate", "brand")
    inlines = [MahsulotVariantInline]
    list_per_page = 25

    fieldsets = (
        (_("Asosiy ma'lumotlar"), {"fields": ("cate", "brand")}),
        (_("Tarjimalar"), {"fields": ("title", "level")}),
    )

    @display(description=_("Mahsulot nomi"))
    def nomi(self, obj):
        return obj.safe_translation_getter("title", any_language=True) or "—"

    @display(description=_("Kategoriya"))
    def kategoriya(self, obj):
        return obj.cate.safe_translation_getter("title", any_language=True) or "—"

    @display(description=_("Brend"))
    def brend(self, obj):
        return obj.brand.safe_translation_getter("name", any_language=True) or "—"

    @display(description=_("Daraja"))
    def daraja(self, obj):
        return obj.safe_translation_getter("level", any_language=True) or "—"

    @display(description=_("Variantlar soni"))
    def variantlar_soni(self, obj):
        return obj.items.count()


CategoryAdmin.search_fields = ("translations__title",)
BrandAdmin.search_fields = ("translations__name",)


# ---------------------------------------------------------------------------
# PROMOKOD
# ---------------------------------------------------------------------------

@admin.register(PromoCode)
class PromoCodeAdmin(ModelAdmin):
    list_display = ("id", "kod", "chegirma_summasi", "holati")
    list_filter = ("is_active",)
    search_fields = ("code",)
    list_per_page = 25

    fieldsets = (
        (_("Promokod ma'lumotlari"), {
            "fields": ("code", "discount", "is_active"),
        }),
    )

    @display(description=_("Kod"))
    def kod(self, obj):
        return obj.code

    @display(description=_("Chegirma summasi"))
    def chegirma_summasi(self, obj):
        return f"-{intcomma(int(obj.discount))} so'm"

    @display(description=_("Holati"), label=True)
    def holati(self, obj):
        if obj.is_active:
            return "Faol", "success"
        return "Faol emas", "danger"


# ---------------------------------------------------------------------------
# BUYURTMA
# ---------------------------------------------------------------------------

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = (
        "id",
        "mijoz_ismi",
        "mahsulot",
        "soni",
        "jami_narx",
        "promokod_malumot",
        "buyurtma_holati",
        "telefon",
        "manzil",
        "sana",
    )
    list_display_links = ("id", "mijoz_ismi")
    list_filter = (
        ("status", ChoicesDropdownFilter),
        "region",
        ("created_at", RangeDateFilter),
        ("all_price", RangeNumericFilter),
    )
    search_fields = (
        "first_name",
        "last_name",
        "phone_number",
        "second_number",
        "address",
        "promo_code",
    )
    autocomplete_fields = ("product", "user")
    list_select_related = ("product", "user")
    readonly_fields = ("created_at", "tolov_cheki_korinish")
    date_hierarchy = "created_at"
    list_per_page = 25

    fieldsets = (
        (_("Mijoz ma'lumotlari"), {
            "fields": (
                "user",
                ("first_name", "last_name"),
                ("phone_number", "second_number"),
            )
        }),
        (_("Yetkazib berish manzili"), {
            "fields": (
                ("region", "city"),
                "address",
                "desc",
            )
        }),
        (_("Buyurtma tafsilotlari"), {
            "fields": (
                "product",
                "quanty",
                "all_price",
                "promo_code",
                "discount_amount",
                "status",
                "message",
            )
        }),
        (_("To'lov cheki"), {
            "fields": (
                "payment_check",
                "tolov_cheki_korinish",
            )
        }),
        (_("Sana"), {
            "fields": ("created_at",),
        }),
    )

    actions = [
        "tasdiqlash",
        "yetkazilmoqda",
        "yetkazildi",
        "rad_etish",
    ]

    @display(description=_("Mijoz"))
    def mijoz_ismi(self, obj):
        return f"{obj.first_name} {obj.last_name or ''}".strip()

    @display(description=_("Mahsulot"))
    def mahsulot(self, obj):
        return obj.product.safe_translation_getter("title", any_language=True) or "—"

    @display(description=_("Soni"))
    def soni(self, obj):
        return f"{obj.quanty} dona"

    @display(description=_("Viloyat / Shahar"))
    def manzil(self, obj):
        return f"{obj.region}, {obj.city}"

    @display(description=_("Telefon"))
    def telefon(self, obj):
        return obj.phone_number

    @display(description=_("Sana"))
    def sana(self, obj):
        return obj.created_at.strftime("%d.%m.%Y %H:%M")

    @display(description=_("Jami narx"))
    def jami_narx(self, obj):
        return f"{intcomma(int(obj.all_price))} so'm"

    @display(description=_("Promokod"))
    def promokod_malumot(self, obj):
        if obj.promo_code:
            return format_html(
                '{} (-{} so\'m)',
                obj.promo_code,
                intcomma(int(obj.discount_amount)),
            )
        return "—"

    @display(description=_("Holati"), label=True)
    def buyurtma_holati(self, obj):
        mapping = {
            Order.StatusType.PENDING:    ("Kutilmoqda",        "warning"),
            Order.StatusType.CONFIRMED:  ("Tasdiqlandi",       "info"),
            Order.StatusType.REJECTED:   ("Rad etildi",        "danger"),
            Order.StatusType.DELIVERING: ("Yetkazilmoqda",     "primary"),
            Order.StatusType.DELIVERED:  ("Yetkazib berilgan", "success"),
        }
        return mapping.get(obj.status, (obj.status, "secondary"))

    @display(description=_("To'lov cheki"))
    def tolov_cheki_korinish(self, obj):
        if obj.payment_check:
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" style="max-height:200px;border-radius:10px;'
                'border:1px solid #ddd;padding:4px;" />'
                '</a>',
                obj.payment_check.url,
            )
        return "Chek yuklanmagan"

    @admin.action(description=_("Tasdiqlash"))
    def tasdiqlash(self, request, queryset):
        updated = queryset.update(status=Order.StatusType.CONFIRMED)
        self.message_user(request, f"{updated} ta buyurtma tasdiqlandi.")

    @admin.action(description=_("Yetkazilmoqda deb belgilash"))
    def yetkazilmoqda(self, request, queryset):
        updated = queryset.update(status=Order.StatusType.DELIVERING)
        self.message_user(request, f"{updated} ta buyurtma yetkazilmoqda.")

    @admin.action(description=_("Yetkazib berildi deb belgilash"))
    def yetkazildi(self, request, queryset):
        updated = queryset.update(status=Order.StatusType.DELIVERED)
        self.message_user(request, f"{updated} ta buyurtma yetkazib berildi.")

    @admin.action(description=_("Rad etish"))
    def rad_etish(self, request, queryset):
        updated = queryset.update(status=Order.StatusType.REJECTED)
        self.message_user(request, f"{updated} ta buyurtma rad etildi.")