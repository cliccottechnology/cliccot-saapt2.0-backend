from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentViewSet,
    ClassSectionViewSet,
    SchoolClassViewSet,
    SectionViewSet,
    AcademicYearViewSet,
    BloodGroupViewSet,
    RoomViewSet
)

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'class-sections', ClassSectionViewSet, basename='class-section')
router.register(r'classes', SchoolClassViewSet, basename='school-class')
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'academic-years', AcademicYearViewSet, basename='academic-year')
router.register(r'blood-groups', BloodGroupViewSet, basename='blood-group')
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'rooms', RoomViewSet, basename='room')

# Explicit, descriptive action-based endpoints
urlpatterns = [
    # --- Student APIs ---
    path('list-students/', StudentViewSet.as_view({'get': 'list'}), name='list_students'),
    path('add-student/', StudentViewSet.as_view({'post': 'create'}), name='add_student'),
    path('view-student/<int:pk>/', StudentViewSet.as_view({'get': 'retrieve'}), name='view_student'),
    path('edit-student/<int:pk>/', StudentViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='edit_student'),
    path('delete-student/<int:pk>/', StudentViewSet.as_view({'delete': 'destroy'}), name='delete_student'),
    path('student-stats/', StudentViewSet.as_view({'get': 'stats'}), name='student_stats'),
    path('export-students/', StudentViewSet.as_view({'get': 'export'}), name='export_students'),
    path('student-id-card/<int:pk>/', StudentViewSet.as_view({'get': 'id_card'}), name='student_id_card'),
    path('bulk-allocate-students/', StudentViewSet.as_view({'post': 'bulk_allocate'}), name='bulk_allocate_students'),
    path('get-academic-records/<int:pk>/', StudentViewSet.as_view({'get': 'academic_records'}), name='get_academic_records'),
    path('add-academic-record/<int:pk>/', StudentViewSet.as_view({'post': 'academic_records'}), name='add_academic_record'),

    # --- Class & Section Allocation APIs ---
    path('list-class-sections/', ClassSectionViewSet.as_view({'get': 'list'}), name='list_class_sections'),
    path('add-class-section/', ClassSectionViewSet.as_view({'post': 'create'}), name='add_class_section'),
    path('view-class-section/<int:pk>/', ClassSectionViewSet.as_view({'get': 'retrieve'}), name='view_class_section'),
    path('edit-class-section/<int:pk>/', ClassSectionViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='edit_class_section'),
    path('delete-class-section/<int:pk>/', ClassSectionViewSet.as_view({'delete': 'destroy'}), name='delete_class_section'),
    path('class-section-students/<int:pk>/', ClassSectionViewSet.as_view({'get': 'students'}), name='class_section_students'),

    # --- School Class CRUD APIs ---
    path('list-classes/', SchoolClassViewSet.as_view({'get': 'list'}), name='list_classes'),
    path('get-classes/', SchoolClassViewSet.as_view({'get': 'list'}), name='get_classes'),
    path('add-class/', SchoolClassViewSet.as_view({'post': 'create'}), name='add_class'),
    path('view-class/<int:pk>/', SchoolClassViewSet.as_view({'get': 'retrieve'}), name='view_class'),
    path('edit-class/<int:pk>/', SchoolClassViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='edit_class'),
    path('delete-class/<int:pk>/', SchoolClassViewSet.as_view({'delete': 'destroy'}), name='delete_class'),

    # --- Section CRUD APIs ---
    path('list-sections/', SectionViewSet.as_view({'get': 'list'}), name='list_sections'),
    path('get-sections/', SectionViewSet.as_view({'get': 'list'}), name='get_sections'),
    path('add-section/', SectionViewSet.as_view({'post': 'create'}), name='add_section'),
    path('view-section/<int:pk>/', SectionViewSet.as_view({'get': 'retrieve'}), name='view_section'),
    path('edit-section/<int:pk>/', SectionViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='edit_section'),
    path('delete-section/<int:pk>/', SectionViewSet.as_view({'delete': 'destroy'}), name='delete_section'),

    # --- Academic Year CRUD APIs ---
    path('list-academic-years/', AcademicYearViewSet.as_view({'get': 'list'}), name='list_academic_years'),
    path('get-academic-years/', AcademicYearViewSet.as_view({'get': 'list'}), name='get_academic_years'),
    path('add-academic-year/', AcademicYearViewSet.as_view({'post': 'create'}), name='add_academic_year'),
    path('view-academic-year/<int:pk>/', AcademicYearViewSet.as_view({'get': 'retrieve'}), name='view_academic_year'),
    path('edit-academic-year/<int:pk>/', AcademicYearViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='edit_academic_year'),
    path('delete-academic-year/<int:pk>/', AcademicYearViewSet.as_view({'delete': 'destroy'}), name='delete_academic_year'),

    # --- Blood Group CRUD APIs ---
    path('list-blood-groups/', BloodGroupViewSet.as_view({'get': 'list'}), name='list_blood_groups'),
    path('get-blood-groups/', BloodGroupViewSet.as_view({'get': 'list'}), name='get_blood_groups'),
    path('add-blood-group/', BloodGroupViewSet.as_view({'post': 'create'}), name='add_blood_group'),
    path('view-blood-group/<int:pk>/', BloodGroupViewSet.as_view({'get': 'retrieve'}), name='view_blood_group'),
    path('edit-blood-group/<int:pk>/', BloodGroupViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='edit_blood_group'),
    path('delete-blood-group/<int:pk>/', BloodGroupViewSet.as_view({'delete': 'destroy'}), name='delete_blood_group'),

    # --- Room / Classroom / Hall CRUD APIs ---
    path('list-rooms/', RoomViewSet.as_view({'get': 'list'}), name='list_rooms'),
    path('add-room/', RoomViewSet.as_view({'post': 'create'}), name='add_room'),
    path('view-room/<int:pk>/', RoomViewSet.as_view({'get': 'retrieve'}), name='view_room'),
    path('edit-room/<int:pk>/', RoomViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='edit_room'),
    path('delete-room/<int:pk>/', RoomViewSet.as_view({'delete': 'destroy'}), name='delete_room'),

    # Default router URLs (for standard REST conventions)
    path('', include(router.urls)),
]

