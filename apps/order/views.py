from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.utils.response import success_response, bad_request_response
from .models import Order
from .serializers import OrderSerializer


class OrderListView(APIView):
    """
    查看用户所有订单
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            orders = Order.objects.filter(user=request.user)
            serializer = OrderSerializer(orders, many=True)
            return success_response(data=serializer.data)
        except Exception as e:
            return bad_request_response(f"Failed to retrieve orders: {str(e)}")


class OrderDetailView(APIView):
    """
    查看某个订单详情
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            serializer = OrderSerializer(order)
            return success_response(data=serializer.data)
        except Order.DoesNotExist:
            return bad_request_response(f"Order with id {order_id} not found")
        except Exception as e:
            return bad_request_response(f"Failed to retrieve order: {str(e)}")
