# Generated by Django 5.0.6 on 2024-06-10 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0004_alter_rcgrecord_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rcgrecord',
            name='rcg_meth',
            field=models.CharField(choices=[('cash', '现金'), ('wechatPay', '微信'), ('aliPay', '支付宝')], default='微信', max_length=20, verbose_name='充值方式'),
        ),
    ]
