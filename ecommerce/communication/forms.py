from django import forms
from .models import CommunicationThread, CommunicationMessage

class StartThreadForm(forms.Form):
    subject = forms.CharField(max_length=255)
    message = forms.CharField(max_length=255, widget=forms.Textarea)
    
class ReplyToThreadForm(forms.ModelForm):
    class Meta:
        model = CommunicationMessage
        fields = ['content']
        
class ReplyToThreadWithFilesForm(forms.ModelForm):
    files = forms.FileField(
        widget=forms.ClearableFileInput(),
        required=False
    )

    class Meta:
        model = CommunicationMessage
        fields = ['content', 'files']