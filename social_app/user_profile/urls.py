from django.urls import path 
from . import views



urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('signup/', views.Signup.as_view(), name='signup'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('profile/', views.Profile.as_view(), name='profile'),
    path('otheruserprofile/', views.OtherUserProfile.as_view(), name='otheruserprofile'),
    path('friends/', views.FriendsList.as_view(), name='friends'),
    path('search/', views.SearchResult.as_view(), name='search'),
    path('editprofiledetails/', views.EditProfile.as_view(), name='editprofile'),
    path('addotherdetails/', views.AddProfileDetails.as_view(), name='addotherdetails'),

    # api endpoints
    path('api/like/<int:post_id>/', views.PostLikeCheck.as_view(), name='postlike'),
    path('api/friendreqto/<int:other_user_id>/', views.FriendRequestCheck.as_view(), name='friendrequestcheck'),
    path('api/reqaccept/<int:received_req_id>/', views.FriendRequestAction.as_view(), name='friendrequestaction'),
    path('api/postcomment/<int:post_id>/', views.AddComment.as_view(), name='addcomment'),
    path('api/deletepost/<int:post_id>/', views.DeletePost.as_view(), name='deletepost'),
]
