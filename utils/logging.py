import json
import logging
from datetime import datetime

##import for view_logs_base
import os
from django.http import JsonResponse, Http404,HttpResponseForbidden
from django.conf import settings

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_object = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(log_object, ensure_ascii=False)

def view_logs_base(request,file_name):

    ### check if super user
    if not request.user.is_superuser:
        return HttpResponseForbidden(content="You do not have permission to view this")
    

    log_path = os.path.join(settings.BASE_DIR, 'logs', file_name)
    if not os.path.exists(log_path):
        raise Http404("Log file not found")

    level_filter = request.GET.get("level")

    logs = []

    with open(log_path, "r", encoding="utf-8") as f:
        for line in f.readlines():
            try:
                log = json.loads(line)
                if level_filter and log["level"] != level_filter.upper():
                    continue
                logs.append(log)
            except json.JSONDecodeError:
                continue

    return JsonResponse({"logs": logs}, json_dumps_params={"ensure_ascii": False})

def clear_logs(request,file_name):
    """
    Xoá nội dung file log (truncate). Trả về JSON success/fail.
    POST only. (Frontend phải gửi CSRF token)
    """
    ### check if super user
    if not request.user.is_superuser:
        return HttpResponseForbidden(content="You do not have permission to view this")
    

    log_path = os.path.join(settings.BASE_DIR, 'logs', file_name)
    if not os.path.exists(log_path):
        raise Http404("Log file not found")
    
    try:
        # Option 1: truncate file
        with open(log_path, "w", encoding="utf-8") as f:
            f.truncate(0)
        return JsonResponse({"ok": True, "message": "Log file cleared."})
    except Exception as e:
        return JsonResponse({"ok": False, "message": f"Failed to clear log: {e}"}, status=500)