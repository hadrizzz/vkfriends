from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *


# Класс для регистрации нового пользователя
class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Класс для отправки заявки в друзья
class SendFriendRequestView(APIView):
    def post(self, request):
        serializer = FriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            friend_request = serializer.save()
            return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Класс для принятия или отклонения заявки в друзья
class RespondToFriendRequestView(APIView):
    def post(self, request, friend_request_id):
        friend_request = FriendRequest.objects.get(id=friend_request_id)
        serializer = Friendship(friend_request, data=request.data, partial=True)
        if serializer.is_valid():
            friend_request = serializer.save()
            return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Класс для получения списка заявок в друзья
class FriendRequestListView(APIView):
    def get(self, request):
        incoming_requests = FriendRequest.objects.filter(to_user=request.user)
        outgoing_requests = FriendRequest.objects.filter(from_user=request.user)
        incoming_requests_serializer = FriendRequestSerializer(incoming_requests, many=True)
        outgoing_requests_serializer = FriendRequestSerializer(outgoing_requests, many=True)
        response_data = {
            "incoming_requests": incoming_requests_serializer.data,
            "outgoing_requests": outgoing_requests_serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)


# Класс для получения списка друзей
class FriendListView(APIView):
    def get(self, request):
        friends = Friendship.objects.filter(user=request.user)
        friends_serializer = FriendshipSerializer(friends, many=True)
        return Response(friends_serializer.data, status=status.HTTP_200_OK)


# Класс для получения статуса дружбы
class FriendshipStatusView(APIView):
    def get(self, request, user_id):
        try:
            friend = Friendship.objects.get(user=request.user, friend=user_id)
            return Response({"status": "friends"}, status=status.HTTP_200_OK)
        except Friendship.DoesNotExist:
            pass
        try:
            friend_request = FriendRequest.objects.get(from_user=user_id, to_user=request.user)
            return Response({"status": "incoming_request"}, status=status.HTTP_200_OK)
        except FriendRequest.DoesNotExist:
            pass
        try:
            friend_request = FriendRequest.objects.get(from_user=request.user, to_user=user_id)
            return Response({"status": "outgoing_request"}, status=status.HTTP_200_OK)
        except FriendRequest.DoesNotExist:
            pass
        return Response({"status": "none"}, status=status.HTTP_200_OK)


# Класс для удаления друга из списка друзей
class RemoveFriendView(APIView):
    def post(self, request, friend_id):
        try:
            friend = Friendship.objects.get(user=request.user, id=friend_id)
            friend.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Friendship.DoesNotExist:
            pass

