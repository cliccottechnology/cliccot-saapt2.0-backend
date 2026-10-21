from django.contrib import admin
from .models import (
    AcademicYear,
    SchoolClass,
    Section,
    BloodGroup,
    ClassSection,
    ParentGuardian,
    Student,
    AcademicRecord
)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('year_name', 'start_date', 'end_date', 'is_current', 'created_at')
    list_filter = ('is_current',)
    search_fields = ('year_name',)


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'numeric_order')
    search_fields = ('name', 'code')
    ordering = ('numeric_order',)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(BloodGroup)
class BloodGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description', 'created_at')
    search_fields = ('name', 'code')


@admin.register(ClassSection)
class ClassSectionAdmin(admin.ModelAdmin):
    list_display = (
        'display_name',
        'academic_year',
        'teacher_display_name',
        'room_number',
        'max_strength',
        'current_strength'
    )
    list_filter = ('academic_year', 'school_class', 'section')
    search_fields = ('school_class__name', 'section__name', 'room_number', 'class_teacher_name')


class AcademicRecordInline(admin.TabularInline):
    model = AcademicRecord
    extra = 1


@admin.register(ParentGuardian)
class ParentGuardianAdmin(admin.ModelAdmin):
    list_display = ('father_name', 'mother_name', 'relation', 'mobile_number', 'email')
    search_fields = ('father_name', 'mother_name', 'mobile_number', 'email')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'admission_number',
        'full_name',
        'class_display',
        'roll_number',
        'parent_name',
        'parent_mobile',
        'status',
        'admission_date'
    )
    list_filter = (
        'status',
        'academic_year',
        'class_section__school_class',
        'class_section__section',
        'gender',
        'blood_group'
    )
    search_fields = (
        'admission_number',
        'full_name',
        'parent_guardian__father_name',
        'parent_guardian__mobile_number'
    )
    inlines = [AcademicRecordInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AcademicRecord)
class AcademicRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'term', 'subject', 'marks', 'max_marks', 'grade')
    list_filter = ('term', 'grade')
    search_fields = ('student__admission_number', 'student__full_name', 'subject')
