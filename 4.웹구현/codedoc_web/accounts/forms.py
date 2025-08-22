from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile
from django import forms
from django.forms import ModelForm

class SignupForm(UserCreationForm):
    """회원가입 폼"""
    name = forms.CharField(max_length=50, required=True, label='이름')  # 변경

    # Profile 필드들
    교육수준분류 = forms.ChoiceField(
        choices=UserProfile.EDUCATION_CHOICES,
        required=False,
        label='교육수준',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    연령대분류 = forms.ChoiceField(
        choices=UserProfile.AGE_GROUP_CHOICES,
        required=False,
        label='연령대',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    가구주성별 = forms.ChoiceField(
        choices=UserProfile.GENDER_CHOICES,
        required=False,
        label='성별',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    결혼상태 = forms.ChoiceField(
        choices=UserProfile.MARRIAGE_CHOICES,
        required=False,
        label='결혼상태',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    저축여부 = forms.ChoiceField(
        choices=UserProfile.SAVINGS_CHOICES,
        required=False,
        label='저축습관',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    직업분류1 = forms.ChoiceField(
        choices=UserProfile.JOB_CHOICES,
        required=False,
        label='직업분류',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
    
    def save(self, commit=True):
        print("=== SignupForm.save() 호출됨 ===")  # 디버깅
        user = super().save(commit=False)
        
        if commit:
            user.save()
            print(f"User 저장됨: {user.username}")  # 디버깅
            
            # Profile 정보 저장
            profile = user.profile
            print(f"Profile 객체: {profile}")  # 디버깅
            
            profile.name = self.cleaned_data['name']
            profile.교육수준분류 = self.cleaned_data.get('교육수준분류') or None
            profile.연령대분류 = self.cleaned_data.get('연령대분류') or None
            profile.가구주성별 = self.cleaned_data.get('가구주성별') or None
            profile.결혼상태 = self.cleaned_data.get('결혼상태') or None
            profile.저축여부 = self.cleaned_data.get('저축여부') or None
            profile.직업분류1 = self.cleaned_data.get('직업분류1') or None
            
            print(f"프로필 데이터: 이름={profile.name}, 교육수준={profile.교육수준분류}")  # 디버깅
            
            profile.save()
            print("Profile 저장 완료!")  # 디버깅
        
        return user

class ProfileForm(ModelForm):
    """프로필 수정 폼"""
    class Meta:
        model = UserProfile
        fields = [
            'name', '교육수준분류', '연령대분류', '가구주성별', '결혼상태',
            '저축여부', '직업분류1', '금융위험태도'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            '교육수준분류': forms.Select(attrs={'class': 'form-control'}),
            '연령대분류': forms.Select(attrs={'class': 'form-control'}),
            '가구주성별': forms.Select(attrs={'class': 'form-control'}),
            '결혼상태': forms.Select(attrs={'class': 'form-control'}),
            '저축여부': forms.Select(attrs={'class': 'form-control'}),
            '직업분류1': forms.Select(attrs={'class': 'form-control'}),
            '금융위험태도': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

# UserEditForm은 더 이상 필요없음 (User 모델에 추가 정보 없음)