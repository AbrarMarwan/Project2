import json
import os
from PyQt6.QtWidgets import (QCheckBox,
                            QApplication, QMainWindow, QLabel, QLineEdit,QSizePolicy,
                            QPushButton, QMessageBox, QVBoxLayout,QInputDialog,QSpacerItem,
                            QWidget, QTableWidget, QTableWidgetItem, QFileDialog, QComboBox
                            )
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt
import shutil
import pyttsx3
import speech_recognition as sr
import webbrowser
import datetime
import time
import pyautogui
import numpy as np
import pygame
import face_recognition
import cv2 as cv

# Helper functions for JSON data management
def load_json(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# Global Variables
STUDENTS_FILE = "students.json"
USERS_FILE = "users.json"
FACE_PATH = "person"
ASSIGNMENTS_FILE = "assignments.json"



# CSS Style for the Application
APP_CSS = """
    QMainWindow {
        background-color: #f7d1d0;
        font-family: Arial, sans-serif;
    }
    QLabel {
        color: #6b0100;
    }
    QLineEdit {
        padding: 10px;
        border: 2px solid #bd6160;
        border-radius: 8px;
        font-size: 14px;
    }
    QLineEdit:focus {
        border: 2px solid #bf4e4d;
    }
    QPushButton {
        background-color: #bf4e4d;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #9e3e3d;
    }
    QPushButton:pressed {
        background-color: #762f2e;
    }
"""




# Helper Functions
def load_json(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def find_encodings(images):
    encode_list = []
    for img in images:
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encode_list.append(encode)
    return encode_list

def load_face_data():
    images = []
    class_names = []
    person_list = os.listdir(FACE_PATH)

    for c1 in person_list:
        cur_person = cv.imread(f"{FACE_PATH}/{c1}")
        images.append(cur_person)
        class_names.append(os.path.splitext(c1)[0])

    encode_list_known = find_encodings(images)
    return encode_list_known, class_names

# Login Window
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تسجيل الدخول - نظام إدارة المدرسة")
        self.setWindowIcon(QIcon("school.png"))
        self.setFixedSize(450, 350)

        # Layout
        layout = QVBoxLayout()

        # Username Input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم")
        layout.addWidget(self.username_input)

        # Password Input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.user_type_combo = QComboBox()
        self.user_type_combo.addItems(["مدرس", "طالب"])
        layout.addWidget(self.user_type_combo)

        # Login Button
        self.login_button = QPushButton("تسجيل الدخول")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.create_account_button = QPushButton("إنشاء حساب جديد")
        self.create_account_button.clicked.connect(self.open_create_account_window)
        layout.addWidget(self.create_account_button)

        self.forgot_password_button = QPushButton("نسيت كلمة المرور؟")
        self.forgot_password_button.clicked.connect(self.open_forgot_password_window)
        layout.addWidget(self.forgot_password_button)

        # Face Recognition Button
        self.face_recognition_button = QPushButton("التعرف على الوجه")
        self.face_recognition_button.clicked.connect(self.face_recognition_login)
        layout.addWidget(self.face_recognition_button)

        self.setLayout(layout)
        self.setStyleSheet(APP_CSS)
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        users = load_json(USERS_FILE)

        if username in users and users[username]["password"] == password:
            if users[username]["type"] == "طالب":
                self.close()
                self.student_window = StudentWindow()
                self.student_window.show()
            elif users[username]["type"] == "مدرس":
                self.close()
                self.teacher_window = TeacherWindow()
                self.teacher_window.show()
            else:
                QMessageBox.warning(self, "خطأ", "نوع المستخدم غير صالح.")
        else:
            QMessageBox.warning(self, "خطأ", "اسم المستخدم أو كلمة المرور غير صحيح.")

    def face_recognition_login(self):
        encode_list_known, class_names = load_face_data()

        cap = cv.VideoCapture(0)
        while True:
            ret, img = cap.read()
            if not ret:
                QMessageBox.critical(self, "خطأ", "تعذر الوصول إلى الكاميرا.")
                break

            img_small = cv.resize(img, (0, 0), None, 0.25, 0.25)
            img_small = cv.cvtColor(img_small, cv.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(img_small)
            face_encodings = face_recognition.face_encodings(img_small, face_locations)

            for encode_face, face_loc in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(encode_list_known, encode_face)
                face_dis = face_recognition.face_distance(encode_list_known, encode_face)
                match_index = np.argmin(face_dis)

                if matches[match_index]:
                    name = class_names[match_index].lower()
                    QMessageBox.information(self, "نجاح", f"مرحبًا {name}!")
                    self.login_via_face(name)
                    cap.release()
                    cv.destroyAllWindows()
                    return

            cv.imshow("Face Recognition", img)
            if cv.waitKey(1) == ord("x"):
                break

        cap.release()
        cv.destroyAllWindows()
    def open_forgot_password_window(self):
        self.forgot_password_window = ForgotPasswordWindow()
        self.forgot_password_window.show()
    def login_via_face(self, name):
        users = load_json(USERS_FILE)
        name = name.lower()  # تحويل الاسم إلى حروف صغيرة لتجنب الأخطاء

        # البحث عن الاسم في ملف المستخدمين
        for username, info in users.items():
            if username.lower() == name:  # مطابقة غير حساسة لحالة الأحرف
                if info["type"] == "طالب":
                    self.close()
                    self.student_window = StudentWindow()
                    self.student_window.show()
                elif info["type"] == "مدرس":
                    self.close()
                    self.teacher_window = TeacherWindow()
                    self.teacher_window.show()
                else:
                    QMessageBox.warning(self, "خطأ", "نوع المستخدم غير صالح.")
                return

        # إذا لم يتم العثور على الاسم
        QMessageBox.warning(self, "خطأ", "تعذر العثور على بيانات المستخدم.")

    def open_create_account_window(self):
        self.create_account_window = CreateAccountWindow(self)
        self.create_account_window.show()
        self.hide()

class FaceRecognaionWindow(QWidget):
    def __init__(self):
        path = "person"
        images = []
        classNames = []
        personList = os.listdir(path)

        for c1 in personList:
            curPerson = cv.imread(f'{path}/{c1}')
            images.append(curPerson)
            classNames.append(os.path.splitext(c1)[0])
        print(classNames)

        def findEncodeings(images):
            encodeList = []
            for img in images:
                img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
                encode = face_recognition.face_encodings(img)[0]
                encodeList.append(encode)
            return encodeList

        encodeListisKnow = findEncodeings(images)
        print(encodeListisKnow)
        print('Encoding complete')

        cap = cv.VideoCapture(0)
        while True:
            frame, img = cap.read()

            imgs = cv.resize(img, (0, 0), None, 0.25, 0.25)
            imgs = cv.cvtColor(imgs, cv.COLOR_BGR2RGB)
            faceCurentFrame = face_recognition.face_locations(imgs)
            encodeCurentFrame = face_recognition.face_encodings(imgs, faceCurentFrame)
            for encodeface, faceLoc in zip(encodeCurentFrame, faceCurentFrame):
                matches = face_recognition.compare_faces(encodeListisKnow, encodeface)
                faceDis = face_recognition.face_distance(encodeListisKnow, encodeface)
                matchIndex = np.argmin(faceDis)
                if matches[matchIndex]:
                    name = classNames[matchIndex].upper()
                    print(name)
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 0, 255), cv.FILLED)
                    cv.putText(img, name, (x1 + 6, y2 - 6), cv.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            cv.imshow("face recognition", img)
            k = cv.waitKey(1)
            if k == ord("x"):
                break
        cap.release()
        cv.destroyWindow()

class CreateAccountWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("إنشاء حساب جديد")
        self.setWindowIcon(QIcon("ai.png"))  # Replace with your icon
        self.setFixedSize(400, 400)

        # Layout
        layout = QVBoxLayout()

        # Banner or Logo
        self.logo_label = QLabel(self)
        pixmap = QPixmap("user.png")
        set_pixmap=pixmap.scaled(100,100,)# Replace with your banner
        self.logo_label.setPixmap(set_pixmap)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo_label)

        # Username Input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم")
        layout.addWidget(self.username_input)

        # Password Input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        # Confirm Password Input
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("تأكيد كلمة المرور")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm_password_input)

        #Type Button
        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("نوع المستخدم")
        layout.addWidget(self.type_input)


        # Create Account Button
        self.create_account_button = QPushButton("إنشاء حساب")
        self.create_account_button.clicked.connect(self.create_account)
        layout.addWidget(self.create_account_button)

        # Back to Login Button
        self.back_button = QPushButton("عودة")
        self.back_button.clicked.connect(self.back_to_login)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

        # CSS for Create Account Window
        self.setStyleSheet(APP_CSS)
    def create_account(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        type = self.type_input.text()

        if not username or not password or not type:
            QMessageBox.warning(self, "خطأ", "يجب ملء جميع الحقول.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "خطأ", "كلمتا المرور غير متطابقتين.")
            return

        if len(password) < 6:
            QMessageBox.warning(self, "خطأ", "يجب أن تحتوي كلمة المرور على 6 أحرف على الأقل.")
            return
        st="طالب"
        te="مدرس"
        if type !=st  and type !=te:
            QMessageBox.warning(self, "خطأ", "يجب أن يكون اما مدرس او طالب.")
            return

        try:
            users = self.load_users()
            if username in users:
                QMessageBox.warning(self, "خطأ", "اسم المستخدم موجود بالفعل.")
                return

            users[username] = {
                "password": password,
                "type": type
            }

            self.save_users(users)
            QMessageBox.information(self, "نجاح", "تم إنشاء الحساب بنجاح!")
            self.back_to_login()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حفظ البيانات: {e}")

    def back_to_login(self):
        self.close()
        self.parent.show()

    def load_users(self):
        if not os.path.exists("users.json"):
            return {}
        with open("users.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def save_users(self, users):
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)

# Student and Teacher Windows (Dummy)

class StudentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام الطلاب")
        self.setWindowIcon(QIcon("school.png"))
        self.setFixedSize(800, 600)

        main_layout = QVBoxLayout()

        title_label = QLabel("مرحبا ")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
                           font-size: 28px;
                           font-weight: bold;
                           color: black;
                           margin-bottom: 20px;
                       """)
        main_layout.addWidget(title_label)

        self.logo_label = QLabel(self)
        pixmap = QPixmap("lecture-room.png")
        scaled_pixmap = pixmap.scaled(300, 200, Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(scaled_pixmap)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)


        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(15)

        self.view_profile_button = QPushButton("عرض البيانات الشخصية", self)
        self.view_profile_button.setIcon(QIcon("user.png"))
        buttons_layout.addWidget(self.view_profile_button)
        self.view_profile_button.clicked.connect(self.view_profile)

        self.upload_photo_button = QPushButton("رفع صورة شخصية", self)
        self.upload_photo_button.setIcon(QIcon("photo.png"))
        buttons_layout.addWidget(self.upload_photo_button)
        self.upload_photo_button.clicked.connect(self.upload_photo)

        self.view_assignments_button = QPushButton("عرض التكاليف", self)
        self.view_assignments_button.setIcon(QIcon("notebook.png"))
        buttons_layout.addWidget(self.view_assignments_button)
        self.view_assignments_button.clicked.connect(self.view_assignments)

        self.solve_assignments_button = QPushButton("حل التكاليف", self)
        self.solve_assignments_button.setIcon(QIcon("checklist.png"))
        buttons_layout.addWidget(self.solve_assignments_button)
        self.solve_assignments_button.clicked.connect(self.solve_assignments)

        # إضافة الـ buttons_layout إلى الـ main_layout
        main_layout.addLayout(buttons_layout)

        # ضبط المسافات بين العناصر
        main_layout.setSpacing(20)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        self.setStyleSheet(APP_CSS)

    def view_profile(self):
        # طلب رقم الطالب من المستخدم
        student_id, ok = QInputDialog.getText(self, "بحث عن طالب", "أدخل رقم الطالب:")

        if not ok or not student_id.strip():
            QMessageBox.warning(self, "خطأ", "يرجى إدخال رقم الطالب.")
            return

        student_data = load_json(STUDENTS_FILE)  # تحميل بيانات الطلاب
        student_id = student_id.strip()  # إزالة المسافات الزائدة

        # التحقق من وجود الطالب في البيانات
        if student_id in student_data:
            info = student_data[student_id]
            profile_info = f"الاسم: {info['name']}\nالعمر: {info['age']}\nالقسم: {info['department']}"
            QMessageBox.information(self, "البيانات الشخصية", profile_info)
        else:
            QMessageBox.warning(self, "خطأ", "تعذر العثور على بيانات الطالب.")

    def upload_photo(self):
        """رفع صورة شخصية للطالب."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Images (*.png *.xpm *.jpg *.jpeg)")
        if file_dialog.exec():
            photo_path = file_dialog.selectedFiles()[0]
            try:
                # Copy the photo to the person folder with the original file name
                original_name = os.path.basename(photo_path)
                dest_path = os.path.join(FACE_PATH, original_name)
                shutil.copy(photo_path, dest_path)
                QMessageBox.information(self, "نجاح", f"تم رفع الصورة وحفظها بنجاح: {dest_path}")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حفظ الصورة: {e}")

    def view_assignments(self):
        assignments = load_json(ASSIGNMENTS_FILE)
        student_id, ok = QInputDialog.getText(self, "عرض التكاليف", "أدخل رقم الطالب:")

        if not ok or not student_id.strip():
            QMessageBox.warning(self, "خطأ", "يرجى إدخال رقم الطالب.")
            return

        student_id = student_id.strip()
        if student_id in assignments:
            student_assignments = assignments[student_id]
            assignment_text = "\n".join([f"{idx + 1}. {desc}" for idx, desc in enumerate(student_assignments)])
            QMessageBox.information(self, "التكاليف", assignment_text)
        else:
            QMessageBox.information(self, "التكاليف", "لا توجد تكاليف لهذا الطالب.")

    def solve_assignments(self):
        assignments = load_json(ASSIGNMENTS_FILE)
        student_id, ok = QInputDialog.getText(self, "حل التكاليف", "أدخل رقم الطالب:")

        if not ok or not student_id.strip():
            QMessageBox.warning(self, "خطأ", "يرجى إدخال رقم الطالب.")
            return

        student_id = student_id.strip()
        if student_id in assignments:
            student_assignments = assignments[student_id]
            if not student_assignments:
                QMessageBox.information(self, "حل التكاليف", "لا توجد تكاليف لهذا الطالب.")
                return

            for idx, assignment in enumerate(student_assignments):
                solution, ok = QInputDialog.getText(self, f"حل التكليف {idx + 1}", assignment)
                if ok and solution.strip():
                    student_assignments[idx] = f"{assignment} - تم الحل: {solution.strip()}"

            assignments[student_id] = student_assignments
            save_json(ASSIGNMENTS_FILE, assignments)
            QMessageBox.information(self, "نجاح", "تم حفظ حلول التكاليف بنجاح.")
        else:
            QMessageBox.warning(self, "خطأ", "لا توجد تكاليف لهذا الطالب.")


class TeacherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("واجهة المدرس")
        self.setWindowIcon(QIcon("school.png"))
        self.setFixedSize(800, 600)

        main_layout = QVBoxLayout()

        title_label = QLabel("مرحبا ")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
                    font-size: 28px;
                    font-weight: bold;
                    color: black;
                    margin-bottom: 10px;
                """)
        main_layout.addWidget(title_label)

        self.logo_label = QLabel(self)
        pixmap = QPixmap("teacher.png")
        scaled_pixmap = pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(scaled_pixmap)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.logo_label)

        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(15)

        self.add_student_button = QPushButton("إضافة طالب")
        self.add_student_button.setIcon(QIcon("id.png"))
        self.add_student_button.clicked.connect(self.add_student)
        buttons_layout.addWidget(self.add_student_button)

        self.mark_attendance_button = QPushButton("تحضير الطلاب")
        self.mark_attendance_button.setIcon(QIcon("cheake.png"))
        self.mark_attendance_button.clicked.connect(self.mark_attendance)
        buttons_layout.addWidget(self.mark_attendance_button)

        self.add_grades_button = QPushButton("إضافة درجات")
        self.add_grades_button.setIcon(QIcon("exam.png"))
        self.add_grades_button.clicked.connect(self.add_grades)
        buttons_layout.addWidget(self.add_grades_button)

        self.add_assignments_button = QPushButton("إضافة تكاليف")
        self.add_assignments_button.setIcon(QIcon("document.png"))
        self.add_assignments_button.clicked.connect(self.add_assignments)
        buttons_layout.addWidget(self.add_assignments_button)

        self.view_students_button = QPushButton("عرض الطلاب")
        self.view_students_button.setIcon(QIcon("social-media.png"))
        self.view_students_button.clicked.connect(self.view_students)
        buttons_layout.addWidget(self.view_students_button)

        main_layout.addLayout(buttons_layout)

        self.widget_container = QWidget()
        self.widget_container.setLayout(main_layout)

        self.setCentralWidget(self.widget_container)
        self.setStyleSheet(APP_CSS)

    def add_student(self):
        self.student_window = AddStudentWindow()
        self.student_window.show()

    def mark_attendance(self):
        self.attendance_window = MarkAttendanceWindow()
        self.attendance_window.show()

    def add_grades(self):
        self.grades_window = AddGradesWindow()
        self.grades_window.show()

    def add_assignments(self):
        self.assignments_window = AddAssignmentWindow()
        self.assignments_window.show()

    def view_students(self):
        self.students_window = ViewStudentsWindow()
        self.students_window.show()

class AddStudentWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة طالب")
        self.setWindowIcon(QIcon("ai.png"))
        self.setFixedSize(400, 300)

        self.name_label = QLabel("اسم الطالب:", self)
        self.name_label.setGeometry(50, 50, 100, 30)

        self.name_input = QLineEdit(self)
        self.name_input.setGeometry(150, 50, 200, 30)

        self.age_label = QLabel("العمر:", self)
        self.age_label.setGeometry(50, 100, 100, 30)

        self.age_input = QLineEdit(self)
        self.age_input.setGeometry(150, 100, 200, 30)
        self.age_input.setPlaceholderText("مثال: 20")

        self.department_label = QLabel("القسم:", self)
        self.department_label.setGeometry(50, 150, 100, 30)

        self.department_input = QLineEdit(self)
        self.department_input.setGeometry(150, 150, 200, 30)
        self.department_input.setPlaceholderText("مثال: علوم حاسوب")

        self.submit_button = QPushButton("إضافة", self)
        self.submit_button.setGeometry(150, 220, 100, 40)
        self.submit_button.clicked.connect(self.add_student)

        self.setStyleSheet(APP_CSS)

    def add_student(self):
        name = self.name_input.text().strip()
        age = self.age_input.text().strip()
        department = self.department_input.text().strip()

        if not name or not age or not department:
            QMessageBox.warning(self, "خطأ", "يرجى ملء جميع الحقول.")
            return

        students = load_json(STUDENTS_FILE)
        student_id = f"2025{len(students) + 1:02d}"

        students[student_id] = {
            "name": name,
            "age": age,
            "department": department,
            "attendance": [],
            "grades": {},
            "assignments": {}
        }

        save_json(STUDENTS_FILE, students)
        QMessageBox.information(self, "نجاح", f"تم إضافة الطالب: {name}")
        self.close()

# View Students Window


class ViewStudentsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("عرض الطلاب")
        self.setWindowIcon(QIcon("ai.png"))
        self.setFixedSize(600, 400)

        self.table = QTableWidget(self)
        self.table.setGeometry(50, 50, 500, 300)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["رقم الطالب", "اسم الطالب", "العمر", "القسم", "الحضور", "الدرجات"])

        self.load_students()
        self.setStyleSheet(APP_CSS)

    def load_students(self):
        students = load_json(STUDENTS_FILE)
        self.table.setRowCount(len(students))

        for row, (student_id, info) in enumerate(students.items()):
            self.table.setItem(row, 0, QTableWidgetItem(student_id))
            self.table.setItem(row, 1, QTableWidgetItem(info["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(info["age"]))
            self.table.setItem(row, 3, QTableWidgetItem(info["department"]))
            self.table.setItem(row, 4, QTableWidgetItem(", ".join(info["attendance"])))
            grades = ", ".join([f"{subject}: {score}" for subject, score in info.get("grades", {}).items()])
            self.table.setItem(row, 5, QTableWidgetItem(grades))
# Add Assignment Window
class AddAssignmentWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة تكليف")
        self.setWindowIcon(QIcon("ai.png"))
        self.setFixedSize(600, 400)

        self.assignment_label = QLabel("وصف التكليف:", self)
        self.assignment_label.setGeometry(50, 50, 100, 38)

        self.assignment_input = QLineEdit(self)
        self.assignment_input.setGeometry(150, 50, 300, 38)
        self.assignment_input.setPlaceholderText("أدخل وصف التكليف")

        self.student_id_label = QLabel("رقم الطالب:", self)
        self.student_id_label.setGeometry(50, 100, 100, 30)

        self.student_id_input = QLineEdit(self)
        self.student_id_input.setGeometry(150, 100, 300, 30)
        self.student_id_input.setPlaceholderText("أدخل رقم الطالب (أو الكل)")

        self.submit_button = QPushButton("إرسال التكليف", self)
        self.submit_button.setGeometry(250, 200, 100, 40)
        self.submit_button.clicked.connect(self.add_assignment)

        self.setStyleSheet(APP_CSS)

    def add_assignment(self):
        description = self.assignment_input.text().strip()
        student_id = self.student_id_input.text().strip()

        if not description:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال وصف التكليف.")
            return

        assignments = load_json(ASSIGNMENTS_FILE)

        if student_id.lower() == "الكل":
            # إضافة التكليف لجميع الطلاب
            students = load_json(STUDENTS_FILE)
            for sid in students.keys():
                assignments.setdefault(sid, []).append(description)
        elif student_id in assignments:
            # إضافة التكليف لطالب محدد
            assignments.setdefault(student_id, []).append(description)
        else:
            QMessageBox.warning(self, "خطأ", "رقم الطالب غير موجود.")
            return

        save_json(ASSIGNMENTS_FILE, assignments)
        QMessageBox.information(self, "نجاح", "تم إضافة التكليف بنجاح.")
        self.close()


# Mark Attendance Window
class MarkAttendanceWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("تحضير الطلاب")
        self.setWindowIcon(QIcon("ai.png"))
        self.setFixedSize(600, 400)

        self.attendance_label = QLabel("تحديد حالة الحضور للطلاب:", self)
        self.attendance_label.setGeometry(50, 10, 300, 30)

        self.attendance_widgets = []
        self.students = load_json(STUDENTS_FILE)

        # Dynamic UI for students
        self.checkboxes = {}
        y_position = 50
        for student_id, info in self.students.items():
            label = QLabel(f"{info['name']} ({student_id}):", self)
            label.setGeometry(50, y_position, 200, 30)

            checkbox = QCheckBox("حاضر", self)
            checkbox.setGeometry(300, y_position, 100, 30)
            checkbox.setChecked("حاضر" in info["attendance"])
            self.checkboxes[student_id] = checkbox

            y_position += 40

        # Save Button
        self.save_button = QPushButton("حفظ الحضور", self)
        self.save_button.setGeometry(250, y_position + 20, 100, 40)
        self.save_button.clicked.connect(self.save_attendance)

        self.setStyleSheet(APP_CSS)

    def save_attendance(self):
        for student_id, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                if "حاضر" not in self.students[student_id]["attendance"]:
                    self.students[student_id]["attendance"].append("حاضر")
            else:
                if "حاضر" in self.students[student_id]["attendance"]:
                    self.students[student_id]["attendance"].remove("حاضر")

        save_json(STUDENTS_FILE, self.students)
        QMessageBox.information(self, "نجاح", "تم تحديث الحضور للطلاب.")
        self.close()

# Add Grades Window
class AddGradesWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة درجات")
        self.setWindowIcon(QIcon("ai.png"))
        self.setFixedSize(600, 400)

        self.grades_label = QLabel("إدخال درجات الطلاب في المادة:", self)
        self.grades_label.setGeometry(50, 10, 500, 30)

        # تحميل بيانات الطلاب
        self.students = load_json(STUDENTS_FILE)
        self.grade_inputs = {}

        y_position = 50
        for student_id, info in self.students.items():
            # عرض اسم الطالب
            label = QLabel(f"{info['name']} ({student_id}):", self)
            label.setGeometry(50, y_position, 200, 30)

            # إدخال الدرجة
            grade_input = QLineEdit(self)
            grade_input.setGeometry(300, y_position, 200,35)
            grade_input.setPlaceholderText("أدخل الدرجة")
            grade_input.setText(str(info.get("grades", {}).get("برمجة3", "")))

            self.grade_inputs[student_id] = grade_input
            y_position += 40

        # زر حفظ الدرجات
        self.submit_button = QPushButton("حفظ الدرجات", self)
        self.submit_button.setGeometry(250, y_position + 20, 100, 40)
        self.submit_button.clicked.connect(self.save_grades)

        self.setStyleSheet(APP_CSS)

    def save_grades(self):
        """حفظ الدرجات في ملف JSON."""
        for student_id, grade_input in self.grade_inputs.items():
            grade = grade_input.text().strip()
            if grade.isdigit():
                self.students[student_id].setdefault("grades", {})["مادة"] = int(grade)

        save_json(STUDENTS_FILE, self.students)
        QMessageBox.information(self, "نجاح", "تم حفظ الدرجات بنجاح.")
        self.close()

class ForgotPasswordWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نسيت كلمة المرور")
        self.setFixedSize(500, 400)

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("أدخل اسم المستخدم")
        layout.addWidget(self.username_input)

        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("أدخل كلمة المرور الجديدة")
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.new_password_input)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("أدخل تأكيد كلمة المرور")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm_password_input)

        self.reset_button = QPushButton("إعادة تعيين كلمة المرور")
        self.reset_button.clicked.connect(self.reset_password)
        layout.addWidget(self.reset_button)

        self.setLayout(layout)
        self.setStyleSheet(APP_CSS)

    def reset_password(self):
        username = self.username_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not username or not new_password or not confirm_password:
            QMessageBox.warning(self, "خطأ", "يجب ملء جميع الحقول.")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "خطأ", "كلمتا المرور غير متطابقتين.")
            return

        users = self.load_users()

        if username not in users:
            QMessageBox.warning(self, "خطأ", "اسم المستخدم غير موجود.")
            return

        users[username]['password'] = new_password

        self.save_users(users)

        QMessageBox.information(self, "نجاح", "تمت إعادة تعيين كلمة المرور بنجاح.")
        self.close()

    def load_users(self):
        if not os.path.exists("usersp.json"):
            return {}
        with open("usersp.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def save_users(self, users):
        with open("usersp.json", "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    app = QApplication([])
    login_window = LoginWindow()
    login_window.show()
    app.exec()





