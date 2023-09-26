from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Quota, QuotaStatistics
from django.utils.html import format_html
from import_export import resources


class QuotaResource(resources.ModelResource):

    class Meta:
        model = Quota


class QuotaStatisticsResource(resources.ModelResource):

    class Meta:
        model = QuotaStatistics


class QuotaAdmin(ImportExportModelAdmin):
    # 定制哪些字段需要展示
    list_display = ('id', 'employee', 'size', 'is_linux', 'warning',)

    '''分页：每页10条'''
    list_per_page = 10

    '''最大条目'''
    list_max_show_all = 200  # default

    '''搜索框 ^, =, @, None=icontains'''
    search_fields = ['user']

    resource_class = QuotaResource


class QuotaStatisticsAdmin(ImportExportModelAdmin):
    # 定制哪些字段需要展示
    list_display = ('id', 'employee', 'date', 'is_linux', 'used', 'dept')

    '''分页：每页10条'''
    list_per_page = 10

    '''最大条目'''
    list_max_show_all = 200  # default

    '''搜索框 ^, =, @, None=icontains'''
    search_fields = ['user', 'date', 'dept']

    resource_class = QuotaStatisticsResource


admin.site.register(Quota, QuotaAdmin)
admin.site.register(QuotaStatistics, QuotaStatisticsAdmin)
