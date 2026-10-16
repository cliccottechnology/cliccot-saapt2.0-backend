from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentViewSet,
    ClassSectionViewSet,
    SchoolClassViewSet,
    SectionViewSet,
    AcademicYearViewSet
)

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'class-sections', ClassSectionViewSet, basename='class-section')
router.register(r'classes', SchoolClassViewSet, basename='school-class')
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'academic-years', AcademicYearViewSet, basename='academic-year')

urlpatterns = [
    path('', include(router.urls)),
]
