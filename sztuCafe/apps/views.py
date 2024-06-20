from django.shortcuts import render, redirect
from django.contrib.sessions.models import Session
from django.contrib import messages
from django.http import HttpResponse
from .models import *
from math import ceil


# Create your views here.
def index(req):
    return render(req, "index.html")


def login(req):
    if req.method == "POST":
        username = req.POST.get("username")
        password = req.POST.get("password")
        if username.strip() and password:
            try:
                user = UserInfo.objects.get(ID_number=username)
            except:
                message = "用户不存在，请注册"
                return render(req, "user_login.html", {"message": message})

            if user.pwd == password:
                req.session["user_id"] = user.ID_number
                return redirect("/apps/userhome")
            else:
                message = "账号或密码不正确"
                return render(req, "user_login.html", {"message": message})
        else:
            message = "请输入账号或密码"
            return render(req, "user_login.html", {"message": message})

    return render(req, "user_login.html")


def adlogin(req):
    """ 管理员登录 """
    if req.method == "POST":
        username = req.POST.get("username")
        password = req.POST.get("password")
        message = '请输入账号或密码'
        if username.strip() and password:
            try:
                account = CafeAdmin.objects.get(admin_acct=username)
            except:
                message = '用户不存在！！！'
                return render(req, "adlogin.html", {"message": message})

            if account.admin_pwd == password:
                return redirect("/apps/adhome")
            else:
                message = '密码不正确！！！'
                return render(req, "adlogin.html", {"message": message})
        else:
            return render(req, "adlogin.html", {"message": message})
    return render(req, "adlogin.html")


def recharge(req):
    """ 充值 """
    # 1、先查询是否已经登录，已经登录则拿到用户余额信息，否则跳到用户登录界面
    try:
        user_id = req.session["user_id"]
        user = UserInfo.objects.get(ID_number=user_id)
        balance = user.balance
    except KeyError:
        return HttpResponse("<div><h1>未登录，请先登录</h1><a href='/apps/login'>前往登录页面</a></div>")

    return render(req, "recharge.html", {
        "balance": balance
    })


def recharging(req):
    """ 充值 """
    try:
        user_id = req.session["user_id"]
        user = UserInfo.objects.get(ID_number=user_id)
    except KeyError:
        return HttpResponse("<div><h1>未登录，请先登录</h1><a href='/apps/login'>前往登录页面</a></div>")
    amount = req.GET.get("amount")
    method = req.GET.get("method")
    html = """
        <div>
            <h1>我是充值页面，没事别访问我</h1>
            <a href="/apps/userhome">前往首页</a><br/>
            <a href="/apps/recharge">前往充值页面</a>
        </div>
    """
    if amount and method:
        # 2、修改用户余额
        user.balance += int(amount)
        user.save()
        # 3、新增一条充值记录
        rcg = RcgRecord(id_number=user, rcg_fig=amount, rcg_meth=method)
        rcg.save()
        html = """
            <div>
                <h1>充值成功！！！</h1>
                <a href="/apps/userhome">返回首页</a><br/>
                <a href="/apps/recharge">返回充值页面</a>
            </div>
        """
    return HttpResponse(html)


def get_on_board(req):
    """ 用户上机 """
    one_pay_record = ''
    try:
        user_id = req.session["user_id"]
        pays = PayRecord.objects.filter(id_number_id=user_id)
        for pay in pays:
            if pay.start_time == pay.end_time:
                one_pay_record = pay
                break
    except KeyError:
        messages.error(req, "请先登录")

    if one_pay_record == '':
        comp = Comp.objects.filter(status=0)
        return render(req, "get_on_board.html", context={
            "comp": comp
        })
    else:
        messages.error(req, "用户已在上机")
        return redirect("/apps/userhome")


def boarding(req, nid):
    # 获取当前用户信息
    user_id = req.session["user_id"]
    user = UserInfo.objects.get(ID_number=user_id)

    # 通过url获取该电脑相关信息
    com = Comp.objects.get(comp_id=nid)

    # 检查用户余额是否足够上机
    if user.balance >= com.area_id.price_ph:
        # 修改电脑当前状态
        com.status = 1
        com.save()
        # 创建一条消费记录
        PayRecord.objects.create(id_number=user, comp_id=com, to_pay=com.area_id.price_ph)
        messages.success(req, "上机成功，玩得愉快！")
        return redirect("/apps/userhome")

    else:
        messages.error(req, "余额不足，请先充值！")
        return redirect("/apps/recharge")


def out_of_board(req):
    """ 下机 """
    # 更新下机时间，利用下机时间计算出上机时长
    try:
        user_id = req.session["user_id"]
        user = UserInfo.objects.get(ID_number=user_id)
    except KeyError:
        messages.error(req, "未登录状态，不可访问！")
        return redirect("/apps/login")

    pay_records = PayRecord.objects.filter(id_number=user)

    one_pay_record = ''
    for pay in pay_records:
        if pay.start_time == pay.end_time:
            one_pay_record = pay
            break

    if one_pay_record == '':
        req.session.flush()
        messages.success(req, "用户已退出登录")
        return redirect("/")

    one_pay_record.save()

    start_time = one_pay_record.start_time
    end_time = one_pay_record.end_time
    gap = end_time - start_time

    # 利用时长再次更新消费金额
    play_time_seconds = gap.seconds
    play_time_days = gap.days
    play_time_hours = ceil(play_time_days * 24 + play_time_seconds / 3600)

    total_pay=one_pay_record.to_pay * play_time_hours
    one_pay_record.to_pay = total_pay

    # 扣取用户余额
    user.balance -= one_pay_record.to_pay
    if user.balance < 0:
        messages.error(req, "余额不足，请前往充值！")
        return redirect("/apps/recharge")
    else:
        user.save()
        one_pay_record.save()
        com = one_pay_record.comp_id
        com.status = 0
        com.save()
        # 将消费记录展示给用户
        messages.success(req, f"消费成功，上机时间：{start_time}，下机时间：{end_time}，一共消费：{total_pay}元，欢迎下次光临！")
        # 将session里面的user信息给刷掉
        req.session.flush()

        return redirect("/")


def change_pwd(req):
    """ 用户修改密码 """
    if req.method == "POST":
        try:
            user_id = req.session["user_id"]
            user = UserInfo.objects.get(ID_number=user_id)
        except KeyError:
            messages.error(req, "用户未登录，请前往登录")
            return redirect("/apps/login")
        input_pwd = req.POST.get('password')
        new_pwd = req.POST.get('new_password')
        confirm_pwd = req.POST.get('confirm_password')

        if input_pwd == user.pwd:
            if new_pwd == confirm_pwd:
                user.pwd = new_pwd
                user.save()
                messages.success(req, "修改密码成功！")
                return redirect("/apps/userhome")
            else:
                messages.error(req, "两次密码输入不一致，请重新输入")
        else:
            messages.error(req, "旧密码错误，请重新输入")

        return redirect("/apps/changepwd")
    return render(req, "chg_pwd.html")


def check_spare(req):
    """ 管理员查询空闲机器 """
    computers = Comp.objects.filter(status=0)
    return render(req, "checkSpare.html", {"computers": computers})


def force_SD(req):
    """ 强制下机 """
    computers = Comp.objects.filter(status=1)
    return render(req, "admin_ForceSD.html", {"computers": computers})


def shutdown(req, nid):
    computer = Comp.objects.get(comp_id=nid)
    computer.status = 0
    pay_records = PayRecord.objects.filter(comp_id=computer)

    one_pay_record = ''
    for pay_record in pay_records:
        if pay_record.start_time == pay_record.end_time:
            one_pay_record = pay_record
            break
    if one_pay_record == '':
        return redirect("/apps/forceSD")
    else:
        user = one_pay_record.id_number

        one_pay_record.save()

        start_time = one_pay_record.start_time
        end_time = one_pay_record.end_time
        gap = end_time - start_time

        # 利用时长再次更新消费金额
        play_time_seconds = gap.seconds
        play_time_days = gap.days
        play_time_hours = ceil(play_time_days * 24 + play_time_seconds / 3600)

        one_pay_record.to_pay = one_pay_record.to_pay * play_time_hours

        # 扣取用户余额
        user.balance -= one_pay_record.to_pay
        if user.balance < 0:
            messages.error(req, "用户余额不足")

        else:
            one_pay_record.save()
            user.save()
            computer.save()
            messages.success(req, "用户已被下机")
        return redirect("/apps/forceSD")


def admin_index(req):
    return render(req, "admin_home.html")


def user_index(req):
    try:
        user_id = req.session["user_id"]
    except KeyError:
        messages.error(req, "请先进行登录")
        return redirect("/apps/login")

    return render(req, "user_home.html")


def register(req):
    """ 用户注册 """
    if req.method == "POST":
        id_num = req.POST.get("username")
        password = req.POST.get("password")
        repeatpwd = req.POST.get("repeatpwd")
        message = '请输入相关信息'
        if id_num and password and repeatpwd:
            if len(id_num) != 18:
                message = '身份证号不符合规范！！！'
                return render(req, "register.html", {"message": message})
            elif password != repeatpwd:
                message = '密码输入不一致！！！'
                return render(req, "register.html", {"message": message})
            else:
                message = '注册成功，请登录！'
                try:
                    admin_account = CafeAdmin.objects.get(admin_acct="admin1")
                    UserInfo.objects.create(ID_number=id_num, pwd=password, balance=0, admin_acct=admin_account)
                except Exception as e:
                    print(e)
                    message = '该身份证号已被注册，请登录！'
                finally:
                    return render(req, "user_login.html", {"message": message})
        else:
            return render(req, "register.html", {"message": message})

    return render(req, "register.html")
