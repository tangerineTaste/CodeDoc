from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile
from django import forms
from django.forms import ModelForm

class SignupForm(UserCreationForm):
    """회원가입 폼"""
    full_name = forms.CharField(max_length=50, required=True, label='이름')  # name -> full_name
    age = forms.IntegerField(required=False, label='연령', min_value=18, max_value=100)
    
    # Profile 필드들 - 템플릿과 이름 맞춤
    education = forms.ChoiceField(
        choices=UserProfile.EDUCATION_CHOICES,
        required=False,
        label='교육수준',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    gender = forms.ChoiceField(
        choices=UserProfile.GENDER_CHOICES,
        required=False,
        label='성별',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    marital_status = forms.ChoiceField(
        choices=UserProfile.MARRIAGE_CHOICES,
        required=False,
        label='결혼상태',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    savings_habit = forms.ChoiceField(
        choices=UserProfile.SAVINGS_CHOICES,
        required=False,
        label='저축습관',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    job_category = forms.ChoiceField(
        choices=UserProfile.JOB_CHOICES,
        required=False,
        label='직업분류',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
    
    def save(self, commit=True):
        print(f"=== SIGNUP FORM SAVE METHOD CALLED ===")  # 디버깅
        print(f"Cleaned data: {self.cleaned_data}")  # 디버깅
        
        user = super().save(commit=False)
        
        if commit:
            user.save()
            print(f"User saved to DB: {user.username}")  # 디버깅
            
            # Profile 정보 저장 - 더 안전한 방식
            try:
                profile = user.profile
                print("Profile found via signal")  # 디버깅
            except:
                profile = UserProfile.objects.create(user=user)
                print("Profile created manually")  # 디버깅
            
            # 템플릿과 일치하는 필드 이름 사용
            full_name = self.cleaned_data.get('full_name', '')
            profile.name = full_name
            print(f"Setting profile name: {full_name}")  # 디버깅
            
            # 나이를 연령대분류로 변환
            age = self.cleaned_data.get('age')
            if age:
                if 18 <= age <= 25:
                    profile.연령대분류 = 1
                elif 26 <= age <= 35:
                    profile.연령대분류 = 2
                elif 36 <= age <= 45:
                    profile.연령대분류 = 3
                elif 46 <= age <= 55:
                    profile.연령대분류 = 4
                elif 56 <= age <= 65:
                    profile.연령대분류 = 5
                else:
                    profile.연령대분류 = 6
                print(f"Setting age group: {age} -> {profile.연령대분류}")  # 디버깅
            
            # 값이 비어있지 않을 때만 저장 (빈 문자열이나 None 체크)
            education = self.cleaned_data.get('education')
            if education:
                profile.교육수준분류 = int(education)
                print(f"Setting education: {education}")  # 디버깅
            
            gender = self.cleaned_data.get('gender')
            if gender:
                profile.가구주성별 = int(gender)
                print(f"Setting gender: {gender}")  # 디버깅
            
            marriage = self.cleaned_data.get('marital_status')
            if marriage:
                profile.결혼상태 = int(marriage)
                print(f"Setting marriage: {marriage}")  # 디버깅
            
            savings = self.cleaned_data.get('savings_habit')
            if savings:
                profile.저축여부 = int(savings)
                print(f"Setting savings: {savings}")  # 디버깅
            
            job = self.cleaned_data.get('job_category')
            if job:
                profile.직업분류1 = int(job)
                print(f"Setting job: {job}")  # 디버깅
            
            try:
                profile.save()
                print(f"Profile saved successfully: {profile.name}, User: {user.username}, Age Group: {profile.연령대분류}")  # 디버깅
            except Exception as e:
                print(f"Error saving profile: {e}")  # 디버깅
        
        return user

class ProfileForm(ModelForm):
    """프로필 수정 폼"""
    class Meta:
        model = UserProfile
        fields = [
            'name', '교육수준분류', '연령대분류', '가구주성별', '결혼상태',
            '저축여부', '직업분류1', # '금융위험태도'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            '교육수준분류': forms.Select(attrs={'class': 'form-control'}),
            '연령대분류': forms.Select(attrs={'class': 'form-control'}),
            '가구주성별': forms.Select(attrs={'class': 'form-control'}),
            '결혼상태': forms.Select(attrs={'class': 'form-control'}),
            '저축여부': forms.Select(attrs={'class': 'form-control'}),
            '직업분류1': forms.Select(attrs={'class': 'form-control'}),
            # '금융위험태도': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

# UserEditForm은 더 이상 필요없음 (User 모델에 추가 정보 없음)
