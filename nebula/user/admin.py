from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import MyUser, Employee, Organization
from django.utils.html import format_html
from import_export import resources


class EmployeeResource(resources.ModelResource):

    class Meta:
        model = Employee


class OrganizationResource(resources.ModelResource):

    class Meta:
        model = Organization


class EmployeeAdmin(ImportExportModelAdmin):
    # 定制哪些字段需要展示
    list_display = ('id', 'name', 'login', 'department', 'onboard_date',)

    # list_display_links = ('title', ) # 默认
    # sortable_by # 排序

    '''定义哪个字段可以编辑'''
    # list_editable = ('status',)

    '''分页：每页10条'''
    list_per_page = 10

    '''最大条目'''
    list_max_show_all = 200  # default

    '''搜索框 ^, =, @, None=icontains'''
    search_fields = ['name', 'login', 'department', 'onboard_date']

    resource_class = EmployeeResource


class OrganisationAdmin(ImportExportModelAdmin):
    # 定制哪些字段需要展示
    list_display = ('id', 'dept', 'code', 'description',)

    # list_display_links = ('title', ) # 默认
    # sortable_by # 排序

    '''定义哪个字段可以编辑'''
    # list_editable = ('status',)

    '''分页：每页10条'''
    list_per_page = 10

    '''最大条目'''
    list_max_show_all = 200  # default

    '''搜索框 ^, =, @, None=icontains'''
    search_fields = ['dept', 'code']

    resource_class = OrganizationResource


admin.site.register(MyUser)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Organization, OrganisationAdmin)
