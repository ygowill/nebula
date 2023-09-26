from django.contrib.auth.models import User, Group
from rest_framework import serializers
from user.models import MyUser, Employee, Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'dept', 'code', 'description']


class EmployeeSerializer(serializers.ModelSerializer):
    dept = serializers.SerializerMethodField()

    def get_dept(self, instance):
        data = Organization.objects.get(employee=instance)
        data = OrganizationSerializer(data).data
        return data
    class Meta:
        model = Employee
        fields = ['id', 'name', 'login', 'dept', 'onboard_date']


class MyUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyUser
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'login_name')

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
