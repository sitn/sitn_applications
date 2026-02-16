from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template, render_to_string

LANG = settings.LANGUAGE_CODE

def _render_email_templates(template_name, template_data):
    html_template_name = '{}_{}.html'.format(template_name, LANG)
    return (
        render_to_string(html_template_name, template_data),
        get_template(html_template_name).render(template_data),
    )


def send_email(subject, message='', to=None, template_name=None, template_data=None):
    """
    Will send templated email to recipients.

    Parameters
    ----------
    subject : str
        The subject of email
    message : str
        The email message, also the body if template_name is None
    to : str or Identity or None
        If str, email is expected to be a valid email address
        If str[], email is sent to all addresses provided
    template_name : str or None
        Any valid template as found in ./templates folder
    template_data : Dict or None
        A Dict containing data for the provided template name. Ignored if template_name
        is not given.
    """
    if template_name:
        if template_data is None:
            template_data = {'messages': [message]}
        (message, html_message) = _render_email_templates(template_name, template_data)
    if isinstance(to, str):
        recipient_list = [to]
    else:
        recipient_list = to
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        html_message=html_message,
        fail_silently=False,
    )
