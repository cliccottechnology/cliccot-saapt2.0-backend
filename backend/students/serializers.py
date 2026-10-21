from django.db import models
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


class AcademicYearRelatedField(serializers.Field):
    """
    Accepts AcademicYear ID (int/str), year_name (str e.g. '2026-27'), or AcademicYear instance.
    """
    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError("This field is required.")
        if isinstance(data, AcademicYear):
            return data
        if isinstance(data, int) or (isinstance(data, str) and data.isdigit()):
            try:
                return AcademicYear.objects.get(pk=int(data))
            except AcademicYear.DoesNotExist:
                raise serializers.ValidationError(f"AcademicYear with id={data} does not exist.")
        elif isinstance(data, str):
            val = data.strip()
            ay = AcademicYear.objects.filter(year_name__iexact=val).first()
            if not ay:
                ay = AcademicYear.objects.create(year_name=val, is_current=True)
            return ay
        raise serializers.ValidationError("Invalid academic_year. Expected integer ID or year string (e.g. '2026-27').")

    def to_representation(self, value):
        return value.id if hasattr(value, 'id') else value


class SectionRelatedField(serializers.Field):
    """
    Accepts Section ID (int/str), section name (str e.g. 'A', 'B'), or Section instance.
    """
    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError("This field is required.")
        if isinstance(data, Section):
            return data
        if isinstance(data, int) or (isinstance(data, str) and data.isdigit()):
            try:
                return Section.objects.get(pk=int(data))
            except Section.DoesNotExist:
                raise serializers.ValidationError(f"Section with id={data} does not exist.")
        elif isinstance(data, str):
            val = data.strip().upper()
            sec, _ = Section.objects.get_or_create(name=val)
            return sec
        raise serializers.ValidationError("Invalid section. Expected integer ID or section name (e.g. 'A').")

    def to_representation(self, value):
        return value.id if hasattr(value, 'id') else value


class SchoolClassRelatedField(serializers.Field):
    """
    Accepts SchoolClass ID (int/str), class name (e.g. 'Class 8', '8'), or SchoolClass instance.
    """
    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError("This field is required.")
        if isinstance(data, SchoolClass):
            return data
        if isinstance(data, int) or (isinstance(data, str) and data.isdigit()):
            try:
                return SchoolClass.objects.get(pk=int(data))
            except SchoolClass.DoesNotExist:
                pass
        if isinstance(data, str):
            val = data.strip()
            sc = SchoolClass.objects.filter(
                models.Q(name__iexact=val) |
                models.Q(code__iexact=val) |
                models.Q(name__iexact=f"Class {val}")
            ).first()
            if sc:
                return sc
            sc, _ = SchoolClass.objects.get_or_create(name=val)
            return sc
        raise serializers.ValidationError("Invalid school class. Expected integer ID or class name (e.g. 'Class 8').")

    def to_representation(self, value):
        return value.id if hasattr(value, 'id') else value


class ClassSectionRelatedField(serializers.Field):
    """
    Accepts ClassSection ID (int/str), or display string (e.g. 'Class 8-A' or '8-A'),
    or ClassSection instance.
    """
    def to_internal_value(self, data):
        if not data:
            return None
        if isinstance(data, ClassSection):
            return data
        if isinstance(data, int) or (isinstance(data, str) and data.isdigit()):
            try:
                return ClassSection.objects.get(pk=int(data))
            except ClassSection.DoesNotExist:
                raise serializers.ValidationError(f"ClassSection with id={data} does not exist.")
        elif isinstance(data, str):
            val = data.strip()
            if '-' in val:
                parts = val.split('-', 1)
                c_part, s_part = parts[0].strip(), parts[1].strip()
                cs = ClassSection.objects.filter(
                    (models.Q(school_class__name__iexact=c_part) |
                     models.Q(school_class__code__iexact=c_part) |
                     models.Q(school_class__name__iexact=f"Class {c_part}")) &
                    models.Q(section__name__iexact=s_part)
                ).first()
                if cs:
                    return cs
            else:
                cs = ClassSection.objects.filter(section__name__iexact=val).first()
                if cs:
                    return cs
            raise serializers.ValidationError(
                f"ClassSection '{val}' not found. Please provide valid ClassSection ID or format like 'Class 8-A'."
            )
        raise serializers.ValidationError("Invalid class_section. Expected integer ID or name (e.g. 'Class 8-A').")

    def to_representation(self, value):
        return value.id if hasattr(value, 'id') else value


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
    Supports academic_year, school_class, and section as IDs or Strings.
    """
    academic_year = AcademicYearRelatedField()
    school_class = SchoolClassRelatedField()
    section = SectionRelatedField()

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
    class_name = serializers.CharField(read_only=True)
    section_name = serializers.CharField(read_only=True)
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
            'class_name',
            'section_name',
            'roll_number',
            'parent_name',
            'parent_mobile',
            'status',
            'student_photo',
            'admission_date'
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['class'] = instance.class_name
        ret['section'] = instance.section_name
        return ret


class StudentDetailSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for Student Profile Page (Page 8).
    Includes personal details, parent guardian, academic records, and summary KPIs.
    """
    parent_guardian = ParentGuardianSerializer(read_only=True)
    academic_records = AcademicRecordSerializer(many=True, read_only=True)
    class_section_details = ClassSectionSerializer(source='class_section', read_only=True)
    class_display = serializers.CharField(read_only=True)
    class_name = serializers.CharField(read_only=True)
    section_name = serializers.CharField(read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.year_name', read_only=True)
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
            'academic_year_name',
            'class_section',
            'class_section_details',
            'class_display',
            'class_name',
            'section_name',
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

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['class'] = instance.class_name
        ret['section'] = instance.section_name
        return ret


class StudentCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for New Admission dialog (Step 1, Step 2, Step 3) and Profile Editing.
    Supports atomic creation of ParentGuardian record and file attachments.
    Accepts academic_year as string ('2026-27') or integer ID.
    Accepts class as string ('Class 8' or '8') and section as string ('A').
    """
    academic_year = AcademicYearRelatedField(required=True)
    class_section = ClassSectionRelatedField(required=False, allow_null=True)

    # Optional string helper inputs directly from form:
    section = serializers.CharField(write_only=True, required=False, allow_blank=True)
    school_class = serializers.CharField(write_only=True, required=False, allow_blank=True)
    class_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

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
            'section',
            'school_class',
            'class_name',
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

    def to_internal_value(self, data):
        # Allow passing 'class' directly as key in form/JSON
        if hasattr(data, 'copy'):
            data = data.copy()
        else:
            data = dict(data)
        if 'class' in data and not data.get('school_class'):
            data['school_class'] = data.get('class')
        return super().to_internal_value(data)

    def _resolve_class_section(self, validated_data, instance=None):
        section_str = validated_data.pop('section', '').strip()
        class_str = (validated_data.pop('school_class', '') or validated_data.pop('class_name', '')).strip()

        # If class_section is explicitly provided, it takes precedence
        if validated_data.get('class_section'):
            return

        ay = validated_data.get('academic_year') or (instance.academic_year if instance else None)

        if section_str or class_str:
            sec_obj = None
            if section_str:
                sec_obj, _ = Section.objects.get_or_create(name=section_str.upper())

            cls_obj = None
            if class_str:
                cls_obj = SchoolClass.objects.filter(
                    models.Q(name__iexact=class_str) |
                    models.Q(code__iexact=class_str) |
                    models.Q(name__iexact=f"Class {class_str}")
                ).first()
                if not cls_obj:
                    cls_obj, _ = SchoolClass.objects.get_or_create(
                        name=f"Class {class_str}" if class_str.isdigit() else class_str
                    )

            if cls_obj and sec_obj and ay:
                cs_obj, _ = ClassSection.objects.get_or_create(
                    academic_year=ay,
                    school_class=cls_obj,
                    section=sec_obj
                )
                validated_data['class_section'] = cs_obj
            elif sec_obj and ay:
                cs_obj = ClassSection.objects.filter(academic_year=ay, section=sec_obj).first()
                if cs_obj:
                    validated_data['class_section'] = cs_obj

    def create(self, validated_data):
        self._resolve_class_section(validated_data)

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
        self._resolve_class_section(validated_data, instance=instance)

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

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['class'] = instance.class_name
        ret['section'] = instance.section_name
        ret['academic_year_name'] = instance.academic_year_name
        ret['section_name'] = instance.section_name
        ret['class_name'] = instance.class_name
        ret['class_display'] = instance.class_display
        return ret


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
