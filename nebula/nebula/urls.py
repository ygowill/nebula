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
from django.urls import path, include
from rest_framework import routers
from user import views as user_view
from quota import views as quota_view


router = routers.DefaultRouter()
router.register(r'employees', user_view.UserViewSet)
router.register(r'organizations', user_view.OrganizationViewSet)
router.register(r'quota', quota_view.QuotaViewSet)
router.register(r'quotastatistics', quota_view.QuotaStatisticsViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('user/', include('user.urls')),
    # path('quota/', include('quota.urls'))
]
