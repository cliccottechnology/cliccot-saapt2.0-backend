import re
from django.db import models
from django.utils import timezone
from django.conf import settings


class AcademicYear(models.Model):
    """
    Academic Year representation (e.g., 2026-27).
    """
    year_name = models.CharField(max_length=20, unique=True, help_text="e.g. 2026-27")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year_name']
        verbose_name = "Academic Year"
        verbose_name_plural = "Academic Years"

    def __str__(self):
        return self.year_name


class SchoolClass(models.Model):
    """
    Represents a grade/standard (e.g., Class 6, Class 7, Class 8).
    """
    name = models.CharField(max_length=50, unique=True, help_text="e.g. Class 8")
    code = models.CharField(max_length=20, blank=True, help_text="e.g. 8 or C8")
    numeric_order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['numeric_order', 'name']
        verbose_name = "School Class"
        verbose_name_plural = "School Classes"

    def __str__(self):
        return self.name


class Section(models.Model):
    """
    Represents a class section (e.g., A, B, C).
    """
    name = models.CharField(max_length=10, unique=True, help_text="e.g. A, B, C")

    class Meta:
        ordering = ['name']
        verbose_name = "Section"
        verbose_name_plural = "Sections"

    def __str__(self):
        return self.name


class ClassSection(models.Model):
    """
    Represents an allocated Class & Section for an academic year (Page 9 & 10).
    E.g. Class 8 - Section A for 2026-27 with Room No and Class Teacher.
    """
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='class_sections'
    )
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name='class_sections'
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='class_sections'
    )
    class_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_classes'
    )
    class_teacher_name = models.CharField(
        max_length=120,
        blank=True,
        help_text="Teacher name displayed if not linked to user (e.g., Mrs. Latha)"
    )
    room_number = models.CharField(max_length=50, blank=True, help_text="e.g. Room 12")
    max_strength = models.PositiveIntegerField(default=45, help_text="Maximum allowed students")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('academic_year', 'school_class', 'section')
        ordering = ['school_class__numeric_order', 'section__name']
        verbose_name = "Class & Section Allocation"
        verbose_name_plural = "Class & Section Allocations"

    def __str__(self):
        return f"{self.school_class.name}-{self.section.name} ({self.academic_year.year_name})"

    @property
    def display_name(self):
        return f"{self.school_class.name}-{self.section.name}"

    @property
    def short_name(self):
        code = self.school_class.code or self.school_class.name.replace("Class", "").strip()
        return f"{code}-{self.section.name}"

    @property
    def current_strength(self):
        return self.students.filter(status=Student.Status.ACTIVE).count()

    @property
    def teacher_display_name(self):
        if self.class_teacher:
            return self.class_teacher.get_full_name() or self.class_teacher.username
        return self.class_teacher_name or "Not Assigned"


class ParentGuardian(models.Model):
    """
    Parent / Guardian contact and address information (Page 6 - Step 2).
    """
    class Relation(models.TextChoices):
        FATHER = 'Father', 'Father'
        MOTHER = 'Mother', 'Mother'
        GUARDIAN = 'Guardian', 'Guardian'

    father_name = models.CharField(max_length=150, help_text="Father full name")
    mother_name = models.CharField(max_length=150, blank=True, help_text="Mother full name")
    relation = models.CharField(
        max_length=20,
        choices=Relation.choices,
        default=Relation.FATHER
    )
    mobile_number = models.CharField(
        max_length=25,
        help_text="Primary parent mobile number for alerts (e.g. 98400 12345)"
    )
    alternate_mobile = models.CharField(max_length=25, blank=True)
    email = models.EmailField(blank=True, help_text="e.g. parent@email.com")
    address = models.TextField(help_text="Door no, street, area, city, pincode")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Parent / Guardian"
        verbose_name_plural = "Parents / Guardians"

    def __str__(self):
        return f"{self.father_name} ({self.mobile_number})"


def student_photo_upload_path(instance, filename):
    adm = instance.admission_number or 'temp'
    return f"students/photos/{adm}_{filename}"


def student_document_upload_path(instance, filename):
    adm = instance.admission_number or 'temp'
    return f"students/documents/{adm}_{filename}"


class Student(models.Model):
    """
    Core Student Model capturing Admission Steps 1-3, List View, and Profile details.
    """
    class Gender(models.TextChoices):
        MALE = 'Male', 'Male'
        FEMALE = 'Female', 'Female'
        OTHER = 'Other', 'Other'

    class BloodGroup(models.TextChoices):
        A_POS = 'A+', 'A+'
        A_NEG = 'A-', 'A-'
        B_POS = 'B+', 'B+'
        B_NEG = 'B-', 'B-'
        O_POS = 'O+', 'O+'
        O_NEG = 'O-', 'O-'
        AB_POS = 'AB+', 'AB+'
        AB_NEG = 'AB-', 'AB-'
        UNKNOWN = 'Unknown', 'Unknown'

    class Status(models.TextChoices):
        ACTIVE = 'Active', 'Active'
        TRANSFERRED = 'Transferred', 'Transferred'
        GRADUATED = 'Graduated', 'Graduated'
        INACTIVE = 'Inactive', 'Inactive'

    # Step 1: Student Details
    admission_number = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        help_text="Automatic admission number (e.g. A-1021)"
    )
    full_name = models.CharField(max_length=200, help_text="Student full name")
    date_of_birth = models.DateField(help_text="dd-mm-yyyy")
    gender = models.CharField(
        max_length=15,
        choices=Gender.choices,
        default=Gender.MALE
    )
    blood_group = models.CharField(
        max_length=10,
        choices=BloodGroup.choices,
        default=BloodGroup.UNKNOWN,
        blank=True
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name='students'
    )
    class_section = models.ForeignKey(
        ClassSection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )
    roll_number = models.CharField(max_length=20, blank=True, help_text="e.g. Roll 14")
    admission_date = models.DateField(default=timezone.localdate)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True
    )

    # Step 2: Parent / Guardian Details
    parent_guardian = models.OneToOneField(
        ParentGuardian,
        on_delete=models.CASCADE,
        related_name='student',
        null=True,
        blank=True
    )

    # Step 3: Documents (Page 7)
    student_photo = models.FileField(
        upload_to=student_photo_upload_path,
        blank=True,
        null=True,
        help_text="JPG / PNG student photo"
    )
    birth_certificate = models.FileField(
        upload_to=student_document_upload_path,
        blank=True,
        null=True,
        help_text="Birth certificate (PDF / JPG)"
    )
    transfer_certificate = models.FileField(
        upload_to=student_document_upload_path,
        blank=True,
        null=True,
        help_text="Transfer certificate (PDF / JPG)"
    )
    aadhaar_card = models.FileField(
        upload_to=student_document_upload_path,
        blank=True,
        null=True,
        help_text="Aadhaar document (optional)"
    )

    # Profile & Integrated Info (Page 8)
    bus_route_info = models.CharField(
        max_length=150,
        blank=True,
        help_text="Bus route/number e.g. Bus: TN-09-AB-1234"
    )
    overall_grade = models.CharField(
        max_length=10,
        default='A+',
        blank=True,
        help_text="Current overall grade (e.g., A+)"
    )
    attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=96.00,
        help_text="Attendance KPI % (e.g., 96.00)"
    )
    fees_pending_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Current pending fees (e.g. 24000.00)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['admission_number']
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return f"{self.admission_number} - {self.full_name}"

    @classmethod
    def generate_admission_number(cls, prefix="A-"):
        """
        Auto-generates sequential admission number (e.g., A-1021, A-1022).
        Finds the highest existing numeric suffix and increments by 1.
        """
        existing = cls.objects.filter(admission_number__startswith=prefix).values_list('admission_number', flat=True)
        max_num = 1020  # Default base so next is A-1021 as shown in mockups
        for adm in existing:
            match = re.search(r'(\d+)$', adm)
            if match:
                val = int(match.group(1))
                if val > max_num:
                    max_num = val
        return f"{prefix}{max_num + 1}"

    def save(self, *args, **kwargs):
        if not self.admission_number:
            self.admission_number = self.generate_admission_number()
        super().save(*args, **kwargs)

    @property
    def class_display(self):
        if self.class_section:
            return self.class_section.short_name
        return "Unallocated"

    @property
    def parent_name(self):
        if self.parent_guardian:
            return self.parent_guardian.father_name or self.parent_guardian.mother_name
        return ""

    @property
    def parent_mobile(self):
        if self.parent_guardian:
            return self.parent_guardian.mobile_number
        return ""


class AcademicRecord(models.Model):
    """
    Academic mark records for student profile (Page 8 - Academic records · Term 1).
    Subject, Marks, Max Marks, Grade (e.g., Tamil: 88/100 -> A).
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='academic_records'
    )
    term = models.CharField(max_length=50, default='Term 1', help_text="e.g. Term 1, Term 2")
    subject = models.CharField(max_length=100, help_text="e.g. Tamil, English, Mathematics")
    marks = models.DecimalField(max_digits=5, decimal_places=2, help_text="Marks scored")
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    grade = models.CharField(max_length=10, blank=True, help_text="e.g. A, A+, B")
    remarks = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['term', 'subject']
        verbose_name = "Academic Record"
        verbose_name_plural = "Academic Records"

    def __str__(self):
        return f"{self.student.admission_number} - {self.subject} ({self.term}): {self.marks}/{self.max_marks}"

    def calculate_grade(self):
        if self.max_marks > 0:
            pct = (float(self.marks) / float(self.max_marks)) * 100
            if pct >= 90:
                return 'A+'
            elif pct >= 80:
                return 'A'
            elif pct >= 70:
                return 'B+'
            elif pct >= 60:
                return 'B'
            elif pct >= 50:
                return 'C'
            elif pct >= 35:
                return 'D'
            else:
                return 'F'
        return 'N/A'

    def save(self, *args, **kwargs):
        if not self.grade:
            self.grade = self.calculate_grade()
        super().save(*args, **kwargs)
