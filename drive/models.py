# drive/models.py
from django.db import models

class DriveToken(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    token_uri = models.URLField(default="https://oauth2.googleapis.com/token")
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    scopes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Token for {self.user.username}"


class DriveFile(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    file_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=500)
    mime_type = models.CharField(max_length=255)
    size = models.BigIntegerField(null=True, blank=True)
    web_view_link = models.URLField(blank=True)
    created_time = models.DateTimeField(null=True, blank=True)
    modified_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name