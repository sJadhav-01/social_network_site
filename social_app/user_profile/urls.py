from django.urls import path 
from . import views



urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('signup/', views.Signup.as_view(), name='signup'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('profile/', views.Profile.as_view(), name='profile'),
    path('otheruserprofile/', views.OtherUserProfile.as_view(), name='otheruserprofile'),
    path('api/like/<int:post_id>/', views.PostLikeCheck.as_view(), name='postlike'),
    path('api/friendreqto/<int:other_user_id>/', views.FriendRequestCheck.as_view(), name='friendrequestcheck'),
    path('friends/', views.FriendsList.as_view(), name='profile'),
    path('api/reqaccept/<int:received_req_id>/', views.FriendRequestAction.as_view(), name='friendrequestaction' )

]
