from django.shortcuts import redirect
from django.contrib import messages

class SuperuserOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if request.path not in ['/admin/login/', '/admin/logout/']:
                if not request.user.is_authenticated:
                    messages.error(request, 'Đã xảy ra lỗi xác thực!')
                    # return redirect('/admin/login/')
                if not request.user.is_superuser:
                    messages.error(request, 'Chỉ Superuser được phép!')
                    # return redirect('/')
        
        return self.get_response(request)