from utils.logging import *

def view_logs_category(request):
    return view_logs_base(request,'Category.jsonl')

def delete_logs_category(request):
    return clear_logs(request,'Category.jsonl')