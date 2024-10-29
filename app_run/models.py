from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
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
    STATUS_CHOICES = (
        (1, "init"),
        (2, "in_progress"),
        (3, "finished"),
    )
    athlete = models.ForeignKey(
        to=User, on_delete=models.PROTECT, verbose_name="бегун", related_name="user_run"
    )
    comment = models.CharField(max_length=255, verbose_name="комментарий")
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1, verbose_name="статус забега")
    created_at = models.DateTimeField(auto_now=True, verbose_name="дата начала")

    def __str__(self):
        return f"{self.athlete.username}, {self.get_status_display()}"

    class Meta:
        verbose_name = "забег"
        verbose_name_plural = "забеги"


class Position(models.Model):
    run = models.ForeignKey(to=Run, on_delete=models.CASCADE, verbose_name="забег")
    latitude = models.FloatField(
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
        verbose_name="широта"
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
        verbose_name="долгота"
    )

    def __str__(self):
        return f"{self.run}: {self.latitude}, {self.longitude}"

    class Meta:
        verbose_name = "координаты забега"
        verbose_name_plural = "координаты забегов"

