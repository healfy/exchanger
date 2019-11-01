from django.contrib import admin

from exchanger.models import (
    Currency,
    ExchangeHistory,
    OutPutTransaction,
    InputTransaction,
    PlatformWallet,
)


class BaseAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    empty_value_display = '-empty-'


class InputTransactionAdmin(BaseAdmin):
    fields = ('trx_hash', 'value', ('to_address', 'from_address'),
              'confirmed_at', 'currency', 'uuid')
    list_display = ('currency', 'to_address', 'from_address')

    readonly_fields = ('status', 'created_at')


class OutPutTransactionAdmin(InputTransactionAdmin):
    pass


class ExchangeHistoryAdmin(BaseAdmin):
    readonly_fields = ('status', 'created_at')
    list_display = ('user_email', 'from_currency', 'to_currency', 'fee')


class CurrencyAdmin(BaseAdmin):
    fields = ('name', 'slug', 'active', 'is_token')
    readonly_fields = ('created_at',)
    list_display = ('name', 'active')


class PlatformWalletAdmin(BaseAdmin):
    readonly_fields = ('address', 'currency', 'external_id', 'created_at')
    list_display = ('currency', 'external_id')


admin.site.register(Currency, CurrencyAdmin)
admin.site.register(InputTransaction, InputTransactionAdmin)
admin.site.register(OutPutTransaction, OutPutTransactionAdmin)
admin.site.register(ExchangeHistory, ExchangeHistoryAdmin)
admin.site.register(PlatformWallet, PlatformWalletAdmin)
