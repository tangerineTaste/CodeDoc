from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=50, blank=True, verbose_name='이름')
    # 선택지 정의
    EDUCATION_CHOICES = [
        (1, '고등학교 중퇴 이하'),
        (2, '고등학교 졸업'),
        (3, '대학교 중퇴/전문대 졸업'),
        (4, '대학교 졸업 이상'),
    ]
    
    AGE_GROUP_CHOICES = [
        (1, '18-25세'),
        (2, '26-35세'),
        (3, '36-45세'),
        (4, '46-55세'),
        (5, '56-65세'),
        (6, '66세 이상'),
    ]
    
    GENDER_CHOICES = [
        (1, '남성'),
        (2, '여성'),
    ]
    
    MARRIAGE_CHOICES = [
        (1, '기혼'),
        (2, '미혼/기타'),
    ]
    
    SAVINGS_CHOICES = [
        (1, '저축 안함'),
        (2, '일부 저축'),
        (3, '적극적 저축'),
    ]
    
    JOB_CHOICES = [
        (1, '일반 직장인/중간관리직'),
        (2, '고소득 전문직/사업가/경영진'),
        (3, '은퇴자/연금수급자'),
        (4, '저소득층/학생/비정규직'),
    ]

    # # 추가 필드들
    # phone = models.CharField(max_length=20, blank=True, verbose_name='휴대폰 번호')
    # annual_income = models.IntegerField(choices=[
    #     (1, '2,000만원 미만'),
    #     (2, '2,000만원 ~ 4,000만원'),
    #     (3, '4,000만원 ~ 6,000만원'),
    #     (4, '6,000만원 ~ 8,000만원'),
    #     (5, '8,000만원 ~ 1억원'),
    #     (6, '1억원 이상'),
    # ], null=True, blank=True, verbose_name='연간 소득')
    
    # 필드 정의
    교육수준분류 = models.IntegerField(choices=EDUCATION_CHOICES, null=True, blank=True, verbose_name='교육수준')
    연령대분류 = models.IntegerField(choices=AGE_GROUP_CHOICES, null=True, blank=True, verbose_name='연령대')
    가구주성별 = models.IntegerField(choices=GENDER_CHOICES, null=True, blank=True, verbose_name='성별')
    결혼상태 = models.IntegerField(choices=MARRIAGE_CHOICES, null=True, blank=True, verbose_name='결혼상태')
    저축여부 = models.IntegerField(choices=SAVINGS_CHOICES, null=True, blank=True, verbose_name='저축습관')
    직업분류1 = models.IntegerField(choices=JOB_CHOICES, null=True, blank=True, verbose_name='직업분류')
    금융위험태도 = models.IntegerField(default=0, null=True, blank=True, verbose_name='금융위험태도')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}의 프로필"
    
    class Meta:
        verbose_name = '사용자 프로필'
        verbose_name_plural = '사용자 프로필'

# User 생성 시 자동으로 Profile 생성
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)


# Create your models here.

