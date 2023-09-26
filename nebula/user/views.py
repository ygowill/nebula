import requests
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from django.http import HttpResponse

from nebula.settings import STORAGE_URLS
from quota.serializers import QuotaSerializer
from user.serializers import EmployeeSerializer, OrganizationSerializer, MyUserSerializer
from user.models import MyUser, Employee, Organization
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib import auth
from user.models import Employee, Organization, MyUser
from quota.models import Quota
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Employee.objects.all().order_by("id")
    serializer_class = EmployeeSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Organization.objects.all().order_by("id")
    serializer_class = OrganizationSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all().order_by("id")
    serializer_class = MyUserSerializer
    permission_classes = [IsAuthenticated]


class UserLogIn(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        data = request.data
        user:MyUser = auth.authenticate(username=data["username"], password=data["password"])
        if user:
            token, created = Token.objects.get_or_create(user=user)
            response = JsonResponse(MyUserSerializer(user).data, status=HTTP_200_OK)
            response.headers["Authorization"] = f"Token {token}"
            return response
        else:
            return Response("Invalid username or password.", status=HTTP_400_BAD_REQUEST)


class addUser():
    
    def add_user(self, request):
        login_user = Employee.objects.get(id=request.data['login_user'])
        login_dept = Organization.objects.get(code=login_user.department)
        if login_dept != 'hr' :
            return Response("Only hr can add user!", status=HTTP_400_BAD_REQUEST)
        
        new_employee = Employee(
            name=request.data['name'],
            login=request.data['login'],
            department=request.data['department'],
            onboard_date=request.data['onboard_date']
        )
        
        quota_data = {
            'user': request.data['login'],
            'is_Linux': 1,
            'size': request.data['quota'],
            'warning': request.data['quota'] * 0.8
        }

        add_user_params = {
            "users": [{
                "firstname": request.data['name'].split(" ")[0],
                "lastname": request.data['name'].split(" ")[1],
                "username": request.data['username'],
                "pwd": "qweASD123",
                "quota": request.data['quota'],
                "dept": request.data['department']
            }]
        }
        response_windows = requests.post(STORAGE_URLS.Windows + '/user/addUsers', json=add_user_params)
        
        if (response_windows.status_code == 200 and response_windows.json().get("success") == 'True'):
            response_linux = request.post(STORAGE_URLS.Linux + '/user/addUsers', add_user_params)
            if (response_linux.status_code == 200 and response_linux.json().get("success") == 'True'):
                new_employee.save()
                return Response(f"add {add_user_params.users[0].username} successfully!")
            else:
                requests.post(STORAGE_URLS.Windows + f'/user/removeUser/{add_user_params.users[0].username}')
        return Response(f"Failed to add user {add_user_params.users[0].username}!")
    

class removeUser():
    
    def remove_user(self, request):
        requests.post(STORAGE_URLS.Windows + f'/user/removeUser/{request.data['username']}')
        requests.post(STORAGE_URLS.Linux + f'/user/removeUser/{request.data['username']}')
        

class changeQuota():
    
    def change_quota(self, request):
        change_quota_param = {
            "username": request.data['username']
            "quota": request.data['quota']
        }
        
        response_windows = requests.post(STORAGE_URLS.Windows + '/user/changeQuota', json=change_quota_param)
        response_Linux = requests.post(STORAGE_URLS.Linux + '/user/changeQuota', json=change_quota_param)
        
        return Response(f"Changed the quota for {change_quota_param.username} successfully!")
    