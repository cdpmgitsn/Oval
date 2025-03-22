from django.urls import path
from .views import *

urlpatterns = [
    path('about/view/', AboutViewSet.as_view({'get': 'list'}), name='api-about-view'),
    path('tex_work/view/', Tex_workViewSet.as_view({'get': 'list'}), name='api-tex-work-view'),
    path('explanation/view/', ExplanationViewSet.as_view({'get': 'list'}), name='api-explanation-view'),
]