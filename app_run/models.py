from django.contrib.auth.models import User
from django.db import models


class ClubData(models.Model):
    company_name = models.CharField(max_length=255, unique=True, verbose_name="название")
    slogan = models.CharField(max_length=100, verbose_name="слоган")
    contacts = models.CharField(max_length=255, verbose_name="адрес")

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = "клуб"
        verbose_name_plural = "клубы"


class Run(models.Model):
    athlete = models.ForeignKey(
        to=User, on_delete=models.PROTECT, verbose_name="бегун", related_name="user_run"
    )
    comment = models.CharField(max_length=255, verbose_name="комментарий")
    created_at = models.DateTimeField(auto_now=True, verbose_name="дата начала")

    def __str__(self):
        return f"{self.athlete.username}"

    class Meta:
        verbose_name = "забег"
        verbose_name_plural = "забеги"

