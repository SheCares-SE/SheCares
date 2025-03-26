from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def home_redirect(request):
    return redirect('accounts:login')  # Redirects home to patient dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('patient/', include('patient.urls', namespace='patient')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('gync/', include('gync.urls', namespace='gync')),
    path('', home_redirect, name='home_redirect'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
