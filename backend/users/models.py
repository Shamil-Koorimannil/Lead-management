from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

from decimal import Decimal

class UserRole(models.TextChoices):
    BRAND_OWNER = 'BRAND_OWNER', _('Brand Owner')
    SALES_MANAGER = 'SALES_MANAGER', _('Sales Manager')
    SALES_AGENT = 'SALES_AGENT', _('Sales Agent')

class Organization(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Brand(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='brands')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    min_investment_threshold = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal('1500000.00'),
        help_text=_('Minimum investment capacity required for a lead to qualify.')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.organization.name} - {self.name}"

class CustomUserManager(BaseUserManager):
    """Custom user manager where email is the unique identifier for authentication."""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.BRAND_OWNER)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.CharField(
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.SALES_AGENT
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.get_full_name()} ({self.email}) - {self.role}"

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email

    @property
    def is_brand_owner(self):
        return self.role == UserRole.BRAND_OWNER or self.is_superuser

    @property
    def is_sales_manager(self):
        return self.role == UserRole.SALES_MANAGER

    @property
    def is_sales_agent(self):
        return self.role == UserRole.SALES_AGENT
