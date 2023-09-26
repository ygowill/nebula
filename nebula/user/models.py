from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token


class MyUser(AbstractUser):
    login_name = models.CharField(verbose_name="user login name, same as Employee login name", max_length=255)

    def __str__(self):
        return self.username + " $ " + self.login_name


# Create your models here.
class Organization(models.Model):
    id = models.AutoField(primary_key=True)
    dept = models.CharField(verbose_name="department", max_length=10)
    code = models.CharField(verbose_name="department id", max_length=30)
    description = models.CharField(verbose_name="department description", max_length=255)

    def __str__(self):
        return self.code + "  ||  " + self.dept


class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    name = models.CharField(verbose_name="employee name", max_length=255)
    login = models.CharField(verbose_name="user login id", max_length=255)
    department = models.ForeignKey(Organization, on_delete=models.CASCADE)
    onboard_date = models.DateField(verbose_name="onboard date", auto_now=False)

    def __str__(self):
        return self.login + "  ||  " + self.name


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
