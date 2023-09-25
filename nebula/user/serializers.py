from django.contrib.auth.models import User, Group
from rest_framework import serializers
from user.models import MyUser, Employee, Organization


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'name', 'login', 'department', 'onboard_date']


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'dept', 'code', 'description']


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
