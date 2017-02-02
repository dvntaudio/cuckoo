# Copyright (C) 2010-2013 Claudio Guarnieri.
# Copyright (C) 2014-2017 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import calendar
import datetime
import functools
import json
import os
import StringIO

from django.core.servers.basehttp import FileWrapper
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from cuckoo.misc import cwd
from cuckoo.common.config import Config

def view_error(request, msg, status=500):
    return render(request, "errors/error.html", {"error": msg}, status=status)

def get_directory_size(path):
    """recursive"""

    size = 0
    for path_dir, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(path_dir, f)
            size += os.path.getsize(fp)

    return size

def _api_post(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        request = args[0]

        if not request.is_ajax():
            return json_error_response("Request was not ajax")

        args += (json.loads(request.body),)
        return func(*args, **kwargs)
    return inner

api_post = lambda func: staticmethod(_api_post(csrf_exempt(require_http_methods(["POST"])(func))))

def _api_get(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        return func(*args, **kwargs)
    return inner

api_get = lambda func: staticmethod(_api_get(require_http_methods(["GET"])(func)))

class JsonSerialize(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "to_dict"):
            return obj.to_dict()

        if isinstance(obj, datetime.datetime):
            if obj.utcoffset() is not None:
                obj = obj - obj.utcoffset()
            return calendar.timegm(obj.timetuple()) + obj.microsecond / 1000000.0
        raise TypeError("%r is not JSON serializable" % obj)

def render_template(request, template_name, **kwargs):
    env = {}

    if hasattr(request, "resolver_match"):
        resolver_match = request.resolver_match
        env["view_name"] = resolver_match.view_name
        env["view_kwargs"] = resolver_match.kwargs
        env["url_name"] = resolver_match.url_name
        env["cfg"] = Config.from_confdir(cwd("conf"))

    kwargs["env"] = env

    return render(request, template_name, kwargs)

def json_response(message, status=200):
    return JsonResponse({
        "status": True if status == 200 else False,
        "message": message
    }, encoder=JsonSerialize, status=status)

def json_error_response(message):
    return json_response(message, 501)

def json_fatal_response(message):
    return json_response(message, 500)

def file_response(data, filename, content_type):
    response = StreamingHttpResponse(FileWrapper(data), content_type=content_type)

    if isinstance(data, file) and hasattr(data, "name"):
        response["Content-Length"] = os.path.getsize(data.name)
    elif isinstance(data, StringIO.StringIO) and hasattr(data, "buf"):
        response["Content-Length"] = len(data.buf)

    response["Content-Disposition"] = "attachment; filename=%s" % filename
    return response
