import os
from django.template import engines, Context, Template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags
from email.mime.image import MIMEImage 

def send_email(subject, html_path, to_email, context_data, no_reply=False, inline_images=False):
    """
    Sends an email by rendering the content from an HTML file inside a given template layout.

    :param subject: Email subject.
    :param html_path: Path to the HTML content file (e.g., 'emails/messages/order_placed.html').
    :param to_email: Email or list of emails.
    :param context_data: Dictionary of variables to be passed to both template and message.
    """

    if isinstance(to_email, str):
        to_email = [to_email]

    django_engine = engines['django']

    # Load the HTML file (which is the block content)
    with open(os.path.join(settings.BASE_DIR, html_path), 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Compile and render the final full email
    compiled_template = django_engine.from_string(html_content)
    final_rendered = compiled_template.render(context_data)

    # Extract plain text for fallback
    plain_text = strip_tags(final_rendered)

    if no_reply:
        from_email = settings.NO_REPLY_FROM_EMAIL
    else:
        from_email = settings.DEFAULT_FROM_EMAIL

    # Send it
    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_text,  # Plain text version
        from_email=from_email,
        to=to_email,
    )

    image_paths = {
        
    }

    default_paths = {
        "logo_primary_linear": settings.BASE_DIR + '/shared/static/shared/img/branding/logo_primary_linear.png',
    }
    
    image_paths.update(default_paths)
    
    if inline_images:
        image_paths.update(inline_images)
    
    if image_paths:
        for cid, path in image_paths.items():
            with open(path, 'rb') as img:
                mime_img = MIMEImage(img.read())
                mime_img.add_header('Content-ID', f'<{cid}>')
                mime_img.add_header('Content-Disposition', 'inline', filename=os.path.basename(path))
                email.attach(mime_img)
    
    email.attach_alternative(final_rendered, "text/html")  # HTML version
    email.send()
