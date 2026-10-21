from datetime import date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from students.models import (
    AcademicYear,
    SchoolClass,
    Section,
    ClassSection,
    ParentGuardian,
    Student,
    AcademicRecord
)

User = get_user_model()


class StudentModuleTests(APITestCase):
    def setUp(self):
        # Create user and authenticate
        self.user = User.objects.create_user(
            username='admin_test',
            email='admin@school.com',
            password='testpassword123'
        )
        self.client.force_authenticate(user=self.user)

        # Setup Academic Year
        self.academic_year = AcademicYear.objects.create(
            year_name="2026-27",
            start_date=date(2026, 6, 1),
            end_date=date(2027, 4, 30),
            is_current=True
        )

        # Setup Class and Section
        self.school_class_8 = SchoolClass.objects.create(name="Class 8", code="8", numeric_order=8)
        self.school_class_9 = SchoolClass.objects.create(name="Class 9", code="9", numeric_order=9)
        self.section_a = Section.objects.create(name="A")
        self.section_b = Section.objects.create(name="B")

        # Class Section allocations
        self.cs_8a = ClassSection.objects.create(
            academic_year=self.academic_year,
            school_class=self.school_class_8,
            section=self.section_a,
            class_teacher_name="Mrs. Latha",
            room_number="Room 12",
            max_strength=45
        )

        self.cs_8b = ClassSection.objects.create(
            academic_year=self.academic_year,
            school_class=self.school_class_8,
            section=self.section_b,
            class_teacher_name="Mr. Kumar",
            room_number="Room 8B",
            max_strength=45
        )

        # Create a parent and student
        self.parent = ParentGuardian.objects.create(
            father_name="Ramesh Kumar",
            mother_name="Geetha R",
            relation="Father",
            mobile_number="98400 12345",
            email="ramesh@email.com",
            address="12, Temple St, Tambaram, Chennai"
        )

        self.student = Student.objects.create(
            admission_number="A-1021",
            full_name="Ananya R",
            date_of_birth=date(2014, 5, 12),
            gender="Female",
            blood_group="O+",
            academic_year=self.academic_year,
            class_section=self.cs_8a,
            roll_number="Roll 14",
            parent_guardian=self.parent,
            status=Student.Status.ACTIVE,
            bus_route_info="Bus: TN-09-AB-1234",
            overall_grade="A+",
            attendance_percentage=96.00,
            fees_pending_amount=24000.00
        )

        AcademicRecord.objects.create(
            student=self.student,
            term="Term 1",
            subject="Mathematics",
            marks=95.00,
            max_marks=100.00,
            grade="A+"
        )

    def test_student_list_and_search(self):
        """Test listing students and filtering by search and status"""
        url = reverse('student-list')
        response = self.client.get(url, {'search': 'Ananya'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check pagination format or result items
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['admission_number'], 'A-1021')

    def test_student_filter_by_class_and_status(self):
        """Test filtering students by class and status"""
        url = reverse('student-list')
        response = self.client.get(url, {'class': '8', 'status': 'Active'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)

    def test_new_admission_auto_admission_number(self):
        """Test creating a new student via the 3-step admission API with auto-generated admission number"""
        url = reverse('student-list')
        payload = {
            "full_name": "Siddharth N",
            "date_of_birth": "2014-06-15",
            "gender": "Male",
            "blood_group": "B+",
            "academic_year": self.academic_year.id,
            "class_section": self.cs_8a.id,
            "father_name": "Natarajan S",
            "mobile_number": "98400 54321",
            "address": "42, Gandhi Road, Chennai"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('admission_number', response.data)
        self.assertTrue(response.data['admission_number'].startswith('A-'))

        # Verify created in DB
        new_student = Student.objects.get(full_name="Siddharth N")
        self.assertIsNotNone(new_student.parent_guardian)
        self.assertEqual(new_student.parent_guardian.father_name, "Natarajan S")

    def test_student_detail_profile(self):
        """Test retrieving full student profile with academic records and parent details"""
        url = reverse('student-detail', kwargs={'pk': self.student.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Ananya R')
        self.assertEqual(response.data['parent_name'], 'Ramesh Kumar')
        self.assertEqual(len(response.data['academic_records']), 1)
        self.assertEqual(response.data['academic_records'][0]['subject'], 'Mathematics')

    def test_student_id_card(self):
        """Test printable ID card data endpoint"""
        url = reverse('student-id-card', kwargs={'pk': self.student.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['school_name'], "Smart Campus School")
        self.assertEqual(response.data['admission_number'], "A-1021")

    def test_bulk_allocate_students(self):
        """Test allocating students to a section (Page 9)"""
        url = reverse('student-bulk-allocate')
        payload = {
            "student_ids": [self.student.id],
            "target_class_section_id": self.cs_8b.id
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertEqual(self.student.class_section, self.cs_8b)

    def test_export_students_csv(self):
        """Test CSV export endpoint"""
        url = reverse('student-export')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('A-1021', response.content.decode('utf-8'))
        self.assertIn('Ananya R', response.content.decode('utf-8'))

    def test_student_stats(self):
        """Test student dashboard statistics endpoint"""
        url = reverse('student-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_students', response.data)
        self.assertIn('active_students', response.data)
        self.assertIn('class_breakdown', response.data)

    def test_new_admission_with_string_academic_year_and_section(self):
        """Test creating a new student submitting academic_year and section as strings"""
        url = reverse('student-list')
        payload = {
            "full_name": "Kavya S",
            "date_of_birth": "2013-08-20",
            "gender": "Female",
            "blood_group": "A+",
            "academic_year": "2026-27",
            "school_class": "Class 8",
            "section": "A",
            "roll_number": "Roll 15",
            "father_name": "Suresh S",
            "mobile_number": "98400 99999",
            "address": "15, Anna Nagar, Chennai"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['full_name'], "Kavya S")
        self.assertEqual(response.data['academic_year_name'], "2026-27")
        self.assertEqual(response.data['section_name'], "A")
        self.assertEqual(response.data['class_name'], "Class 8")

        # Verify DB entry
        student = Student.objects.get(full_name="Kavya S")
        self.assertEqual(student.academic_year.year_name, "2026-27")
        self.assertEqual(student.class_section.section.name, "A")
        self.assertEqual(student.class_section.school_class.name, "Class 8")

    def test_new_admission_with_string_class_section(self):
        """Test creating student passing class_section as combined string (e.g., 'Class 8-A')"""
        url = reverse('student-list')
        payload = {
            "full_name": "Pooja V",
            "date_of_birth": "2014-01-10",
            "gender": "Female",
            "academic_year": "2026-27",
            "class_section": "Class 8-A",
            "father_name": "Vijay",
            "mobile_number": "98400 88888"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        student = Student.objects.get(full_name="Pooja V")
        self.assertEqual(student.class_section, self.cs_8a)
        self.assertEqual(student.section_name, "A")

    def test_create_class_section_with_strings(self):
        """Test creating class section using string names for academic_year, school_class, section"""
        url = reverse('class-section-list')
        payload = {
            "academic_year": "2026-27",
            "school_class": "Class 9",
            "section": "C",
            "room_number": "Room 9C",
            "max_strength": 40
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['section_name'], "C")
        self.assertEqual(response.data['academic_year_name'], "2026-27")
        self.assertEqual(response.data['class_name'], "Class 9")
