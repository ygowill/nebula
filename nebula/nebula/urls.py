"""nebula URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path, include, reverse_lazy
from django.views.generic.base import RedirectView
from rest_framework import routers
from user import views as user_view
from user.views import UserLogIn
from quota import views as quota_view


router = routers.DefaultRouter()
router.register(r'employees', user_view.EmployeeViewSet)
router.register(r'organizations', user_view.OrganizationViewSet)
router.register(r'users', user_view.UserViewSet)
router.register(r'quota', quota_view.QuotaViewSet)
router.register(r'quotastatistics', quota_view.QuotaStatisticsViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v2/quotastatistics/get_all_groupby_department/', quota_view.get_all_groupby_department),
    path('api-user-login/', UserLogIn.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
