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

    readonly_fields = ('status', 'to_address', 'from_address',
                       'trx_hash', 'value', 'uuid')


class OutPutTransactionAdmin(InputTransactionAdmin):
    pass


class ExchangeHistoryAdmin(BaseAdmin):
    readonly_fields = ExchangeHistory.READ_ONLY_FIELDS
    list_display = ('user_email', 'from_currency', 'to_currency', 'uuid')
    exclude = ('deleted_at', 'is_deleted', )
    fieldsets = (
        ('Main info', {
            'fields': ('user_email', 'uuid',
                       'from_currency', 'to_currency',
                       'ingoing_amount', 'outgoing_amount')
        }),
        ('Read only info', {
            'fields': ('status', 'issue_rate_from', 'issue_rate_to', 'fee')
        }),
        ('InputTransaction info', {
            'fields': ('transaction_input',)
        }),
        ('OutPutTransaction', {
            'fields': ('transaction_output',)
        }),
    )

    def trx_hash(self, instance: ExchangeHistory):
        return instance.transaction_input.trx_hash


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
