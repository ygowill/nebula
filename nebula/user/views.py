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
    @api_view(['POST'])
    def add_user(self, request):
        if request.method == 'POST':
            login_user, created = Employee.objects.get_or_create(login=request.data['login_user'])
            login_dept, created = Organization.objects.get_or_create(code=login_user.department)
            if login_dept != 'hr' :
                return Response("Only hr can add user", status=HTTP_400_BAD_REQUEST)

            employee_data = {
                'name': request.data['name'],
                'login': request.data['login'],
                'department': request.data['department'],
                'onboard_date': request.data['onboard_date'],
            }

            quota_data = {
                'user': request.data['login'],
                'is_Linux': 1,
                'size': request.data['quota'],
                'warning': request.data['quota'] * 0.8
            }

            dept, created = Organization.objects.get_or_create(code=request.data['department'])

            add_user_params = {
                "users": [{
                    "firstname": request.data['name'].split(" ")[0],
                    "lastname": request.data['name'].split(" ")[1],
                    "username": request.data['login'],
                    "pwd": request.data['password'],
                    "": ""
                }]
            }
            response_windows = requests.post(STORAGE_URLS.Windows + '', add_user_params)
            response_linux = request.post(STORAGE_URLS.Linux + '', add_user_params)

            employee_serializer = EmployeeSerializer(data=employee_data)
            quota_serializer = QuotaSerializer(data=quota_data)

            if employee_serializer.is_valid() and quota_serializer.is_valid():
                employee_serializer.save()
                quota_serializer.save()