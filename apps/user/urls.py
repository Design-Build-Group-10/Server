from django.urls import path

from apps.shop.views.info import UserShopListView
from apps.user.views.message import AllMessagesView, UnreadMessagesView, MarkMessageAsReadView
from apps.user.views.product import UserAddressView, UserFollowedShopsView, UserFavoriteProductsView, \
    UserBrowseHistoryView
from apps.user.views.profile import ProfileView, UserAvatar, UserFace, ValidateTokenView
from apps.user.views.signIn import LoginView, FaceLoginView
from apps.user.views.signup import RegisterView

app_name = 'user'

urlpatterns = [
    path('', ProfileView.as_view(), name='用户个人信息'),
    path('signup/', RegisterView.as_view(), name='注册'),
    path('signIn/', LoginView.as_view(), name='登录'),
    path('face/signIn/', FaceLoginView.as_view(), name='人脸登录'),
    path("avatar/", UserAvatar.as_view(), name='用户头像'),
    path('face/', UserFace.as_view(), name='绑定用户人脸信息'),
    path('address/', UserAddressView.as_view(), name='user-address'),
    path('favorites/', UserFavoriteProductsView.as_view(), name='user-favorites'),
    path('followed-shops/', UserFollowedShopsView.as_view(), name='user-followed-shops'),
    path('browse-history/', UserBrowseHistoryView.as_view(), name='user-browse-history'),
    path('shops/', UserShopListView.as_view(), name='user-shop-list'),
    path('validate-token/', ValidateTokenView.as_view(), name='validate_token'),
    path('allmessages/', AllMessagesView.as_view(), name='all_messages'),
    path('unreadmessages/', UnreadMessagesView.as_view(), name='unread_messages'),
    path('markread/', MarkMessageAsReadView.as_view(), name='mark_read'),
    path('browse-history/', UserBrowseHistoryView.as_view(), name='user-browse-history'),
]
