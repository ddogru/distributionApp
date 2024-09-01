from django.core.exceptions import ValidationError
from django.db import models


class TypeNormalizationMixin:
    TYPE_CHOICES = []

    def normalize_type(self):
        if hasattr(self, 'type') and self.type:
            self.type = self.type.lower()
            if self.type not in dict(self.TYPE_CHOICES):
                raise ValidationError(f"Invalid type: {self.type}")

    def save(self, *args, **kwargs):
        self.normalize_type()
        super().save(*args, **kwargs)


from django.db import models
from django.core.exceptions import ValidationError


class Vehicle(models.Model, TypeNormalizationMixin):
    COLD = 'cold'
    NORMAL = 'normal'
    TYPE_CHOICES = [
        (COLD, 'Cold'),
        (NORMAL, 'Normal'),
    ]
    vehicle_name = models.CharField(max_length=20)
    weight_capacity = models.FloatField()
    size_capacity = models.IntegerField()
    vehicle_type = models.CharField(max_length=6, choices=TYPE_CHOICES)
    km_capacity = models.FloatField()

    def save(self, *args, **kwargs):
        self.type = self.vehicle_type  # To work with the mixin
        super().save(*args, **kwargs)


class Package(models.Model, TypeNormalizationMixin):
    COLD = 'cold'
    NORMAL = 'normal'
    TYPE_CHOICES = [
        (COLD, 'Cold'),
        (NORMAL, 'Normal'),
    ]

    """CLOSE = 'close'
    MIDDLE = 'middle'
    FAR = 'far'
    DELIVERY_ORDER_CHOICES = [
        (CLOSE, 'Close'),
        (MIDDLE, 'Middle'),
        (FAR, 'Far'),
    ]"""
    package_name = models.CharField(max_length=20)
    weight = models.FloatField()
    size = models.FloatField()
    package_type = models.CharField(max_length=6, choices=TYPE_CHOICES)
    """delivery_order = models.CharField(max_length=10, choices=DELIVERY_ORDER_CHOICES)"""
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='packages')
    package_location = models.CharField(max_length=1000)
    is_delivered = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.type = self.package_type  # To work with the mixin
        super().save(*args, **kwargs)


class Area(models.Model):
    AREA_CHOICES = [
        ('area1', 'Area 1'),
        ('area2', 'Area 2'),
        ('area3', 'Area 3'),
    ]
    area_name = models.CharField(max_length=10, choices=AREA_CHOICES)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='areas')

    def __str__(self):
        return f'{self.area_name} ({self.vehicle.vehicle_name})'


class AreaPackageAssignment(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='area_assignments')
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='area_assignments')
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='area_assignments')

    def __str__(self):
        return f'{self.package.package_name} assigned to {self.area.area_name} in {self.vehicle.vehicle_name}'


class TemporaryPackageAssignment(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    area = models.CharField(max_length=10, choices=Area.AREA_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.package} assigned to {self.area}'


class TemporarySelection(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='temporary_selections')
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='temporary_selections')

    def __str__(self):
        return f'Selection for Vehicle: {self.vehicle}, Package: {self.package}'
