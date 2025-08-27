from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from .forms import ProfileForm, SignupForm
from django.contrib import messages
from django.contrib.messages import get_messages

# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(settings.LOGIN_URL)
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def profile(request):
    """마이페이지 메인"""
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'profile': request.user.profile
    })

def profile_edit(request):
    """프로필 수정"""
    
    # GET 요청 시 모든 기존 메시지 강제 삭제
    if request.method == 'GET':
        # 메시지 스토리지 직접 접근해서 완전 삭제
        storage = messages.get_messages(request)
        storage.used = True  # 모든 메시지를 사용된 것으로 표시
        storage._queued_messages = []  # 대기 중인 메시지 삭제
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)
        
        # 이메일 처리
        email = request.POST.get('email', '')
        if email:
            request.user.email = email
            request.user.save()
        
        if form.is_valid():
            profile = form.save()
            return redirect('/accounts/profile/?saved=true')
        else:
            messages.error(request, '입력 정보를 다시 확인해주세요.')
    else:
        form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'user': request.user,
        'profile': request.user.profile
    })

@login_required
def password_change(request):
    """비밀번호 변경"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # 세션 유지
            messages.success(request, '비밀번호가 성공적으로 변경되었습니다.')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/password_change.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def signup_view(request):
    print(f"=== SIGNUP_VIEW CALLED - Method: {request.method} ===")  # 디버깅
    
    if request.method == 'POST':
        print(f"POST data received: {request.POST}")  # 디버깅
        form = SignupForm(request.POST)  # UserCreationForm을 SignupForm으로 변경
        if form.is_valid():
            print("Form is valid, saving user...")  # 디버깅
            user = form.save()
            print(f"User created: {user.username}")  # 디버깅
            username = form.cleaned_data.get('username')
            return redirect('accounts:login')
        else:
            print(f"Form errors: {form.errors}")  # 디버깅
    else:
        form = SignupForm()  # UserCreationForm을 SignupForm으로 변경
    return render(request, 'accounts/signup.html', {'form': form})

def logout_view(request):
    """로그아웃 봰"""
    print(f"Logout view called - Method: {request.method}")  # 디버깅
    
    if request.method == 'POST':
        print("POST request - logging out user")  # 디버깅
        logout(request)
        return redirect('/')
    else:
        print("GET request - showing logout page")  # 디버깅
        try:
            return render(request, 'accounts/logout_simple.html')
        except Exception as e:
            print(f"Template error: {e}")  # 디버깅
            return redirect('/')

