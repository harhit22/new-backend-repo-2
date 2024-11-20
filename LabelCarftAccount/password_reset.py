from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_password_reset_email(user, reset_url):
    subject = 'Password Reset Requested'
    html_message = render_to_string('LabelCarftAccount/password_change.html', {
        'user': user,
        'reset_url': reset_url,
    })
    plain_message = strip_tags(html_message)
    from_email = 'harshitshrimalee.wevois@gmail.com'
    to_email = user.email

    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
