from django.views.generic import ListView  
from .models import TCMDocument  

class DocumentListView(ListView):  
    model = TCMDocument  
    template_name = 'knowledge/doc_list.html'  
    context_object_name = 'documents'  
    paginate_by = 20  

    def get_queryset(self):  
        return TCMDocument.objects.filter(is_verified=True)  