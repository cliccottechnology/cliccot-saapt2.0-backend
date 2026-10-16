import csv
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import (
    AcademicYear,
    SchoolClass,
    Section,
    ClassSection,
    ParentGuardian,
    Student,
    AcademicRecord
)
from .serializers import (
    AcademicYearSerializer,
    SchoolClassSerializer,
    SectionSerializer,
    ClassSectionSerializer,
    StudentListSerializer,
    StudentDetailSerializer,
    StudentCreateUpdateSerializer,
    BulkAllocateStudentsSerializer,
    StudentIDCardSerializer,
    AcademicRecordSerializer,
    ParentGuardianSerializer
)


class AcademicYearViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing academic years.
    """
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None


class SchoolClassViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing standards/grades (e.g., Class 6, Class 7, Class 8).
    """
    queryset = SchoolClass.objects.all()
    serializer_class = SchoolClassSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None


class SectionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing sections (e.g., A, B, C).
    """
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None


class ClassSectionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Class & Section Allocation (Page 9 & Page 10).
    Provides classes, sections, assigned teacher, room number, max strength, and current strength.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClassSectionSerializer
    pagination_class = None

    def get_queryset(self):
        qs = ClassSection.objects.select_related(
            'school_class',
            'section',
            'academic_year',
            'class_teacher'
        ).annotate(
            current_strength=Count(
                'students',
                filter=Q(students__status=Student.Status.ACTIVE)
            )
        )

        academic_year = self.request.query_params.get('academic_year')
        if academic_year:
            qs = qs.filter(academic_year__year_name=academic_year)

        class_id = self.request.query_params.get('class_id')
        if class_id:
            qs = qs.filter(school_class_id=class_id)

        return qs

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """
        List all students currently allocated to this specific class & section.
        """
        class_section = self.get_object()
        students = class_section.students.select_related('parent_guardian').all()
        serializer = StudentListSerializer(students, many=True, context={'request': request})
        return Response(serializer.data)


class StudentViewSet(viewsets.ModelViewSet):
    """
    Comprehensive Student Management ViewSet:
    - Page 4: Student List with filters (class, section, status, search), pagination, export
    - Page 5-7: Multi-step Admission (Student Details, Parent Details, Document Uploads)
    - Page 8: Student Profile View with KPI metrics and academic records
    - Page 9: Bulk Student Section Allocation
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = Student.objects.select_related(
            'class_section',
            'class_section__school_class',
            'class_section__section',
            'parent_guardian',
            'academic_year'
        ).prefetch_related('academic_records').all()

        # Search by student name or admission number
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(full_name__icontains=search) |
                Q(admission_number__icontains=search)
            )

        # Filter by Class
        class_param = self.request.query_params.get('class')
        if class_param:
            qs = qs.filter(
                Q(class_section__school_class__name__iexact=class_param) |
                Q(class_section__school_class__code__iexact=class_param) |
                Q(class_section__school_class_id=class_param if class_param.isdigit() else None)
            )

        # Filter by Section
        section_param = self.request.query_params.get('section')
        if section_param:
            qs = qs.filter(
                Q(class_section__section__name__iexact=section_param) |
                Q(class_section__section_id=section_param if section_param.isdigit() else None)
            )

        # Filter by Status (Active, Transferred, Graduated, Inactive)
        status_param = self.request.query_params.get('status')
        if status_param and status_param.lower() != 'all':
            qs = qs.filter(status__iexact=status_param)

        # Filter by Academic Year
        academic_year = self.request.query_params.get('academic_year')
        if academic_year:
            qs = qs.filter(
                Q(academic_year__year_name=academic_year) |
                Q(academic_year_id=academic_year if academic_year.isdigit() else None)
            )

        return qs.order_by('-admission_date', 'admission_number')

    def get_serializer_class(self):
        if self.action == 'list':
            return StudentListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return StudentCreateUpdateSerializer
        return StudentDetailSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Dashboard & Student Header Metrics (Page 3 & Page 4).
        Returns total students, active count, new admissions count, and status distribution.
        """
        total_students = Student.objects.count()
        active_students = Student.objects.filter(status=Student.Status.ACTIVE).count()
        transferred_students = Student.objects.filter(status=Student.Status.TRANSFERRED).count()
        graduated_students = Student.objects.filter(status=Student.Status.GRADUATED).count()
        inactive_students = Student.objects.filter(status=Student.Status.INACTIVE).count()

        # New admissions this academic month
        now = timezone.now()
        new_admissions_month = Student.objects.filter(
            admission_date__year=now.year,
            admission_date__month=now.month
        ).count()

        # Class-wise strength breakdown
        class_breakdown = ClassSection.objects.values(
            'id',
            'school_class__name',
            'section__name',
            'max_strength'
        ).annotate(
            active_count=Count('students', filter=Q(students__status=Student.Status.ACTIVE))
        ).order_by('school_class__numeric_order', 'section__name')

        return Response({
            'total_students': total_students,
            'active_students': active_students,
            'transferred_students': transferred_students,
            'graduated_students': graduated_students,
            'inactive_students': inactive_students,
            'new_admissions_this_month': new_admissions_month,
            'class_breakdown': list(class_breakdown)
        })

    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Export filtered student records as CSV (Page 4 - Export button).
        """
        students = self.get_queryset()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="students_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Admission Number',
            'Student Name',
            'Class',
            'Section',
            'Roll Number',
            'Parent Name',
            'Parent Mobile',
            'Status',
            'Gender',
            'Blood Group',
            'Admission Date',
            'Academic Year'
        ])

        for s in students:
            writer.writerow([
                s.admission_number,
                s.full_name,
                s.class_section.school_class.name if s.class_section else '',
                s.class_section.section.name if s.class_section else '',
                s.roll_number,
                s.parent_name,
                s.parent_mobile,
                s.status,
                s.gender,
                s.blood_group,
                s.admission_date.strftime('%d-%m-%Y') if s.admission_date else '',
                s.academic_year.year_name if s.academic_year else ''
            ])

        return response

    @action(detail=True, methods=['get'], url_path='id-card')
    def id_card(self, request, pk=None):
        """
        Returns structured student card information for printing ID cards (Page 8).
        """
        student = self.get_object()
        serializer = StudentIDCardSerializer(student, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='bulk-allocate')
    def bulk_allocate(self, request):
        """
        Reallocates students to a section (Page 9 - Class & Section Allocation).
        Payload: { "student_ids": [1, 2, 3], "target_class_section_id": 4 }
        """
        serializer = BulkAllocateStudentsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        student_ids = serializer.validated_data['student_ids']
        target_class_section_id = serializer.validated_data['target_class_section_id']

        try:
            target_class_section = ClassSection.objects.get(pk=target_class_section_id)
        except ClassSection.DoesNotExist:
            return Response(
                {"detail": "Target ClassSection does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check maximum capacity limit
        current_count = target_class_section.current_strength
        if current_count + len(student_ids) > target_class_section.max_strength:
            return Response(
                {
                    "detail": f"Class capacity exceeded. Capacity: {target_class_section.max_strength}, Current: {current_count}, Attempting to add: {len(student_ids)}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            updated_count = Student.objects.filter(id__in=student_ids).update(
                class_section=target_class_section
            )

        return Response({
            "message": f"Successfully moved {updated_count} students to {target_class_section.display_name}.",
            "target_class_section": ClassSectionSerializer(target_class_section).data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'post'], url_path='academic-records')
    def academic_records(self, request, pk=None):
        """
        List or record academic marks for this student (Page 8 - Academic records · Term 1).
        """
        student = self.get_object()

        if request.method == 'GET':
            records = student.academic_records.all()
            term = request.query_params.get('term')
            if term:
                records = records.filter(term__iexact=term)
            serializer = AcademicRecordSerializer(records, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = AcademicRecordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(student=student)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
