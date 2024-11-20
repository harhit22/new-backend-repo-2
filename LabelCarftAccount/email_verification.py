from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from .token import user_tokenizer_generate


def send_verification_email(user, request):
    if request.path.startswith('/account/api/'):
        current_site = get_current_site(request)
        subject = 'Account verification'
        message = render_to_string('LabelCarftAccount/api_email_registration.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': user_tokenizer_generate.make_token(user)
        })
        user.email_user(subject=subject, message=message)
