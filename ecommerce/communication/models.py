from django.db import models
from django.contrib.auth import get_user_model
from ecommerce.users.models import User

THREAD_TYPE_CHOICES = [
    ('support_ticket', 'Support Ticket'),
    ('vendor_approval', 'Vendor Approval'),
]

THREAD_STATUS_CHOICES = [
    ('open', 'Open'),
    ('in_progress', 'In Progress'),
    ('closed', 'Closed'),
    ('awiating_vendor_reply', 'Awaiting Vendor Reply'),
    ('awiating_admin_reply', 'Awaiting Admin Reply'),
    ('awiating_customer_reply', 'Awaiting Customer Reply'),
]

class CommunicationThread(models.Model):
    type = models.CharField(max_length=20, choices=THREAD_TYPE_CHOICES)
    subject = models.CharField(max_length=255)
    
    # The recipient of the communication (either a user or a vendor)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_threads')
    vendor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='vendor_threads')
    
    status = models.CharField(max_length=30, choices=THREAD_STATUS_CHOICES, default='open')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.subject}"

class CommunicationMessage(models.Model):
    thread = models.ForeignKey(CommunicationThread, on_delete=models.CASCADE, related_name='messages')
    
    sender = models.CharField(
        max_length=10,
        choices=[('admin', 'Admin'), ('user', 'User'), ('vendor', 'Vendor')],
        default='admin'  # Admin is the default sender
    )
    
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message in {self.thread.subject} by {self.sender}"
    
class UploadedFile(models.Model):
    message = models.ForeignKey(CommunicationMessage, on_delete=models.CASCADE, related_name='files', null=True, blank=True,)
    file = models.FileField(upload_to='communication_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name