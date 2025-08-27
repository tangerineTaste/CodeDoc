from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile
from django import forms
from django.forms import ModelForm

class SignupForm(UserCreationForm):
    """회원가입 폼"""
    
    email = forms.EmailField(
        required=True,
        label='이메일',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@codedoc.com'
        })
    )
    
    full_name = forms.CharField(max_length=50, required=True, label='이름')
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
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        print(f"=== SIGNUP FORM SAVE METHOD CALLED ===")
        print(f"Cleaned data: {self.cleaned_data}")
        
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']  # 이메일 저장 추가
        
        if commit:
            user.save()
            print(f"User saved to DB: {user.username}")
            
            # Profile 정보 저장 - 더 안전한 방식
            try:
                profile = user.profile
                print("Profile found via signal")
            except:
                profile = UserProfile.objects.create(user=user)
                print("Profile created manually")
            
            # 템플릿과 일치하는 필드 이름 사용
            full_name = self.cleaned_data.get('full_name', '')
            profile.name = full_name
            print(f"Setting profile name: {full_name}")
            
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
                print(f"Setting age group: {age} -> {profile.연령대분류}")
            
            # 값이 비어있지 않을 때만 저장
            education = self.cleaned_data.get('education')
            if education:
                profile.교육수준분류 = int(education)
                print(f"Setting education: {education}")
            
            gender = self.cleaned_data.get('gender')
            if gender:
                profile.가구주성별 = int(gender)
                print(f"Setting gender: {gender}")
            
            marriage = self.cleaned_data.get('marital_status')
            if marriage:
                profile.결혼상태 = int(marriage)
                print(f"Setting marriage: {marriage}")
            
            savings = self.cleaned_data.get('savings_habit')
            if savings:
                profile.저축여부 = int(savings)
                print(f"Setting savings: {savings}")
            
            job = self.cleaned_data.get('job_category')
            if job:
                profile.직업분류1 = int(job)
                print(f"Setting job: {job}")
            
            try:
                profile.save()
                print(f"Profile saved successfully: {profile.name}, User: {user.username}, Age Group: {profile.연령대분류}")
            except Exception as e:
                print(f"Error saving profile: {e}")
        
        return user

class ProfileForm(ModelForm):
    """프로필 수정 폼"""
    class Meta:
        model = UserProfile
        fields = [
            'name', #'phone',
            '교육수준분류', '연령대분류', '가구주성별', '결혼상태',
            '저축여부', '직업분류1',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '이름을 입력하세요'
            }),
            # 'phone': forms.TextInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': '010-0000-0000'
            # }),
            '교육수준분류': forms.Select(attrs={
                'class': 'form-control'
            }),
            '연령대분류': forms.Select(attrs={
                'class': 'form-control'
            }),
            '가구주성별': forms.Select(attrs={
                'class': 'form-control'
            }),
            '결혼상태': forms.Select(attrs={
                'class': 'form-control'
            }),
            '저축여부': forms.Select(attrs={
                'class': 'form-control'
            }),
            '직업분류1': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 빈 선택지를 각 필드에 추가
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ChoiceField):
                choices = list(field.choices)
                if not any(choice[0] == '' for choice in choices):
                    field.choices = [('', '선택해주세요')] + choices
                    
        # 필드별 라벨 설정
        self.fields['name'].label = '이름'
        # self.fields['phone'].label = '휴대폰 번호'
        self.fields['교육수준분류'].label = '교육수준'  
        self.fields['연령대분류'].label = '연령대'
        self.fields['가구주성별'].label = '성별'
        self.fields['결혼상태'].label = '결혼상태'
        self.fields['저축여부'].label = '저축습관'
        self.fields['직업분류1'].label = '직업분류'
        
        # # 휴대폰 번호는 선택 필드로 설정
        # self.fields['phone'].required = False

# UserEditForm은 더 이상 필요없음 (User 모델에 추가 정보 없음)
