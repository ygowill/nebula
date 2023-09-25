from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Quota, QuotaStatistics


class QuotaStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotaStatistics
        fields = ['id', 'user', 'date', 'is_linux', 'used', "dept"]


class QuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quota
        fields = ['id', 'user', 'size', 'is_linux', 'warning']
