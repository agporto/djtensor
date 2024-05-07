from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import  TFModelViewSet, TrainingSessionViewSet, EpochViewSet, TestViewSet

router = DefaultRouter()
router.register(r'tfmodel', TFModelViewSet, 'tfmodels')
router.register(r'trainingsession', TrainingSessionViewSet, 'trainingsessions')
router.register(r'epoch', EpochViewSet, 'epochs')
router.register(r'tests', TestViewSet, 'tests')

urlpatterns = [
    path('', include(router.urls)),
]
