from datetime import datetime

import requests
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from django.http import HttpResponse
from rest_framework.views import APIView
import traceback

from nebula.settings import STORAGE_URLS
from quota.serializers import QuotaSerializer
from user.serializers import EmployeeSerializer, OrganizationSerializer, MyUserSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib import auth
from user.models import Employee, Organization, MyUser
from quota.models import Quota
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, \
    HTTP_403_FORBIDDEN
from django.db import transaction


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Employee.objects.all().order_by("id")
    serializer_class = EmployeeSerializer

    def list(self, *args, **kwargs):
        start_date = self.request.query_params.get("start_date", "")
        end_date = self.request.query_params.get("end_date", "")
        department = self.request.query_params.get("department", "")
        if start_date == "" or end_date == "":
            if department == "":
                queryset = Employee.objects.all()
            else:
                queryset = Employee.objects.filter(department=department)
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            if department == "":
                queryset = Employee.objects.filter(onboard_date__gte=start_date, onboard_date__lte=end_date)
            else:
                queryset = Employee.objects.filter(onboard_date__gte=start_date, onboard_date__lte=end_date,
                                                   department=department)

        serializer = EmployeeSerializer(queryset, many=True)
        return Response(serializer.data)



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

    def create(self, request, *args, **kwargs):
        user = request.user
        employee = Employee.objects.get(user=user)
        if employee.department.dept != 'hr':
            return Response("Only HR can do this", HTTP_401_UNAUTHORIZED)
        # print(request.data["users"][0])
        info = request.data["users"][0]
        dept = Organization.objects.get(pk=info["dept"])

        try:
            with transaction.atomic():
                user = MyUser.objects.create_user(
                    password=info["pwd"],
                    username=info["username"],
                    login_name=info["username"]
                )
                user.first_name = info["firstname"]
                user.last_name = info["lastname"]
                user.save()

                employee = Employee.objects.create(
                    user=user,
                    name=" ".join([info["firstname"], info["lastname"]]),
                    login=info["username"],
                    department=dept,
                    onboard_date=datetime.now(),
                    quota=info["quota"]
                )

                linux_quota = Quota.objects.create(
                    employee=employee,
                    size=info["quota"],
                    is_linux=True,
                    warning=info["quota"] * 0.8
                )
                
                windows_quota = Quota.objects.create(
                    employee=employee,
                    size=info["quota"],
                    is_linux=False,
                    warning=info["quota"] * 0.8
                )

                add_user_params = {
                    "users": [{
                        "firstname": info['firstname'],
                        "lastname": info['lastname'],
                        "username": info['username'],
                        "pwd": info['pwd'],
                        "quota": info['quota'],
                        "dept": dept.dept
                    }]
                }

                windows_url = STORAGE_URLS["Windows"] + '/user/addUsers'
                timeout = 10
                print(windows_url)
                response_windows = requests.post(url=windows_url, json=add_user_params, timeout=timeout)
                if response_windows.status_code == 200 and response_windows.json().get("success") == 'True':
                    linux_url = STORAGE_URLS["Linux"] + '/user/addUsers'
                    print(linux_url)
                    response_linux = request.post(url=linux_url, json=add_user_params, timeout=timeout)
                    if response_linux.status_code == 200 and response_linux.json().get("success") == 'True':
                        pass
                    else:
                        url = STORAGE_URLS["Windows"] + f'/user/removeUser/{add_user_params["users"][0]["username"]}'
                        print(url)
                        requests.post(url=url, timeout=timeout)
                        raise Exception("fail to create quota on linux")
                else:
                    raise Exception("failed to create quota on windows")

        except BaseException as be:
            print(traceback.format_exc())
            return Response(be.__str__(), HTTP_400_BAD_REQUEST)
        return Response("Success", HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        # requests.post(STORAGE_URLS.Windows + f'/user/removeUser/{request.data["username"]}')
        # requests.post(STORAGE_URLS.Linux + f'/user/removeUser/{request.data["username"]}')
        user = MyUser.objects.get(username=request.data["username"])
        user.delete()


class UserLogIn(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        data = request.data
        user: MyUser = auth.authenticate(username=data["username"], password=data["password"])
        if user:
            token, created = Token.objects.get_or_create(user=user)
            response_data = MyUserSerializer(user).data
            response_data["token"] = f'{token}'
            response = JsonResponse(response_data, status=HTTP_200_OK)
            return response
        else:
            return Response("Invalid username or password.", status=HTTP_400_BAD_REQUEST)

# class addUser():
#
#     def add_user(self, request):
#         login_user = Employee.objects.get(id=request.data['login_user'])
#         login_dept = Organization.objects.get(code=login_user.department)
#         if login_dept != 'hr' :
#             return Response("Only hr can add user!", status=HTTP_400_BAD_REQUEST)
#
#         new_employee = Employee(
#             name=request.data['name'],
#             login=request.data['login'],
#             department=request.data['department'],
#             onboard_date=request.data['onboard_date']
#         )
#
#         quota_data = {
#             'user': request.data['login'],
#             'is_Linux': 1,
#             'size': request.data['quota'],
#             'warning': request.data['quota'] * 0.8
#         }
#
#         add_user_params = {
#             "users": [{
#                 "firstname": request.data['name'].split(" ")[0],
#                 "lastname": request.data['name'].split(" ")[1],
#                 "username": request.data['username'],
#                 "pwd": "qweASD123",
#                 "quota": request.data['quota'],
#                 "dept": request.data['department']
#             }]
#         }
#         response_windows = requests.post(STORAGE_URLS.Windows + '/user/addUsers', json=add_user_params)
#
#         if (response_windows.status_code == 200 and response_windows.json().get("success") == 'True'):
#             response_linux = request.post(STORAGE_URLS.Linux + '/user/addUsers', add_user_params)
#             if (response_linux.status_code == 200 and response_linux.json().get("success") == 'True'):
#                 new_employee.save()
#                 return Response(f"add {add_user_params.users[0].username} successfully!")
#             else:
#                 requests.post(STORAGE_URLS.Windows + f'/user/removeUser/{add_user_params.users[0].username}')
#         return Response(f"Failed to add user {add_user_params.users[0].username}!")
#
#
# class removeUser():
#
#     def remove_user(self, request):
#         requests.post(STORAGE_URLS.Windows + f'/user/removeUser/{request.data["username"]}')
#         requests.post(STORAGE_URLS.Linux + f'/user/removeUser/{request.data["username"]}')
#
#
# class changeQuota():
#
#     def change_quota(self, request):
#         change_quota_param = {
#             "username": request.data['username'],
#             "quota": request.data['quota']
#         }
#
#         response_windows = requests.post(STORAGE_URLS.Windows + '/user/changeQuota', json=change_quota_param)
#         response_Linux = requests.post(STORAGE_URLS.Linux + '/user/changeQuota', json=change_quota_param)
#
#         return Response(f"Changed the quota for {change_quota_param.username} successfully!")
