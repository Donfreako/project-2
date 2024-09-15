from django.urls import path
from .views import RegisterView, LoginView, UserSearchView, SendFriendRequestView, RespondFriendRequestView, ListFriendsView, ListPendingFriendRequestsView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('friend-request/send/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('friend-request/respond/<int:pk>/', RespondFriendRequestView.as_view(), name='respond-friend-request'),
    path('friends/', ListFriendsView.as_view(), name='list-friends'),
    path('friend-request/pending/', ListPendingFriendRequestsView.as_view(), name='list-pending-friend-requests'),
]
