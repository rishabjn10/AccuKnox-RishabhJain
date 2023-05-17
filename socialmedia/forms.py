from django import forms
from .models import UserProfile, FriendRequest

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name','email','gender']
        
class FriendRequestForm(forms.ModelForm):
    class Meta:
        model = FriendRequest
        fields = ['sender','receiver']