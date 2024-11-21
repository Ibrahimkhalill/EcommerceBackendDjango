from django.urls import path
from .views import *

urlpatterns = [
     
   path("api/save/product/", save_product, name="save-product"),
   path("api/get/order/",get_order_details, name="get-order"),
   path("api/get/status/",get_status, name="get-status"),
   path("api/put/status/change/", status_change, name="status-change"),
   path("api/get/category/", get_category, name="get-category-name"),
   path("api/save/category/", saveCategory, name="save-category"),
   path("api/delete/category/<int:id>/", delete_category, name="delete-category"),
   path("api/update/category/", update_category, name="update-category"),
   path("api/get/sub/category/", get_subCategory, name="get-sub-category"),
   path("api/save/sub/category/", saveSubCategory, name="save-sub-category"),
   path("api/Update/sub/category/", update_subcategory, name="save-update-category"),
   path("api/delete/sub/category/<int:id>/", delete_subcategory, name="delete-sub-category"),
   path("api/delete/variation/<int:id>/", delete_variation),
   path("api/delete/stock/<int:id>/", delete_Stock),


   #brand api
   path("api/get/brand/", get_brand, name="get-brand"),
   path("api/save/brand/", saveBrand, name="save-brand"),
   path("api/update/brand/", update_brand, name="update-brand"),
   path("api/delete/brand/<int:id>/", delete_brand, name="delete-brand"),

   #material api
   path("api/get/material/", get_material, name="get-material"),
   path("api/save/material/", saveMaterial, name="save-material"),
   path("api/update/material/", update_material, name="update-material"),
   path("api/delete/material/<int:id>/", delete_material, name="delete-material"),

  #color api
   path("api/get/color/", get_color, name="get-color"),
   path("api/save/color/", saveColor, name="save-color"),
   path("api/update/color/", update_color, name="update-color"),
   path("api/delete/color/<int:id>/", delete_color, name="delete-color"),

   #size api
   path("api/get/size/", get_size, name="get-size"),
   path("api/save/size/", saveSize, name="save-size"),
   path("api/update/size/", update_Size, name="update-size"),
   path("api/delete/size/<int:id>/", delete_size, name="delete-size"),

    #question & answer api
   path("api/get/question_answer/", get_question_answer, name="get-question-answer"),
   path("api/update/question_answer/", update_question_answer, name="update-question-answer"),
   path("api/delete/question_answer/<int:id>/", delete_size, name="delete-size"),

   #searc transaction

   path("api/search/transaction/", search_transaction, name="search-transaction"),

   #stock api

   path("api/get/stockAll/", get_stock, name="get-stock"),
   path("api/get/sales-summary/", sales_summary),

   #admin product api
   path("api/get/productAll/", get_product_all, name="get-product-all"),
   path("api/get/All/", get_all, name="get-all"),
   path("api/get-product/<int:id>/",get_product_by_id, name="get-product-id"),
   path("api/upadate/product/<int:id>",update_product, name="update-product"),
   path("api/delete/product/<int:id>",delete_product, name="delete-product"),
   path("api/delete/order/<int:id>",delete_order, name="delete-order"),

   # slider api

   path("api/get/display-slider/", get_display_slider),
   path("api/save/display-slider/", saveDisplaySlider),
   path("api/delete/display-slider/<int:id>", deleteDisplaySlider),


]
