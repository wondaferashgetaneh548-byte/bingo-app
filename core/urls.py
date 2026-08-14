from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView  # ይህን Import አድርግ

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bingo/', include('bingo.urls')),
    
    # ባዶ ገፅ (/) ሲከፈት በቀጥታ ወደ /bingo/ እንዲሄድ ያደርጋል
    path('', RedirectView.as_view(url='/bingo/', permanent=False)),
]