from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import send_bulk_sms
from .models import Contact

@csrf_exempt
def send_sms_view(request):
    if request.method == "POST":
        message_text = request.POST.get('message', '')
        recipients = list(Contact.objects.values_list('phone_number', flat=True))
        
        if recipients and message_text:
            response = send_bulk_sms(recipients, message_text)
            return JsonResponse({"status": "completed", "details": response}, json_dumps_params={'ensure_ascii': False})
        else:
            return JsonResponse({
                "status": "error", 
                "message": "ቁጥር በዳታቤዝ ውስጥ አልተገኘም ወይም የመልእክት ጽሁፉ ባዶ ነው!"
            }, json_dumps_params={'ensure_ascii': False})
            
    return JsonResponse({"message": "እባክዎን በ POST Request መልእክቱን ይላኩ።"}, json_dumps_params={'ensure_ascii': False})