from django.db import models


class ClockModel(models.Model):
    class Meta:
        db_table = "clock_model"
        verbose_name = "时钟"
        verbose_name_plural = "时钟"

    def __str__(self):
        return f"ClockModel #{self.pk}"
