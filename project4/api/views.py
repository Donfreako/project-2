from django.contrib.auth import authenticate
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, RegisterSerializer, FriendRequestSerializer
from .models import FriendRequest
from django.contrib.auth.models import User
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class UserSearchView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'username']
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        if search:
            if '@' in search:
                queryset = queryset.filter(email__iexact=search)
            else:
                queryset = queryset.filter(username__icontains=search)
        return queryset

class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        from_user = request.user
        to_user_id = request.data.get('to_user_id')
        to_user = User.objects.get(id=to_user_id)
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user, status='pending').exists():
            return Response({"error": "Friend request already sent"}, status=status.HTTP_400_BAD_REQUEST)
        friend_request = FriendRequest(from_user=from_user, to_user=to_user, status='pending')
        friend_request.save()
        return Response({"message": "Friend request sent"}, status=status.HTTP_201_CREATED)

class RespondFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        friend_request = FriendRequest.objects.get(id=pk)
        if friend_request.to_user != request.user:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        request_status = request.data.get('status')
        if request_status not in ['accepted', 'rejected']:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        friend_request.status = request_status
        friend_request.save()
        if request_status == 'accepted':
            friend_request.from_user.friends.add(friend_request.to_user)
        if request_status == 'rejected':
            friend_request.status = request_status
            friend_request.save()
        return Response({"message": f"Friend request {request_status}"}, status=status.HTTP_200_OK)

class ListFriendsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(
            Q(from_user__to_user=self.request.user, from_user__status='accepted') |
            Q(to_user__from_user=self.request.user, to_user__status='accepted')
        )

class ListPendingFriendRequestsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user, status='pending')
