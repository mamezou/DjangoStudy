from django.conf import settings
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager

# ここから下はユーザー認証周りの実装です。
# accountsのUserモデルを使う場合だけ、登録する
if settings.AUTH_USER_MODEL == 'accounts.User':
    class UserManager(BaseUserManager):
        """ユーザーマネージャー"""
        use_in_migrations = True

        def _create_user(self, email, password, **extra_fields):
            """Create and save a user with the given username, email, and
            password."""
            if not email:
                raise ValueError('The given email must be set')
            email = self.normalize_email(email)

            user = self.model(email=email, **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
            return user

        def create_user(self, email, password=None, **extra_fields):
            extra_fields.setdefault('is_staff', False)
            extra_fields.setdefault('is_superuser', False)
            return self._create_user(email, password, **extra_fields)

        def create_superuser(self, email, password, **extra_fields):
            extra_fields.setdefault('is_staff', True)
            extra_fields.setdefault('is_superuser', True)

            if extra_fields.get('is_staff') is not True:
                raise ValueError('Superuser must have is_staff=True.')
            if extra_fields.get('is_superuser') is not True:
                raise ValueError('Superuser must have is_superuser=True.')

            return self._create_user(email, password, **extra_fields)


    class User(AbstractBaseUser, PermissionsMixin):
        """カスタムユーザーモデル

        usernameを使わず、emailアドレスをユーザー名として使うようにしています。
        """
        email = models.EmailField(_('email address'), unique=True)
        first_name = models.CharField(_('first name'), max_length=30, blank=True)
        last_name = models.CharField(_('last name'), max_length=150, blank=True)

        is_staff = models.BooleanField(
            _('staff status'),
            default=False,
            help_text=_(
                'Designates whether the user can log into this admin site.'),
        )
        is_active = models.BooleanField(
            _('active'),
            default=True,
            help_text=_(
                'Designates whether this user should be treated as active. '
                'Unselect this instead of deleting accounts.'
            ),
        )
        date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

        objects = UserManager()

        EMAIL_FIELD = 'email'
        USERNAME_FIELD = 'email'
        REQUIRED_FIELDS = []

        class Meta:
            verbose_name = _('user')
            verbose_name_plural = _('users')

        def get_full_name(self):
            """Return the first_name plus the last_name, with a space in
            between."""
            full_name = '%s %s' % (self.first_name, self.last_name)
            return full_name.strip()

        def get_short_name(self):
            """Return the short name for the user."""
            return self.first_name

        def email_user(self, subject, message, from_email=None, **kwargs):
            """Send an email to this user."""
            send_mail(subject, message, from_email, [self.email], **kwargs)

        @property
        def username(self):
            return self.email


# 投稿機能のデータベースです。
class Post(models.Model):
    """
   　投稿クラス
    """

    title = models.CharField(
        verbose_name='タイトル',
        max_length=20,
        blank=False,
        null=False,
    )

    material = models.TextField(
        verbose_name='本文',
        blank=False,
        null=False,
    )

    category_choice = (
        (1, 'つぶやき'),
        (2, 'イベント'),
        (3, 'お知らせ'),
    )

    category = models.IntegerField(
        verbose_name='カテゴリ',
        choices=category_choice,
        blank=True,
        null=True,
    )

    image = models.ImageField(
        upload_to='static/image/',
        verbose_name='画像',
        blank=True,
        null=True,
    )

    date = models.DateTimeField(
        '日付',
        default=timezone.now,
    )

    # 以下、管理項目

    # 作成者(ユーザー)
    created_by = models.ForeignKey(
        User,
        verbose_name='作成者',
        blank=True,
        null=True,
        related_name='CreatedBy',
        on_delete=models.SET_NULL,
        editable=False,
    )

    # 投稿時間
    created_at = models.DateTimeField(
        verbose_name='作成時間',
        blank=True,
        null=True,
        editable=False,
        auto_now_add=True,
    )

    # 更新者(ユーザー)
    updated_by = models.ForeignKey(
        User,
        verbose_name='更新者',
        blank=True,
        null=True,
        related_name='UpdatedBy',
        on_delete=models.SET_NULL,
        editable=False,
    )

    # 更新時間
    updated_at = models.DateTimeField(
        verbose_name='更新時間',
        blank=True,
        null=True,
        editable=False,
    )

    def __str__(self):
        """
        リストボックスや管理画面での表示
        """
        return self.title

    class Meta:
        """
        管理画面でのタイトル表示
        """
        verbose_name = '投稿'
        verbose_name_plural = '投稿'


