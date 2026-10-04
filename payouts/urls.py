from django.urls import path

from payouts.views import ObligationCreateView, RecipientCreateView

urlpatterns = [
    path("recipients/", RecipientCreateView.as_view()),
    path("obligations/", ObligationCreateView.as_view())
]