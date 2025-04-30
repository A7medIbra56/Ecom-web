from allauth.account.forms import SignupForm
from django import forms
from ecommerce.users.models import User, customer
    
    
class BaseAuthForm(SignupForm):
    """
    Base authentication form for all users regardless or role.
    This form is required by AllAuth to register a new user.
    Fields:
    Email, Username, Password1, Password2
    """
    
    def __init__(self, role, *args, **kwargs):
        self.role = role  # Store the role
        super().__init__(*args, **kwargs)  # Call parent constructor
    
    def save(self, request):   
        if not self.is_valid():  # Ensure form is validated before saving
            raise ValueError("Cannot save an invalid form")
             
        user = super().save(request)
        user.role = self.role  # Vendors get this role
        user.save()

        return user

class CustomerSignupForm(SignupForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def save(self, request):
        user = super().save(request)
        user.role = 'customer'  # Customers are always assigned this role
        user.save()
        customer.objects.create(
            user=user,
            date_of_birth=self.cleaned_data['date_of_birth']
        )
        return user
