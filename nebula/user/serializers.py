from django.contrib.auth.models import User, Group
from rest_framework import serializers
from user.models import Employee, Organization


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'name', 'login', 'department', 'onboard_date']


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'dept', 'code', 'description']
