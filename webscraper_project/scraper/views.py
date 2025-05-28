from django.http import JsonResponse
from django.db.models import Q
from .models import ScrapedItem

def scraped_items(request):
    region = request.GET.get('region') 
    organism = request.GET.get('organism')  
    start_date = request.GET.get('start_date')  
    end_date = request.GET.get('end_date')  

    filters = Q()
    if region:
        filters &= Q(region=region)
    if organism:
        filters &= Q(organism=organism)
    if start_date:
        filters &= Q(created_at__gte=start_date)
    if end_date:
        filters &= Q(created_at__lte=end_date)

    data = list(ScrapedItem.objects.filter(filters).values())
    return JsonResponse(data, safe=False)