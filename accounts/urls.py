from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('news/', views.News.as_view(), name='news'),
    path('start/', views.Start.as_view(), name='start'),
    path('recommended/', views.Recommended.as_view(), name='recommended'),
    path('category/', views.Category.as_view(), name='category'),
    path('favorite/', views.Favorite.as_view(), name='favorite'),
    path('inquiry/', views.ContactView.as_view(), name='inquiry'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('members/', views.Members.as_view(), name='members'),
    path('notice/', views.Notice.as_view(), name='notice'),
    path('ranking/', views.Ranking.as_view(), name='ranking'),
    path('information/', views.Information.as_view(), name='information'),
    path('user_create/', views.UserCreate.as_view(), name='user_create'),
    path('user_create/done/', views.UserCreateDone.as_view(), name='user_create_done'),
    path('user_create/complete/<token>/', views.UserCreateComplete.as_view(), name='user_create_complete'),
    path('user_detail/<int:pk>/', views.UserDetail.as_view(), name='user_detail'),
    path('user_update/<int:pk>/', views.UserUpdate.as_view(), name='user_update'),
    path('password_change/', views.PasswordChange.as_view(), name='password_change'),
    path('password_change/done/', views.PasswordChangeDone.as_view(), name='password_change_done'),
    path('password_reset/', views.PasswordReset.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDone.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(),
         name='password_reset_confirm'),
    path('password_reset/complete/', views.PasswordResetComplete.as_view(), name='password_reset_complete'),
    path('recipe_detail/<int:pk>/', views.PostDetailView.as_view(), name='recipe_detail'),
    path('recipe_create/', views.PostCreateView.as_view(), name='recipe_create'),
    path('recipe_update/<int:pk>/', views.PostUpdateView.as_view(), name='recipe_update'),
    path('recipe_delete/<int:pk>/', views.PostDeleteView.as_view(), name='recipe_delete'),
    path('recipe/', views.PostListView.as_view(), name='recipe'),
]
