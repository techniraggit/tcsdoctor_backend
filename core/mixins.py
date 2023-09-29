from core.permissions import IsAdminOnly, IsDoctorOnly
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from django.db import models
import pretty_errors


class DeleteMixin(models.Model):
    is_deleted = models.BooleanField(default=False)

    def remove(self):
        self.is_deleted = True
        self.save()

    class Meta:
        abstract = True


class DateTimeFieldMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AdminViewMixin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOnly]


class DoctorViewMixin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsDoctorOnly]
