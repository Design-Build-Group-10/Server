from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.user.models import Message
from common.utils.response import success_response, bad_request_response


class AllMessagesView(APIView):
    """
    获取用户的所有消息
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # 获取用户的所有消息
        all_messages = user.messages.all()
        messages_data = [
            {
                'id': message.id,
                'title': message.title,
                'description': message.description,
                'created_at': message.created_at,
                'is_read': message.is_read,
                'read_at': message.read_at,
                'type': message.type,  # 可选字段
            }
            for message in all_messages
        ]
        return success_response(data={'all_messages': messages_data})


class UnreadMessagesView(APIView):
    """
    获取用户的未读消息
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # 获取未读消息
        unread_messages = user.messages.filter(is_read=False)
        messages_data = [
            {
                'id': message.id,
                'title': message.title,
                'description': message.description,
                'created_at': message.created_at,
            }
            for message in unread_messages
        ]
        return success_response(data={'unread_messages': messages_data})


class MarkMessageAsReadView(APIView):
    """
    标记某条消息为已读
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, message_id):
        user = request.user
        try:
            # 获取消息，确保消息属于当前用户
            message = user.messages.get(id=message_id)
            if message.is_read:
                return bad_request_response(f"Message with id {message_id} is already marked as read")

            # 标记为已读
            message.mark_as_read()

            return success_response(message="Message marked as read successfully")

        except Message.DoesNotExist:
            return bad_request_response(f"Message with id {message_id} not found")
