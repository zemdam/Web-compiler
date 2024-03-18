from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


class Named(models.Model):
    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Container(Named):
    name = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    creation_date = models.DateTimeField(default=now)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    available = models.BooleanField(default=True)
    availability_change_date = models.DateTimeField(blank=True, null=True)
    content_change_date = models.DateTimeField(default=now)
    holder = models.ForeignKey(
        "Catalog", blank=True, null=True, on_delete=models.CASCADE
    )

    class Meta:
        abstract = True


class Catalog(Container):
    pass


class File(Container):
    actual_file = models.FileField(
        upload_to="files/", validators=[FileExtensionValidator(["c"])]
    )


class SectionType(models.Model):
    name = models.CharField(max_length=30, blank=True)
    type = models.CharField(max_length=200, unique=True)
    css_class = models.CharField(max_length=30)

    def __str__(self):
        return self.type


class SectionStatus(models.Model):
    status = models.CharField(max_length=30)

    def __str__(self):
        return self.status


class FileSection(models.Model):
    name = models.CharField(max_length=30, blank=True)
    description = models.TextField(blank=True)
    creation_date = models.DateTimeField(default=now)
    section_start = models.PositiveIntegerField()
    section_end = models.PositiveIntegerField()
    section_type = models.ForeignKey(SectionType, on_delete=models.CASCADE)
    section_status = models.ForeignKey(
        SectionStatus, on_delete=models.CASCADE, default=4
    )
    status_data = models.TextField(blank=True)
    section_data = models.TextField()
    section_of = models.ForeignKey(File, on_delete=models.CASCADE)
