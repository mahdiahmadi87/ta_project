from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from curriculum.views import home, topic_workspace

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('topic/<int:topic_id>/', topic_workspace, name='topic_workspace'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)