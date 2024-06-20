from django.db import models


# Create your models here.
class CafeAdmin(models.Model):
    """ 管理员表 """
    admin_acct = models.CharField(max_length=20, primary_key=True, verbose_name="管理员账户")
    admin_pwd = models.CharField(max_length=20, null=False, verbose_name="管理员密码")
    admin_name = models.CharField(max_length=20, unique=True, null=False, verbose_name="管理员姓名")
    phone_name = models.CharField(max_length=20, unique=True, null=False, verbose_name="联系方式")

    class Meta:
        db_table = "cafe_admin"


class UserInfo(models.Model):
    """ 用户表 """
    ID_number = models.CharField(primary_key=True, max_length=50, verbose_name="身份证号")
    pwd = models.CharField(max_length=20, unique=True, null=False, blank=False, verbose_name="密码")
    balance = models.DecimalField(null=False, decimal_places=2, max_digits=8, verbose_name="账户余额")
    reg_time = models.DateField(auto_now_add=True, verbose_name="注册时间")
    admin_acct = models.ForeignKey("CafeAdmin", on_delete=models.CASCADE, verbose_name="管理员账号")

    class Meta:
        db_table = "user_info"


class Area(models.Model):
    """ 分区表 """
    area_id = models.CharField(max_length=10, primary_key=True, verbose_name="区号")
    area_name = models.CharField(max_length=20, null=False, unique=True, verbose_name="分区名称")
    price_ph = models.IntegerField(null=False, verbose_name="每小时单价")

    class Meta:
        db_table = "area"


class RcgRecord(models.Model):
    """ 充值记录表 """

    method = (
        ('cash', '现金'),
        ('wechatPay', '微信'),
        ('aliPay', '支付宝')
    )

    id_number = models.ForeignKey(to="UserInfo", verbose_name="身份证号", on_delete=models.CASCADE)
    rcg_time = models.DateTimeField(auto_now_add=True, verbose_name="充值时间")
    rcg_meth = models.CharField(max_length=20, null=False, verbose_name="充值方式", choices=method, default="wechatPay")
    rcg_fig = models.IntegerField(null=False, verbose_name="充值金额")

    class Meta:
        db_table = "rcg_record"


class Comp(models.Model):
    """ 电脑表 """

    state = (
        (0, '空闲'),
        (1, '忙碌')
    )

    comp_id = models.IntegerField(null=False, verbose_name="机号", primary_key=True)
    area_id = models.ForeignKey(Area, on_delete=models.CASCADE, verbose_name="所在区号")
    admin_acct = models.ForeignKey("CafeAdmin", on_delete=models.CASCADE, verbose_name="管理员账号")
    status = models.BooleanField(null=0, default=0, verbose_name="状态", choices=state)
    user_comp = models.ManyToManyField("UserInfo", through="PayRecord")

    class Meta:
        db_table = "computer"


class PayRecord(models.Model):
    """ 消费记录表 """
    id_number = models.ForeignKey("UserInfo", on_delete=models.CASCADE, verbose_name="身份证号")
    comp_id = models.ForeignKey("Comp", on_delete=models.CASCADE, verbose_name="机号")
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="上机时间")
    end_time = models.DateTimeField(auto_now=True, verbose_name="下机时间")
    to_pay = models.DecimalField(max_digits=6, decimal_places=2, null=False, verbose_name="消费金额")

    class Meta:
        db_table = "pay_record"
