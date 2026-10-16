from rest_framework import serializers
from .models import (
    AcademicYear,
    SchoolClass,
    Section,
    ClassSection,
    ParentGuardian,
    Student,
    AcademicRecord
)


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ['id', 'year_name', 'start_date', 'end_date', 'is_current']


class SchoolClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolClass
        fields = ['id', 'name', 'code', 'numeric_order']


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'name']


class ClassSectionSerializer(serializers.ModelSerializer):
    """
    Serializer for Class & Section Allocation (Page 9 & 10).
    Includes calculated current strength, maximum strength, and display labels.
    """
    class_name = serializers.CharField(source='school_class.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.year_name', read_only=True)
    current_strength = serializers.IntegerField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    short_name = serializers.CharField(read_only=True)
    class_teacher_display = serializers.CharField(source='teacher_display_name', read_only=True)

    class Meta:
        model = ClassSection
        fields = [
            'id',
            'academic_year',
            'academic_year_name',
            'school_class',
            'class_name',
            'section',
            'section_name',
            'class_teacher',
            'class_teacher_name',
            'class_teacher_display',
            'room_number',
            'max_strength',
            'current_strength',
            'display_name',
            'short_name',
            'created_at',
            'updated_at'
        ]


class ParentGuardianSerializer(serializers.ModelSerializer):
    """
    Serializer for Parent / Guardian information (Step 2).
    """
    class Meta:
        model = ParentGuardian
        fields = [
            'id',
            'father_name',
            'mother_name',
            'relation',
            'mobile_number',
            'alternate_mobile',
            'email',
            'address',
            'created_at',
            'updated_at'
        ]


class AcademicRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for marks and grade records (Page 8 - Academic Tab).
    """
    class Meta:
        model = AcademicRecord
        fields = [
            'id',
            'term',
            'subject',
            'marks',
            'max_marks',
            'grade',
            'remarks',
            'created_at'
        ]
        read_only_fields = ['grade', 'created_at']


class StudentListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for Student List Table (Page 4).
    Columns: ADM NO, STUDENT, CLASS, PARENT, MOBILE, STATUS, ACTION.
    """
    class_display = serializers.CharField(read_only=True)
    parent_name = serializers.CharField(read_only=True)
    parent_mobile = serializers.CharField(read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.year_name', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id',
            'admission_number',
            'full_name',
            'date_of_birth',
            'gender',
            'blood_group',
            'academic_year',
            'academic_year_name',
            'class_section',
            'class_display',
            'roll_number',
            'parent_name',
            'parent_mobile',
            'status',
            'student_photo',
            'admission_date'
        ]


class StudentDetailSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for Student Profile Page (Page 8).
    Includes personal details, parent guardian, academic records, and summary KPIs.
    """
    parent_guardian = ParentGuardianSerializer(read_only=True)
    academic_records = AcademicRecordSerializer(many=True, read_only=True)
    class_section_details = ClassSectionSerializer(source='class_section', read_only=True)
    class_display = serializers.CharField(read_only=True)
    parent_name = serializers.CharField(read_only=True)
    parent_mobile = serializers.CharField(read_only=True)

    class Meta:
        model = Student
        fields = [
            'id',
            'admission_number',
            'full_name',
            'date_of_birth',
            'gender',
            'blood_group',
            'admission_date',
            'academic_year',
            'class_section',
            'class_section_details',
            'class_display',
            'roll_number',
            'status',
            'bus_route_info',
            'overall_grade',
            'attendance_percentage',
            'fees_pending_amount',
            'student_photo',
            'birth_certificate',
            'transfer_certificate',
            'aadhaar_card',
            'parent_name',
            'parent_mobile',
            'parent_guardian',
            'academic_records',
            'created_at',
            'updated_at'
        ]


class StudentCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for New Admission dialog (Step 1, Step 2, Step 3) and Profile Editing.
    Supports atomic creation of ParentGuardian record and file attachments.
    """
    # Parent details directly in payload for seamless Step 1-3 form submission
    father_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    mother_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    relation = serializers.CharField(write_only=True, required=False, default='Father')
    mobile_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    alternate_mobile = serializers.CharField(write_only=True, required=False, allow_blank=True)
    parent_email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    address = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Student
        fields = [
            'id',
            'admission_number',
            'full_name',
            'date_of_birth',
            'gender',
            'blood_group',
            'admission_date',
            'academic_year',
            'class_section',
            'roll_number',
            'status',
            'bus_route_info',
            'student_photo',
            'birth_certificate',
            'transfer_certificate',
            'aadhaar_card',
            # Parent write-only fields:
            'father_name',
            'mother_name',
            'relation',
            'mobile_number',
            'alternate_mobile',
            'parent_email',
            'address'
        ]
        extra_kwargs = {
            'admission_number': {'required': False},
            'full_name': {'required': True},
            'date_of_birth': {'required': True},
            'academic_year': {'required': True},
        }

    def create(self, validated_data):
        parent_fields = {
            'father_name': validated_data.pop('father_name', ''),
            'mother_name': validated_data.pop('mother_name', ''),
            'relation': validated_data.pop('relation', 'Father'),
            'mobile_number': validated_data.pop('mobile_number', ''),
            'alternate_mobile': validated_data.pop('alternate_mobile', ''),
            'email': validated_data.pop('parent_email', ''),
            'address': validated_data.pop('address', '')
        }

        # Create parent guardian if info is provided
        parent = None
        if parent_fields['father_name'] or parent_fields['mobile_number']:
            parent = ParentGuardian.objects.create(**parent_fields)

        student = Student.objects.create(parent_guardian=parent, **validated_data)
        return student

    def update(self, instance, validated_data):
        parent_fields = {}
        for key in ['father_name', 'mother_name', 'relation', 'mobile_number', 'alternate_mobile', 'address']:
            if key in validated_data:
                parent_fields[key] = validated_data.pop(key)
        if 'parent_email' in validated_data:
            parent_fields['email'] = validated_data.pop('parent_email')

        # Update parent guardian if exists, or create if provided
        if parent_fields:
            if instance.parent_guardian:
                for attr, val in parent_fields.items():
                    setattr(instance.parent_guardian, attr, val)
                instance.parent_guardian.save()
            else:
                if parent_fields.get('father_name') or parent_fields.get('mobile_number'):
                    parent = ParentGuardian.objects.create(**parent_fields)
                    instance.parent_guardian = parent

        return super().update(instance, validated_data)


class BulkAllocateStudentsSerializer(serializers.Serializer):
    """
    Serializer for Move Selected Students (Page 9 - Class & Section Allocation).
    """
    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="List of student IDs to reallocate"
    )
    target_class_section_id = serializers.IntegerField(
        help_text="Target ClassSection ID to assign students into"
    )


class StudentIDCardSerializer(serializers.ModelSerializer):
    """
    Serializer to generate printable ID Card data (Page 8 - Print ID Card).
    """
    school_name = serializers.SerializerMethodField()
    class_and_section = serializers.CharField(source='class_display', read_only=True)
    parent_contact = serializers.CharField(source='parent_mobile', read_only=True)
    academic_year = serializers.CharField(source='academic_year.year_name', read_only=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'admission_number',
            'full_name',
            'school_name',
            'class_and_section',
            'roll_number',
            'date_of_birth',
            'blood_group',
            'parent_contact',
            'bus_route_info',
            'academic_year',
            'status',
            'photo_url'
        ]

    def get_school_name(self, obj):
        return "Smart Campus School"

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.student_photo and hasattr(obj.student_photo, 'url'):
            if request:
                return request.build_absolute_uri(obj.student_photo.url)
            return obj.student_photo.url
        return None
