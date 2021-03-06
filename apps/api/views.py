import os
import base64
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from apps.profile.models import Profile
from apps.reader.models import UserSubscription, UserSubscriptionFolders
from utils import json_functions as json

def add_site_load_script(request, token):
    code = 0
    folder_image = open(os.path.join(settings.MEDIA_ROOT, 'img/icons/silk/folder.png'))
    folder_image = base64.b64encode(folder_image.read())
    accept_image = open(os.path.join(settings.MEDIA_ROOT, 'img/icons/silk/accept.png'))
    accept_image = base64.b64encode(accept_image.read())
    error_image = open(os.path.join(settings.MEDIA_ROOT, 'img/icons/silk/error.png'))
    error_image = base64.b64encode(error_image.read())
    try:
        profile = Profile.objects.get(secret_token=token)
        usf = UserSubscriptionFolders.objects.get(
            user=profile.user
        )
    except Profile.DoesNotExist:
        code = -1
    except UserSubscriptionFolders.DoesNotExist:
        code = -1
    
    return render_to_response('api/bookmarklet_subscribe.js', 
        {
            'code': code,
            'token': token,
            'folders': usf.folders,
            'folder_image': folder_image,
            'accept_image': accept_image,
            'error_image': error_image,
        }, 
        context_instance=RequestContext(request),
        mimetype='application/javascript')

def add_site(request, token):
    code = 0
    url = request.GET['url']
    folder = request.GET['folder']
    callback = request.GET['callback']
    
    if not url:
        code = -1
    else:
        try:
            profile = Profile.objects.get(secret_token=token)
            code, message, us = UserSubscription.add_subscription(
                user=profile.user, 
                feed_address=url,
                folder=folder,
                bookmarklet=True
            )
        except Profile.DoesNotExist:
            code = -1
    
    if code > 0:
        message = 'OK'
        
    return HttpResponse(callback + '(' + json.encode({
        'code':    code,
        'message': message,
        'usersub': us and us.feed.pk,
    }) + ')', mimetype='text/plain')