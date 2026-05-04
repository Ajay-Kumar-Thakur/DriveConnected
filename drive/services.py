# drive/services.py
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from django.conf import settings
import io

def get_credentials(user):
    """Retrieve and refresh credentials for a user."""
    from .models import DriveToken
    try:
        token_obj = DriveToken.objects.get(user=user)
        creds = Credentials(
            token=token_obj.token,
            refresh_token=token_obj.refresh_token,
            token_uri=token_obj.token_uri,
            client_id=token_obj.client_id,
            client_secret=token_obj.client_secret,
            scopes=token_obj.scopes.split(','),
        )
        # Auto-refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_obj.token = creds.token
            token_obj.save()
        return creds
    except DriveToken.DoesNotExist:
        return None


def get_drive_service(user):
    """Build the Drive API service."""
    creds = get_credentials(user)
    if not creds:
        raise ValueError("No credentials found. Please authenticate first.")
    return build('drive', 'v3', credentials=creds)


def list_files(user, page_size=20, query=None):
    """List files from Google Drive."""
    service = get_drive_service(user)
    params = {
        'pageSize': page_size,
        'fields': 'files(id,name,mimeType,size,webViewLink,createdTime,modifiedTime)',
    }
    if query:
        params['q'] = query
    result = service.files().list(**params).execute()
    return result.get('files', [])


def upload_file(user, file_obj, filename, mime_type='application/octet-stream'):
    """Upload a file to Google Drive."""
    service = get_drive_service(user)
    file_metadata = {'name': filename}
    media = MediaIoBaseUpload(io.BytesIO(file_obj.read()), mimetype=mime_type)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id,name,webViewLink'
    ).execute()
    return file


def download_file(user, file_id):
    """Download a file from Google Drive."""
    service = get_drive_service(user)
    request = service.files().get_media(fileId=file_id)
    file_content = io.BytesIO()
    from googleapiclient.http import MediaIoBaseDownload
    downloader = MediaIoBaseDownload(file_content, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    file_content.seek(0)
    return file_content


def update_file(user, file_id, new_name=None, new_file=None, mime_type=None):
    """Update file metadata and/or content."""
    service = get_drive_service(user)
    file_metadata = {}
    if new_name:
        file_metadata['name'] = new_name
    if new_file:
        media = MediaIoBaseUpload(
            io.BytesIO(new_file.read()),
            mimetype=mime_type or 'application/octet-stream'
        )
        return service.files().update(
            fileId=file_id,
            body=file_metadata,
            media_body=media,
            fields='id,name,modifiedTime'
        ).execute()
    return service.files().update(
        fileId=file_id,
        body=file_metadata,
        fields='id,name,modifiedTime'
    ).execute()


def delete_file(user, file_id):
    """Permanently delete a file from Google Drive."""
    service = get_drive_service(user)
    service.files().delete(fileId=file_id).execute()
    return True