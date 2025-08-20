from django.db import models
from django.utils import timezone

class News(models.Model):
    CATEGORY_CHOICES = [
        ('주식/증권', '주식/증권'),
        ('채권', '채권'),
        ('금리', '금리'),
        ('환율/외환', '환율/외환'),
        ('부동산', '부동산'),
        ('은행/대출', '은행/대출'),
        ('보험/연금', '보험/연금'),
        ('투자/자산관리', '투자/자산관리'),
        ('경제지표', '경제지표'),
        ('정책/규제', '정책/규제'),
        ('기타금융', '기타금융'),
    ]
    
    title = models.CharField(max_length=500)
    description = models.TextField()
    link = models.URLField(max_length=1000)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='기타금융')
    source = models.CharField(max_length=100, default='네이버 뉴스')
    pub_date = models.CharField(max_length=20)  # 원본 날짜 형식 저장
    collected_time = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-collected_time']
        unique_together = ['title', 'link']  # 중복 방지
    
    def __str__(self):
        return self.title[:50]
