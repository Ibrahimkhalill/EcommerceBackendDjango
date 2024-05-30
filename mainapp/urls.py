from django.urls import path
from .views import *

urlpatterns = [
     
    path('index/',index,name='index'),
    path('send/otp/', send_otp, name='send_otp'),
    # path('send/otp-drm/', otp, name='send_otp'),
    path('pasword/send/otp/', Password_reset_send_otp, name='passwprd_send_otp'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('password/change/', changepassword, name='change-password'),
    path('password/reset/', reset_password, name='reset-password'),

    path('api/signup/', signup_view, name='signup'),
    path('api/google/signup/',google_signup,name='google'),
    path('api/login/',login_view,name='login'),
    path('api/google/login/',goole_login_view,name='login'),
    path('api/logout/',logout_view,name='login'),
    path('api/get-products/', get_products, name='get_videos'),
    path('api/get-brand/', get_brand, name='get-brand'),
    # path('api/get-product-subcategory/',get_product_subcategory, name='get-productsubcategory'),
    path('api/get-products/image/', get_product_image, name='get-image'),
    path('api/update-item/',update_item, name='update-item'),
    path('api/cart-items/',cart, name='cart-items'),
    path('api/place-order/', processOrder, name='place-order'),
    path('api/get-product-id/<int:id>/', get_product_id, name='get-product-id'),
    path('api/get-subcategory/',get_subcategory,name="get-subcategory"),
    path('api/get-displaymarketing/',get_displaymarketing,name="get-displaymarketing"),
    path('api/search-product/',itemSearch,name='search-product'),
    path('api/get-subcategory-product/', get_subcategory_product, name='get-subcategory-product'),
    path('api/save/feedback/', save_feedback, name='save-feedback'),
    path('api/save/ecomerce/issue/', save_issue, name='save-feedback'),
    # path('products/', product_list_create_view, name='product-list-create'),
    # path('products/<int:pk>/', product_detail_view, name='product-detail'),
    path('api/order/item/delete/<int:id>',delete_order_item,name="delete-order-item"),
    path('api/watchlist/item/delete/<int:id>',delete_wishlist_product,name="delete-watchlist-item"),

    path('api/watchlist/product/save/' , SaveWatchlistProduct, name = "save-watchlist-product"),
    path('api/wishListProduct/getAll/',getWishlistProduct,name='get-wishList-product'),
    path('api/question/answer/getAll/',getQuestionAnswer,name='get-question-answer'),
    path('api/question/answer/save/',SaveQuestionAnswer,name='save-question-answer'),
    path('api/shipping/address/getAll/',getShhipingAddress,name='get-shipping-address'),
    path('api/user/details/getAll/',getUserDeatils,name='get-user-details'),
    path('order/confirmation/',OrderConfirm,name='get-user-details'),

]
