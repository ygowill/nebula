import datetime

from django.core import serializers
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from quota.serializers import QuotaSerializer, QuotaStatisticsSerializer
from .models import Quota, QuotaStatistics
from user.models import Employee, Organization
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, \
    HTTP_403_FORBIDDEN
import traceback
from rest_framework.decorators import api_view
from django.db.models import Count, Sum
import json
import pandas


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

    def list(self, request, *args, **kwargs):
        try:
            username = request.query_params.get("username", "")
            employee = Employee.objects.get(login=username)
            if employee.department.dept == 'it':
                queryset = QuotaStatistics.objects.order_by('dept__id').values()
            else:
                queryset = QuotaStatistics.objects.filter(dept=employee.department.id).order_by('dept__id').values()

            employee_usage_info = {"data": []}
            for q in queryset:
                info = {
                    "user": Employee.objects.get(id=q["employee_id"]).login,
                    "dept": Organization.objects.get(id=q["dept_id"]).dept,
                    "machine": "Linux" if q["is_linux"] else "Windows",
                    "date": str(q["date"]),
                    "limit": Quota.objects.filter(is_linux=q["is_linux"]).get(employee__login=username).size,
                    "usage": q["used"]
                }

                employee_usage_info["data"].append(info)

            return Response(employee_usage_info, HTTP_200_OK)
        except BaseException as be:
            print(traceback.format_exc())
            return Response(be.__str__(), HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:
            username = request.data["username"]
            dept = request.data["dept"]

            if request.data["is_linux"] in ["True", "true", "1"]:
                is_linux = True
            else:
                is_linux = False
            used = int(request.data["used"])
            date = datetime.datetime.now().date()


            employee = Employee.objects.get(login=username)
            department = Organization.objects.get(dept=dept)

            is_record_exist = QuotaStatistics.objects.filter(employee=employee, date=date, is_linux=is_linux)
            if is_record_exist:
                return Response("Record already submitted, report twice", HTTP_400_BAD_REQUEST)

            qs = QuotaStatistics.objects.create(
                employee=employee,
                date=date,
                is_linux=is_linux,
                used=used,
                dept=department
            )

            return Response("Success", HTTP_200_OK)
        except BaseException as be:
            print(traceback.format_exc())
            return Response("Error: {}".format(be.__str__()), HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_groupby_department(request, *args, **kwargs):
    try:
        username = request.query_params.get("username", "")
        employee = Employee.objects.get(login=username)

        if employee.department.dept == 'it':
            queryset = QuotaStatistics.objects\
                .values('dept__id', 'is_linux', 'date')\
                .order_by('dept__id')\
                .annotate(
                    limit=Sum('employee__quota__size'),
                    total_usage=Sum('used')
                )
        else:
            queryset = QuotaStatistics.objects \
                .filter(dept=employee.department.id) \
                .values('dept__id', 'is_linux', 'date') \
                .order_by('dept__id') \
                .annotate(
                    limit=Sum('employee__quota__size'),
                    total_usage=Sum('used')
                )

        department_usage_info = {"data": []}
        for q in queryset:
            info = {
                "user": "-",
                "dept": Organization.objects.get(id=q["dept__id"]).dept,
                "machine": "Linux" if q["is_linux"] else "Windows",
                "date": str(q["date"]),
                "limit": q["limit"],
                "usage": q["total_usage"]
            }

            department_usage_info["data"].append(info)

        return Response(department_usage_info, HTTP_200_OK)
    except BaseException as be:
        print(traceback.format_exc())
        return Response(be.__str__(), HTTP_400_BAD_REQUEST)
    

# class QuotaStatistics():
#     requests.post(STORAGE_URLS.Windows + f'/user/quotaStatistics')
#     requests.post(STORAGE_URLS.Linux + f'/user/quotaStatistics')
    
