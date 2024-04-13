from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.crypt.api import signer
from common.models import BaseModel


class Org(BaseModel):
    name = models.CharField(max_length=128, db_comment=_('部门名称'))
    dept_id = models.IntegerField(unique=True, db_comment=_('部门ID'))
    parent_dept_id = models.IntegerField(db_comment=_('父部门ID'))
    level = models.IntegerField(null=True, blank=True, db_comment=_('部门级别'))
    path = models.CharField(max_length=100, null=True, blank=True, db_comment='部门级别路径')

    class Meta:
        verbose_name = '组织架构'
        app_label = 'user'


class User(BaseModel):
    REQUIRED_FIELDS = ['name']
    USERNAME_FIELD = 'username'

    ROLE_CHOICES = (
        ('user', _('用户')),
        ('admin', _('管理员')),
    )
    ACCOUNT_TYPE_CHOICE = (
        ('inner', _('内部')),
        ('inner_temp', _('内部临时')),
        ('out_user', _('外部人员')),
        ('out_sys', _('外部系统')),
        ('partners', _('合作伙伴账号')),
    )

    dept = models.ForeignKey(Org, blank=True, null=True, on_delete=models.SET_NULL, db_comment=_('部门'))
    username = models.CharField(max_length=128, unique=True, db_comment=_('用户名'))
    name = models.CharField(max_length=128, db_comment=_('名称'))
    emp_no = models.CharField(max_length=12, unique=True, db_comment=_('EmpNo'))
    _password = models.CharField(max_length=100, null=True, blank=True, db_comment=_('密码'))
    is_active = models.BooleanField(default=True, db_comment=_('是否可用'))
    role = models.CharField(choices=ROLE_CHOICES, default='user', max_length=50, db_comment=_('角色'))
    account_type = models.CharField(choices=ACCOUNT_TYPE_CHOICE, max_length=50, db_comment=_('账号类型'))

    @property
    def is_anonymous(self):
        """
        Always return False. This is a way of comparing User objects to
        anonymous user.
        """
        return False

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    @property
    def password(self):
        return signer.decrypt(self._password)

    @password.setter
    def password(self, dat):
        self._password = signer.encrypt(dat)

    def check_password(self, password):
        if not self._password:
            return False
        return password == self.password

    @property
    def dept_name(self):
        return self.dept.name if self.dept else ""

    @property
    def role_display(self):
        return self.get_role_display()

    @property
    def account_display(self):
        return self.get_account_type_display()

    @property
    def is_active_display(self):
        return "是" if self.is_active else "否"

    def __str__(self):
        return f'{self.name}({self.username})'

    class Meta:
        verbose_name = '用户'
        app_label = "user"
