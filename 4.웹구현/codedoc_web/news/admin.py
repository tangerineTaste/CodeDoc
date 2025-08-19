from django.contrib import admin
from .models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'source', 'pub_date', 'collected_time']
    list_filter = ['category', 'source', 'collected_time']
    search_fields = ['title', 'description']
    readonly_fields = ['collected_time']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-collected_time')
