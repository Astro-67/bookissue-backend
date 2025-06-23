from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    # Comments for specific tickets
    path('tickets/<int:ticket_id>/comments/', views.CommentListCreateView.as_view(), name='ticket_comments'),
    path('<int:pk>/', views.CommentDetailView.as_view(), name='comment_detail'),
]
