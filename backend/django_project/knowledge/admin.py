from django.contrib import admin  
from .models import TCMDocument  

class TCMDocumentAdmin(admin.ModelAdmin):  
    list_display = ('title', 'doc_type', 'upload_time', 'is_verified')  
    list_filter = ('doc_type', 'is_verified')  
    search_fields = ('title', 'content')  
    readonly_fields = ('upload_time',)  
    fieldsets = (  
        (None, {  
            'fields': ('title', 'doc_type')  
        }),  
        ('内容管理', {  
            'fields': ('content', 'source_file'),  
            'classes': ('wide',)  
        }),  
        ('状态管理', {  
            'fields': ('is_verified', 'upload_time'),  
            'classes': ('collapse',)  
        }),  
    )  

admin.site.register(TCMDocument, TCMDocumentAdmin)  