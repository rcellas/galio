from django.http import JsonResponse
from .models import ScrapedItem

def scraped_items(request):
    data = list(ScrapedItem.objects.values())
    return JsonResponse(data, safe=False)