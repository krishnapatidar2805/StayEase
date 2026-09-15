import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from .forms import RegisterForm, LoginForm, ProfileForm, ForgotPasswordForm, ResetPasswordForm
from .models import UserProfile
from .sms import send_otp_sms
from bookings.models import Booking, Payment
from rooms.models import Wishlist
from rooms.ai import personalized_suggestions_for_user


def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = True
            user.save()

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.phone = form.cleaned_data.get('phone', '')
            profile.is_email_verified = True
            profile.email_otp = ''
            profile.save()

            login(request, user)
            messages.success(request, f'Account created successfully! Welcome to StayEase, {user.first_name or user.username}!')
            return redirect('core:home')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def verify_email_view(request):
    return redirect('core:home')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']

            username = identifier
            # Check if identifier is an email
            if '@' in identifier:
                user_by_email = User.objects.filter(email__iexact=identifier).first()
                if user_by_email:
                    username = user_by_email.username
            else:
                # Check if identifier is a phone number
                clean_phone = identifier.replace(' ', '').replace('-', '')
                if (clean_phone.isdigit() or clean_phone.startswith('+')) and len(clean_phone) >= 10:
                    profile_by_phone = UserProfile.objects.filter(phone__endswith=clean_phone[-10:]).first()
                    if profile_by_phone:
                        username = profile_by_phone.user.username

            user = authenticate(request, username=username, password=password)
            if user:
                # Ensure profile exists and is verified so login is never blocked
                profile, _ = UserProfile.objects.get_or_create(user=user)
                if not profile.is_email_verified:
                    profile.is_email_verified = True
                    profile.save()

                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                next_url = request.GET.get('next')
                return redirect(next_url or 'core:home')
            else:
                messages.error(request, 'Invalid username/email or password.')
                form.add_error(None, 'Invalid username/email or password.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('core:home')


def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                otp = f"{random.randint(100000, 999999)}"
                user.profile.email_otp = otp
                user.profile.save()
                send_mail(
                    'StayEase Password Reset OTP',
                    f'Your password reset OTP is: {otp}',
                    'noreply@stayease.com',
                    [email],
                    fail_silently=True,
                )
                request.session['reset_user_id'] = user.id
                messages.success(request, 'OTP sent! Check the console/email for your reset code.')
                return redirect('accounts:reset_password')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email.')
    else:
        form = ForgotPasswordForm()

    return render(request, 'accounts/forgot_password.html', {'form': form})


def reset_password_view(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('accounts:forgot_password')

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(id=user_id)
                if user.profile.email_otp == form.cleaned_data['otp']:
                    user.set_password(form.cleaned_data['new_password'])
                    user.save()
                    user.profile.email_otp = ''
                    user.profile.save()
                    del request.session['reset_user_id']
                    messages.success(request, 'Password reset successful! Please log in.')
                    return redirect('accounts:login')
                else:
                    messages.error(request, 'Invalid OTP.')
            except User.DoesNotExist:
                return redirect('accounts:forgot_password')
    else:
        form = ResetPasswordForm()

    return render(request, 'accounts/reset_password.html', {'form': form})


@login_required
def dashboard_view(request):
    bookings = Booking.objects.filter(user=request.user).select_related('room')[:5]
    wishlist = Wishlist.objects.filter(user=request.user).select_related('room')
    suggestions = personalized_suggestions_for_user(request.user, limit=4)
    payments = Payment.objects.filter(booking__user=request.user)[:5]

    context = {
        'bookings': bookings,
        'wishlist': wishlist,
        'suggestions': suggestions,
        'payments': payments,
        'total_bookings': Booking.objects.filter(user=request.user).count(),
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            request.user.first_name = form.cleaned_data.get('first_name', request.user.first_name)
            request.user.last_name = form.cleaned_data.get('last_name', request.user.last_name)
            request.user.save()
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        })

    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        if request.user.check_password(old_password):
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Password changed. Please log in again.')
            logout(request)
            return redirect('accounts:login')
        else:
            messages.error(request, 'Old password is incorrect.')
    return render(request, 'accounts/change_password.html')
