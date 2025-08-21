from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', '교육수준분류', '연령대분류', '직업분류1', 'created_at']
    list_filter = ['교육수준분류', '연령대분류', '직업분류1', '저축여부']
    search_fields = ['user__username', 'name']
    readonly_fields = ['created_at', 'updated_at']
