# customer_support/models.py
from django.db import models
from django.contrib.auth.models import User

class Notice(models.Model):
    title = models.CharField(max_length=200, verbose_name='제목')
    content = models.TextField(verbose_name='내용')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='작성자')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    is_active = models.BooleanField(default=True, verbose_name='게시 여부')
    is_important = models.BooleanField(default=False, verbose_name='중요 공지')
    view_count = models.PositiveIntegerField(default=0, verbose_name='조회수')
    
    class Meta:
        ordering = ['-created_at']  # 최신순 정렬
        verbose_name = '공지사항'
        verbose_name_plural = '공지사항'
    
    def __str__(self):
        return self.title
    
    @property
    def is_new(self):
        """최근 7일 이내 작성된 글인지 확인"""
        from django.utils import timezone
        from datetime import timedelta
        return (timezone.now() - self.created_at) <= timedelta(days=7)