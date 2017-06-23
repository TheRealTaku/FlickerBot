from django.contrib import admin

from .models import Settings, Currency


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('username', 'amount')
    fieldsets = [
        ('User', {'fields': ['username', 'userid']}),
        ('Money', {'fields': ['amount', ]})
    ]


admin.site.register(Settings)
admin.site.register(Currency, CurrencyAdmin)
