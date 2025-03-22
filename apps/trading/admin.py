from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportModelAdmin
from .models import *


@admin.register(Trader)
class TraderAdmin(UserAdmin, ImportExportModelAdmin):
    list_display = ('full_name', 'date_of_birth', 'city', 'address', 'email_verified', 'choose_currency', 'bot_lang_code', 'theme', 'status')
    list_display_links = ('full_name',)
    list_filter = ('city', 'email_verified', 'bot_lang_code', 'theme', 'status')
    list_editable = ('bot_lang_code',)
    search_fields = ('username',)
    autocomplete_fields = ('city',)
    date_hierarchy = "date_of_birth"
    fieldsets = (
        (None, {"fields": ("username", "password", "hash_code")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "email_verified"
                )
            }
        ),
        (
            _("Bot info"),
            {
                "fields": (
                    "bot_first_name",
                    "bot_last_name",
                    "bot_username",
                    "bot_user_id",
                    "bot_phone_number",
                    "bot_lang_code",
                    "bot_registration_finished",
                )
            }
        ),
        (_("Location"), {"fields": ("city", "address")}),
        (
            _("Extra data"),
            {
                "fields": (
                    "image",
                    "choose_currency",
                    "subscription_type",
                    "theme",
                    "status",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("date_of_birth", "last_login", "date_joined")}),
    )
    readonly_fields = ("hash_code", "last_login", "date_joined")


@admin.register(Credit_card)
class Credit_cardAdmin(ImportExportModelAdmin):
    list_display = ('name', 'card_type', 'expiration_date', 'trader', 'verified')
    list_display_links = ('name',)
    list_filter = ('card_type',)
    search_fields = ('name',)
    autocomplete_fields = ('trader',)
    date_hierarchy = "expiration_date"
    readonly_fields = ('trader', 'name', 'number', 'expiration_date', 'cvv', 'card_type', 'verified')


@admin.register(Stock_amount)
class Stock_amountAdmin(ImportExportModelAdmin):
    list_display = ('amount',)
    list_display_links = ('amount',)
    search_fields = ('amount',)


@admin.register(Currency)
class CurrencyAdmin(ImportExportModelAdmin):
    list_display = ('name', 'symbol', 'currency_type', 'simple', 'medium', 'pro', 'simple_max_price', 'medium_max_price', 'pro_max_price', 'country', 'blockchain', 'status')
    list_display_links = ('name',)
    list_filter = ('currency_type', 'status')
    list_editable = ('simple', 'medium', 'pro', 'simple_max_price', 'medium_max_price', 'pro_max_price', 'status')
    search_fields = ('name',)
    autocomplete_fields = ('stock_amounts',)


@admin.register(Exchange)
class ExchangeAdmin(ImportExportModelAdmin):
    list_display = ("trader", "exchange_type", "currency_type", "currency_from", "amount_input", "currency_to", "amount_output", 'rate', 'fees', 'confirmed', "date")
    list_display_links = ('trader',)
    list_filter = ('exchange_type', "currency_type", 'confirmed')
    list_editable = ('confirmed',)
    autocomplete_fields = ("trader", "currency_from", "currency_to")
    date_hierarchy = "date"


@admin.register(Balance_update)
class Balance_updateAdmin(ImportExportModelAdmin):
    list_display = ('trader', 'update_type', 'currency', 'amount', 'payment_type', 'confirmed', 'payed', 'date')
    list_display_links = ('trader',)
    list_filter = ('update_type', 'currency', 'payment_type', 'confirmed', 'payed')
    list_editable = ('confirmed', 'payed',)
    autocomplete_fields = ('trader', 'currency')
    date_hierarchy = "date"


@admin.register(Withdraw)
class WithdrawAdmin(ImportExportModelAdmin):
    list_display = ('trader', 'currency_type', 'currency', 'amount', 'fees', 'confirmed', 'accepted', 'date')
    list_display_links = ('trader',)
    list_editable = ('confirmed', 'accepted')
    list_filter = ('currency_type', 'currency', 'confirmed', 'accepted')
    autocomplete_fields = ('trader', 'currency')
    date_hierarchy = "date"


@admin.register(Send)
class SendAdmin(admin.ModelAdmin):
    list_display = ('trader', 'currency_type', 'currency', 'amount', 'receiver', 'confirmed', 'accepted', 'denied', 'date')
    list_display_links = ('trader',)
    list_editable = ('confirmed', 'accepted', 'denied')
    list_filter = ('currency_type', 'currency', 'confirmed', 'accepted', 'denied')
    autocomplete_fields = ('trader', 'currency', 'receiver')
    date_hierarchy = "date"


@admin.register(Rate_template)
class Rate_templateAdmin(admin.ModelAdmin):
    list_display = ('currency_from', 'currency_to', 'amount')
    list_display_links = ('currency_from', 'currency_to')
    list_filter = ('currency_from', 'currency_to')
    autocomplete_fields = ('currency_from', 'currency_to')
