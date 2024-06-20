from django.urls import path
from . import views

urlpatterns = [
    path("login", views.login),
    path("adlogin", views.adlogin),
    path("recharge", views.recharge),
    path("shangji", views.get_on_board),
    path("changepwd", views.change_pwd),
    path("checkspare", views.check_spare),
    path("forceSD", views.force_SD),
    path("shutdown/<int:nid>",views.shutdown),
    path("adhome", views.admin_index),
    path("userhome", views.user_index),
    path("register",views.register),
    path("recharging",views.recharging),
    path("getOnBoard/<int:nid>",views.boarding),
    path("outLogin",views.out_of_board)
]
