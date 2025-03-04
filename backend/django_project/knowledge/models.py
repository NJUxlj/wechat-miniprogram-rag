from django.db import models  
from django.contrib import admin  
from django.utils import timezone 

class TCMDocument1(models.Model):  
    title = models.CharField(max_length=200)  
    content = models.TextField()  
    source = models.FileField(upload_to="docs/")  
    upload_time = models.DateTimeField(auto_now_add=True)  
    
    def __str__(self):  
        return self.title  
    


class TCMDocument(models.Model):  
    DOC_TYPE_CHOICES = [  
        ('theory', '中医理论'),  
        ('prescription', '方剂'),  
        ('herb', '中药材'),  
        ('case', '医案'),  
    ]  

    title = models.CharField("标题", max_length=200)  
    content = models.TextField("内容")  
    doc_type = models.CharField("类型", max_length=20, choices=DOC_TYPE_CHOICES)  
    source_file = models.FileField("源文件", upload_to='tcm_docs/')  
    upload_time = models.DateTimeField("上传时间", default=timezone.now)  
    is_verified = models.BooleanField("已审核", default=False)  

    class Meta:  
        verbose_name = "中医文献"  
        verbose_name_plural = "中医文献管理"  
        indexes = [  
            models.Index(fields=['title']),  
            models.Index(fields=['doc_type']),  
        ]  

@admin.register(TCMDocument)  
class TCMDocumentAdmin(admin.ModelAdmin):  
    list_display = ("title", "upload_time")  
    search_fields = ("title", "content")  