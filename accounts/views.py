from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView, FormView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, resolve_url
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views import generic

from .models import Post
from .forms import (
    LoginForm, UserCreateForm, UserUpdateForm, MyPasswordChangeForm,
    MyPasswordResetForm, MySetPasswordForm, PostCreateForm, ContactForm,
)

User = get_user_model()


class Index(generic.TemplateView):
    template_name = 'accounts/index.html'


class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'accounts/login.html'


class Logout(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""
    template_name = 'accounts/index.html'


class News(generic.TemplateView):
    template_name = 'accounts/news.html'


class Start(generic.TemplateView):
    template_name = 'accounts/start.html'


class Recommended(generic.TemplateView):
    template_name = 'accounts/recommended.html'


class Category(generic.TemplateView):
    template_name = 'accounts/category.html'


class Favorite(generic.TemplateView):
    template_name = 'accounts/favorite.html'


class Information(generic.TemplateView):
    template_name = 'accounts/information.html'


class Inquiry(generic.TemplateView):
    template_name = 'accounts/inquiry.html'


class Members(generic.TemplateView):
    template_name = 'accounts/members.html'


class Notice(generic.TemplateView):
    template_name = 'accounts/notice.html'


class Ranking(generic.TemplateView):
    template_name = 'accounts/ranking.html'


class UserCreate(generic.CreateView):
    """ユーザー仮登録"""
    template_name = 'accounts/user_create.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単。
        # 退会処理も、is_activeをFalseにするだけにしておくと捗ります。
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject_template = get_template('accounts/mail_template/create/subject.txt')
        subject = subject_template.render(context)

        message_template = get_template('accounts/mail_template/create/message.txt')
        message = message_template.render(context)

        user.email_user(subject, message)
        return redirect('accounts:user_create_done')


class UserCreateDone(generic.TemplateView):
    """ユーザー仮登録したよ"""
    template_name = 'accounts/user_create_done.html'


class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'accounts/user_create_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # まだ仮登録で、他に問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()


class OnlyYouMixin(UserPassesTestMixin):
    """本人か、スーパーユーザーだけユーザーページアクセスを許可する"""
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser


class UserDetail(OnlyYouMixin, generic.DetailView):
    """ユーザー情報詳細画面ビュー"""
    model = User
    template_name = 'accounts/user_detail.html'


class UserUpdate(OnlyYouMixin, generic.UpdateView):
    """ユーザー情報更新ビュー"""
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/user_form.html'

    def get_success_url(self):
        return resolve_url('accounts:user_detail', pk=self.kwargs['pk'])


class PasswordChange(PasswordChangeView):
    """パスワード変更ビュー"""
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('accounts:password_change_done')
    template_name = 'accounts/password_change.html'


class PasswordChangeDone(PasswordChangeDoneView):
    """パスワード変更しました"""
    template_name = 'accounts/password_change_done.html'


class PasswordReset(PasswordResetView):
    """パスワード変更用URLの送付ページ"""
    subject_template_name = 'accounts/mail_template/password_reset/subject.txt'
    email_template_name = 'accounts/mail_template/password_reset/message.txt'
    template_name = 'accounts/password_reset_form.html'
    form_class = MyPasswordResetForm
    success_url = reverse_lazy('accounts:password_reset_done')


class PasswordResetDone(PasswordResetDoneView):
    """パスワード変更用URLを送ったよと伝えるページ"""
    template_name = 'accounts/password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    """新パスワード入力ページ"""
    form_class = MySetPasswordForm
    success_url = reverse_lazy('accounts:password_reset_complete')
    template_name = 'accounts/password_reset_confirm.html'


class PasswordResetComplete(PasswordResetCompleteView):
    """新パスワードを設定完了しましたよページ"""
    template_name = 'accounts/password_reset_complete.html'


class PostFilterView(generic.ListView):
    """
    ビュー：フィルターのやつ
    """
    model = Post
    template_name = 'accounts/post.html'

    # 1ページの表示するコンテンツ数
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        表示データの設定
        """
        kwargs['title'] = 'title'
        # 表示データを追加したい場合は、ここでキーを追加しテンプレート上で表示する
        # 例：kwargs['sample'] = 'sample'
        return super().get_context_data(object_list=object_list, **kwargs)


class PostListView(generic.ListView):
    """
    一覧ページ
    """
    model = Post
    template_name = 'accounts/post.html'
    paginate_by = 5


class PostDetailView(generic.DetailView):
    """
    ビュー：詳細画面
    """
    model = Post
    template_name = 'accounts/post_detail.html'

    def get_context_data(self, **kwargs):
        """
        表示データの設定
        """
        # 表示データの追加はここでする予定 例： kwargs['sample'] = 'sample'
        return super().get_context_data(**kwargs)


class PostCreateView(generic.CreateView):
    """
    ビュー：登録画面
    """
    model = Post
    template_name = 'accounts/post_create.html'
    form_class = PostCreateForm
    success_url = reverse_lazy('accounts:post')

    def form_valid(self, form):
        """
        登録処理
        """
        result = super().form_valid(form)
        messages.success(
            self.request, '「{}」を作成しました'.format(form.instance))
        return result


class PostUpdateView(OnlyYouMixin, generic.UpdateView):
    """
    ビュー：更新画面
    """
    model = Post
    form_class = PostCreateForm
    success_url = reverse_lazy('accounts:post')

    def form_valid(self, form):
        """
        更新処理
        """
        result = super().form_valid(form)
        messages.success(
            self.request, '「{}」を更新しました'.format(form.instance))
        return result


class PostDeleteView(OnlyYouMixin, generic.DeleteView):
    """
    ビュー：削除画面
    """
    model = Post
    form_class = PostCreateForm
    success_url = reverse_lazy('accounts:post')

    def delete(self, request, *args, **kwargs):
        """
        削除処理
        """
        result = super().delete(request, *args, **kwargs)
        messages.success(
            self.request, '「{}」を削除しました'.format(self.object))
        return result


class ContactView(FormView):
    """お問い合わせフォーム"""
    template_name = 'accounts/inquiry.html'
    form_class = ContactForm
    success_url = reverse_lazy('accounts:index')

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.send_email()
        return super(ContactView, self).form_valid(form)

