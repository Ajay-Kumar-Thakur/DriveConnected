# drive/views.py
import json
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_http_methods
from google_auth_oauthlib.flow import Flow
from django.conf import settings
from . import services
from .models import DriveToken, DriveFile

import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# ─── OAuth2 ──────────────────────────────────────────────────────────────────

def google_auth(request):
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=settings.GOOGLE_DRIVE_SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',  # forces refresh_token to be returned
    )
    request.session['oauth_state'] = state
    request.session.modified = True   # ← force Django to save the session
    request.session.save()            # ← explicitly save before redirect
    return redirect(auth_url)


# drive/views.py - oauth2_callback
# drive/views.py

def oauth2_callback(request):
    if not request.user.is_authenticated:
        return redirect('/admin/')

    # Get state from URL param directly (skip session state check)
    state = request.GET.get('state')
    
    if not state:
        return redirect('/drive/auth/')

    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=settings.GOOGLE_DRIVE_SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
        state=state,  # use state from URL, not session
    )
    
    # Tell oauthlib to skip state verification
    import os
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    flow.oauth2session.state = state  # force match
    
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    creds = flow.credentials

    DriveToken.objects.update_or_create(
        user=request.user,
        defaults={
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': ','.join(creds.scopes),
        }
    )
    return redirect('drive_list')
# ─── CRUD Views ───────────────────────────────────────────────────────────────

@login_required
def file_list(request):
    """List files from Google Drive."""
    query = request.GET.get('q', '')
    files = services.list_files(request.user, query=f"name contains '{query}'" if query else None)
    return render(request, 'drive/file_list.html', {'files': files, 'query': query})


@login_required
@require_http_methods(["POST"])
def file_upload(request):
    """Upload a file to Google Drive."""
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return JsonResponse({'error': 'No file provided'}, status=400)
    result = services.upload_file(
        request.user,
        uploaded_file,
        uploaded_file.name,
        uploaded_file.content_type,
    )
    return JsonResponse({'success': True, 'file': result})


@login_required
def file_download(request, file_id):
    """Download a file from Google Drive."""
    file_content = services.download_file(request.user, file_id)
    response = HttpResponse(file_content.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file_id}"'
    return response


@login_required
@require_http_methods(["POST"])
def file_update(request, file_id):
    """Rename or replace a file in Google Drive."""
    new_name = request.POST.get('name')
    new_file = request.FILES.get('file')
    result = services.update_file(request.user, file_id, new_name=new_name, new_file=new_file)
    return JsonResponse({'success': True, 'file': result})


@login_required
@require_http_methods(["POST", "DELETE"])
def file_delete(request, file_id):
    """Delete a file from Google Drive."""
    services.delete_file(request.user, file_id)
    return JsonResponse({'success': True})