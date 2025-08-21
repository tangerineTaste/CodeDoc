from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.conf import settings
from .forms import ProfileForm, SignupForm

# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '회원가입이 완료되었습니다.')
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

@login_required
def profile_edit(request):
    """프로필 수정"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필이 성공적으로 수정되었습니다.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})

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