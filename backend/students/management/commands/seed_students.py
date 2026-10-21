from datetime import date
from django.core.management.base import BaseCommand
from django.db import transaction
from students.models import (
    AcademicYear,
    SchoolClass,
    Section,
    BloodGroup,
    ClassSection,
    ParentGuardian,
    Student,
    AcademicRecord
)


class Command(BaseCommand):
    help = "Seeds initial student module data matching Smart Campus ERP UI specifications"

    def handle(self, *args, **options):
        self.stdout.write("Seeding Student Module data...")

        with transaction.atomic():
            # 1. Academic Year
            ay, _ = AcademicYear.objects.get_or_create(
                year_name="2026-27",
                defaults={
                    "start_date": date(2026, 6, 1),
                    "end_date": date(2027, 4, 30),
                    "is_current": True
                }
            )

            # 2. Classes
            classes_data = [
                ("Class 6", "6", 6),
                ("Class 7", "7", 7),
                ("Class 8", "8", 8),
                ("Class 9", "9", 9),
                ("Class 10", "10", 10),
                ("Class 12", "12", 12),
            ]
            class_map = {}
            for name, code, order in classes_data:
                sc, _ = SchoolClass.objects.get_or_create(
                    name=name,
                    defaults={"code": code, "numeric_order": order}
                )
                class_map[name] = sc

            # 3. Sections
            sec_map = {}
            for sname in ["A", "B", "C"]:
                sec, _ = Section.objects.get_or_create(name=sname)
                sec_map[sname] = sec

            # 3b. Blood Groups
            for bg_name in ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-', 'Unknown']:
                BloodGroup.objects.get_or_create(name=bg_name)

            # 4. Class & Section Allocations (Page 9)
            allocations = [
                ("Class 6", "A", "Mrs. Revathi", "Room 6A", 45),
                ("Class 6", "B", "Mr. Arun", "Room 6B", 45),
                ("Class 7", "A", "Mrs. Divya", "Room 7A", 45),
                ("Class 8", "A", "Mrs. Latha", "Room 12", 45),
                ("Class 8", "B", "Mr. Kumar", "Room 8B", 45),
                ("Class 9", "A", "Mrs. Meena", "Room 9A", 45),
                ("Class 9", "B", "Mrs. Malini", "Room 9B", 45),
                ("Class 10", "A", "Mr. Sundar", "Room 10A", 45),
                ("Class 12", "C", "Mr. Joseph", "Room 12C", 45),
            ]
            cs_map = {}
            for cname, sname, teacher, room, max_st in allocations:
                cs, _ = ClassSection.objects.get_or_create(
                    academic_year=ay,
                    school_class=class_map[cname],
                    section=sec_map[sname],
                    defaults={
                        "class_teacher_name": teacher,
                        "room_number": room,
                        "max_strength": max_st
                    }
                )
                cs_map[f"{cname}-{sname}"] = cs

            # 5. Students from Page 4
            students_spec = [
                {
                    "adm": "A-1021",
                    "name": "Ananya R",
                    "dob": date(2014, 5, 12),
                    "gender": Student.Gender.FEMALE,
                    "blood_group": Student.BloodGroup.O_POS,
                    "class_key": "Class 8-A",
                    "roll": "Roll 14",
                    "father": "Ramesh Kumar",
                    "mother": "Geetha R",
                    "mobile": "98400 12345",
                    "alt_mobile": "98400 99999",
                    "email": "ramesh@email.com",
                    "address": "12, Temple St, Tambaram, Chennai - 600045",
                    "status": Student.Status.ACTIVE,
                    "bus": "Bus: TN-09-AB-1234",
                    "grade": "A+",
                    "attendance": 96.00,
                    "fees_pending": 24000.00
                },
                {
                    "adm": "A-1022",
                    "name": "Karthik S",
                    "dob": date(2014, 8, 20),
                    "gender": Student.Gender.MALE,
                    "blood_group": Student.BloodGroup.B_POS,
                    "class_key": "Class 8-A",
                    "roll": "Roll 15",
                    "father": "Suresh S",
                    "mother": "Priya S",
                    "mobile": "98410 22334",
                    "email": "suresh@email.com",
                    "address": "45, North St, Medavakkam, Chennai - 600100",
                    "status": Student.Status.ACTIVE,
                    "bus": "Bus: TN-09-AB-1234",
                    "grade": "A",
                    "attendance": 94.50,
                    "fees_pending": 0.00
                },
                {
                    "adm": "A-0987",
                    "name": "Divya M",
                    "dob": date(2013, 2, 14),
                    "gender": Student.Gender.FEMALE,
                    "blood_group": Student.BloodGroup.A_POS,
                    "class_key": "Class 9-B",
                    "roll": "Roll 08",
                    "father": "Mala Murugan",
                    "mother": "Kavitha M",
                    "mobile": "97900 11223",
                    "email": "murugan@email.com",
                    "address": "18, 2nd Main Rd, Chromepet, Chennai",
                    "status": Student.Status.TRANSFERRED,
                    "bus": "Bus: TN-09-CD-5678",
                    "grade": "B+",
                    "attendance": 88.00,
                    "fees_pending": 3000.00
                },
                {
                    "adm": "A-0875",
                    "name": "Rahul V",
                    "dob": date(2012, 11, 5),
                    "gender": Student.Gender.MALE,
                    "blood_group": Student.BloodGroup.AB_POS,
                    "class_key": "Class 10-A",
                    "roll": "Roll 22",
                    "father": "Venkat P",
                    "mother": "Anitha V",
                    "mobile": "99401 55667",
                    "email": "venkat@email.com",
                    "address": "77, Gandhi Rd, Guindy, Chennai",
                    "status": Student.Status.ACTIVE,
                    "bus": "Bus: TN-09-EF-9012",
                    "grade": "A+",
                    "attendance": 98.00,
                    "fees_pending": 20000.00
                },
                {
                    "adm": "A-0612",
                    "name": "Priya K",
                    "dob": date(2010, 7, 19),
                    "gender": Student.Gender.FEMALE,
                    "blood_group": Student.BloodGroup.O_POS,
                    "class_key": "Class 12-C",
                    "roll": "Roll 05",
                    "father": "Kumar D",
                    "mother": "Vani K",
                    "mobile": "98945 33221",
                    "email": "kumar@email.com",
                    "address": "104, Lake View Rd, Velachery, Chennai",
                    "status": Student.Status.GRADUATED,
                    "bus": "",
                    "grade": "A+",
                    "attendance": 95.00,
                    "fees_pending": 0.00
                },
                {
                    "adm": "A-1033",
                    "name": "Arun T",
                    "dob": date(2015, 3, 25),
                    "gender": Student.Gender.MALE,
                    "blood_group": Student.BloodGroup.B_NEG,
                    "class_key": "Class 6-B",
                    "roll": "Roll 12",
                    "father": "Thomas J",
                    "mother": "Mary T",
                    "mobile": "90030 44556",
                    "email": "thomas@email.com",
                    "address": "22, Church St, Pallavaram, Chennai",
                    "status": Student.Status.INACTIVE,
                    "bus": "Bus: TN-09-IJ-7788",
                    "grade": "B",
                    "attendance": 72.00,
                    "fees_pending": 16000.00
                },
                {
                    "adm": "A-1040",
                    "name": "Meena S",
                    "dob": date(2014, 9, 30),
                    "gender": Student.Gender.FEMALE,
                    "blood_group": Student.BloodGroup.A_NEG,
                    "class_key": "Class 7-A",
                    "roll": "Roll 18",
                    "father": "Sekar R",
                    "mother": "Lakshmi S",
                    "mobile": "98840 77889",
                    "email": "sekar@email.com",
                    "address": "8, Station Rd, Tambaram, Chennai",
                    "status": Student.Status.ACTIVE,
                    "bus": "Bus: TN-09-AB-1234",
                    "grade": "A",
                    "attendance": 97.20,
                    "fees_pending": 18000.00
                }
            ]

            for s_data in students_spec:
                parent, _ = ParentGuardian.objects.get_or_create(
                    mobile_number=s_data["mobile"],
                    defaults={
                        "father_name": s_data["father"],
                        "mother_name": s_data.get("mother", ""),
                        "relation": ParentGuardian.Relation.FATHER,
                        "alternate_mobile": s_data.get("alt_mobile", ""),
                        "email": s_data.get("email", ""),
                        "address": s_data["address"]
                    }
                )

                st, created = Student.objects.update_or_create(
                    admission_number=s_data["adm"],
                    defaults={
                        "full_name": s_data["name"],
                        "date_of_birth": s_data["dob"],
                        "gender": s_data["gender"],
                        "blood_group": s_data["blood_group"],
                        "academic_year": ay,
                        "class_section": cs_map.get(s_data["class_key"]),
                        "roll_number": s_data["roll"],
                        "parent_guardian": parent,
                        "status": s_data["status"],
                        "bus_route_info": s_data["bus"],
                        "overall_grade": s_data["grade"],
                        "attendance_percentage": s_data["attendance"],
                        "fees_pending_amount": s_data["fees_pending"],
                        "admission_date": date(2026, 6, 1)
                    }
                )

                # Page 8: Academic Marks for Ananya R (A-1021)
                if s_data["adm"] == "A-1021":
                    marks_data = [
                        ("Term 1", "Tamil", 88.00, 100.00, "A"),
                        ("Term 1", "English", 92.00, 100.00, "A+"),
                        ("Term 1", "Mathematics", 95.00, 100.00, "A+"),
                        ("Term 1", "Science", 90.00, 100.00, "A+"),
                        ("Term 1", "Social", 84.00, 100.00, "A"),
                    ]
                    for term, subj, mrk, max_m, grd in marks_data:
                        AcademicRecord.objects.update_or_create(
                            student=st,
                            term=term,
                            subject=subj,
                            defaults={
                                "marks": mrk,
                                "max_marks": max_m,
                                "grade": grd
                            }
                        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded Student Module data matching UI preview!"))
