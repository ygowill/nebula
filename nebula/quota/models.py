from django.db import models
from user.models import Organization, Employee


# Create your models here.
class QuotaStatistics(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(verbose_name="login date")
    is_linux = models.BooleanField(verbose_name="server type(true for linux)")
    used = models.BigIntegerField(verbose_name="used size")
    dept = models.ForeignKey(Organization, on_delete=models.CASCADE)


class Quota(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Employee, on_delete=models.CASCADE)
    size = models.BigIntegerField(verbose_name="quota size")
    is_linux = models.BooleanField(verbose_name="server type(true for linux)")
    warning = models.BigIntegerField(verbose_name="warning quota size")