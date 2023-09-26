from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from quota.serializers import QuotaSerializer, QuotaStatisticsSerializer
from .models import Quota, QuotaStatistics
from rest_framework import viewsets


class QuotaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Quota.objects.all().order_by("id")
    serializer_class = QuotaSerializer


class QuotaStatisticsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = QuotaStatistics.objects.all().order_by("id")
    serializer_class = QuotaStatisticsSerializer
    

class QuotaStatistics():
    requests.post(STORAGE_URLS.Windows + f'/user/quotaStatistics')
    requests.post(STORAGE_URLS.Linux + f'/user/quotaStatistics')
    
