from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bingo/', include('bingo.urls')),  # የ bingo አፕን URL እዚህ እናገናኛለን
]