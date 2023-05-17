from django.contrib import admin
from django.urls import include, path
from socialmedia import views as SocialMedia 


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # User profile
    path('create_user/', SocialMedia.create_user_profile),
    path('search_users/', SocialMedia.search_users),
    
    # 
    path('accounts/login/',SocialMedia.user_login),
    
    # Friend Requests
    path('friend_request/send/',SocialMedia.send_friend_request),
    path('friend_request/accept_reject/',SocialMedia.friend_request),
    path('friend_request/list/',SocialMedia.friends),
]