from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http import HttpResponse
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