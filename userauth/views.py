from django.http import HttpResponse
from django.contrib.auth.views import LoginView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth import logout as logout_user
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
import traceback
import stripe


stripe.api_key = settings.STRIPE_API_KEY


def index(request):
    username = ""
    if request.user.is_authenticated:
        username = request.user.username
    return HttpResponse("Placeholder for ddh shiny app. Username: {}".format(username))


class Login(LoginView):
    template_name = 'userauth/Login_form.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    template_name = 'userauth/PasswordResetConfirm_form.html'


class PasswordResetComplete(PasswordResetCompleteView):
    template_name = 'userauth/PasswordResetComplete_form.html'


def logout(request):
    logout_user(request)
    return redirect('login')


def auth(request):
    if request.user.is_authenticated:
        return HttpResponse(status=200)
    return HttpResponse(status=403)


@csrf_exempt
def webhook(request):
    try:
        signature = request.headers.get('stripe-signature')
        event = stripe.Webhook.construct_event(
            payload=request.body, sig_header=signature, secret=settings.STRIPE_WEBHOOK_SECRET)
        print("Webhook event received:", event.type)
        if event.type == "customer.subscription.created" or event.type == "customer.subscription.updated":
            on_customer_subscription_changed(request, event)
        elif event.type == "customer.subscription.deleted":
            on_customer_subscription_deleted(request, event)
        return JsonResponse({"success": True})
    except:
        print('Error while parsing webhook:')
        traceback.print_exc()
        return JsonResponse({"success": False})


def on_customer_subscription_changed(request, event):
    obj = event.data["object"]
    status = obj["status"]
    user, created = get_or_create_user_for_stripe_event_object(obj)
    user.is_active = status == "active"
    user.save()
    print("Updated user {} with subscription status {}".format(user.username, status))
    if created:
        reset_url = make_reset_password_url(request, user)
        print("Sending email with reset url: {} to user {}".format(reset_url, user.email))
        send_new_user_email(user, reset_url)


def on_customer_subscription_deleted(request, event):
    obj = event.data["object"]
    user, created = get_or_create_user_for_stripe_event_object(obj)
    user.is_active = False
    user.save()
    print("Deactivated user {}".format(user.username))


def get_or_create_user_for_stripe_event_object(obj):
    customer = stripe.Customer.retrieve(obj["customer"])
    if not customer.email:
        raise ValueError("Customer has no email:" + str(customer))
    try:
        return User.objects.get(username=customer.email), False
    except User.DoesNotExist:
        return User.objects.create_user(username=customer.email, email=customer.email), True


def make_reset_password_url(request, user):
    token_generator = PasswordResetTokenGenerator()
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)
    return request.build_absolute_uri('/accounts/reset/{}/{}/'.format(uid, token))


def send_new_user_email(user, reset_password_url):
    subject = "Welcome to Data-Driven Hypothesis"
    message = """
        To get started, click to set a password for your account: {}
        
        If you have any problems, reply to this email for support.
        
        We're eager to see what you can discover!
    """.format(reset_password_url)
    send_mail(
        subject,
        message,
        settings.EMAIL_FROM_USER,
        [user.email],
        fail_silently=False,
    )
