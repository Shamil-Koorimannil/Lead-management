from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import Brand

class OperatorChoices(models.TextChoices):
    GTE = 'gte', _('Greater than or equal (>=)')
    LTE = 'lte', _('Less than or equal (<=)')
    EQ = 'eq', _('Equals (=)')
    CONTAINS = 'contains', _('Contains')
    IS_TRUE = 'is_true', _('Is True')
    IS_FALSE = 'is_false', _('Is False')

class QualificationRule(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='qualification_rules')
    name = models.CharField(max_length=255)
    field = models.CharField(max_length=100)
    operator = models.CharField(max_length=20, choices=OperatorChoices.choices)
    value = models.CharField(max_length=255, blank=True, default='')
    score = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    priority = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['priority', 'id']

    def __str__(self):
        return f"{self.name} ({self.field} {self.operator} {self.value} -> +{self.score})"
