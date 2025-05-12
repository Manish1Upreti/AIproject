# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     #path('', include('sentimentanalysis.urls')),
#     path('', include('youtubevideosplitter.urls')),
# ]
#
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# for RESTFULapis
from django.urls import path, include

urlpatterns = [
    path('', include('youtubevideosplitter.urls')),
]
