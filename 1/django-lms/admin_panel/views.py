import platform
import sys
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def diagnostics(request):
    context = {
        'server_time': timezone.now(),
        'python_version': sys.version.split()[0],
        'platform': platform.platform(),
    }
    return render(request, 'admin_panel/diagnostics.html', context)


@login_required
def admin_dashboard(request):
    return render(request, 'admin_panel/dashboard.html')
