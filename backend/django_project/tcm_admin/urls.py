from django.contrib import admin  
from django.urls import path  
from django.conf import settings  
from django.conf.urls.static import static  
from knowledge import views  

urlpatterns = [  
    path('admin/', admin.site.urls),  
    path('docs/', views.DocumentListView.as_view(), name='doc-list'),  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  