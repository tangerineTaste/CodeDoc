# customer_support/admin.py
from django.contrib import admin
from .models import Notice

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'is_active', 'is_important', 'view_count']
    list_filter = ['is_active', 'is_important', 'created_at']
    search_fields = ['title', 'content']
    list_editable = ['is_active', 'is_important']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'content', 'author')
        }),
        ('설정', {
            'fields': ('is_active', 'is_important')
        }),
        ('통계', {
            'fields': ('view_count',),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # 새로 생성하는 경우
            obj.author = request.user
        super().save_model(request, obj, form, change)