import sqlite3
import sys
import time

from PyQt5 import QtGui
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget, QComboBox, QVBoxLayout, QGridLayout, QDialog, QFileDialog, \
    QPushButton, QApplication, QMainWindow, QMessageBox, QLabel, QLineEdit, QDateEdit


class DBHelper:
    def __init__(self):
        self.conn = sqlite3.connect("sdms.db")
        self.c = self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS students(reg INTEGER, roll INTEGER, name TEXT, mother TEXT, "
                       "father TEXT, gender INTEGER, dob TEXT, branch INTEGER, address TEXT, mobile INTEGER, "
                       "image TEXT, document TEXT, marks TEXT)")
        self.c.execute("CREATE TABLE IF NOT EXISTS payments(receipt_no INTEGER, reg INTEGER, fee INTEGER, receipt_date TEXT)")

    def addStudent(self, name, mother, father, gender, branch, dob, marks_set, address, mobile, image, document):
        try:
            try:
                self.c.execute("SELECT reg from students WHERE reg = (SELECT MAX(reg) FROM students)")
                reg = self.c.fetchone()[0] + 1
            except:
                reg = 1

            marks = str(marks_set).strip('[]').replace(' ', '')
            self.c.execute("INSERT INTO students (reg, roll, name, mother, father, gender, dob, branch, address, mobile, image, "
                           "document, marks) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (reg, '-1', name, mother, father, gender, dob, branch, address, mobile, image, document, marks))
            self.conn.commit()
            self.c.close()
            self.conn.close()
            QMessageBox.information(QMessageBox(), 'Successful', 'Student is successfully registered!\n'
                                                                 'The Registration No is ' + str(reg))
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not register student!')

    def searchStudent(self, reg):
        self.c.execute("SELECT reg FROM students")
        total = self.c.rowcount
        self.c.execute("SELECT * FROM students WHERE reg = " + str(reg))
        data = self.c.fetchone()

        if not data:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not find any student with Registration no ' + str(reg))
            return None
        list = []
        for i in range(0, 11):
            list.append(data[i])
        self.c.close()
        self.conn.close()

        showStudent(list, total)

    def addPayment(self, reg, fee):
        receipt_no = int(time.time())
        date = time.strftime("%b %d %Y %H:%M:%S")
        try:
            self.c.execute("SELECT * from students WHERE reg = " + str(reg))
            self.conn.commit()

            if not self.c.fetchone():
                QMessageBox.warning(QMessageBox(), 'Error', 'No entries found for Registration No ' + str(reg))
                return None

            try:
                self.c.execute("SELECT MAX(roll) FROM students")
                roll = self.c.fetchone()[0] + 1
                if roll == 0:
                    roll = 1
                self.conn.commit()
            except:
                roll = 1

            self.c.execute("SELECT * from payments WHERE reg = " + str(reg))
            self.conn.commit()

            if not self.c.fetchone():
                self.c.execute(
                    "INSERT INTO payments (receipt_no, reg, fee, receipt_date) VALUES (?, ?, ?, ?)",
                    (receipt_no, reg, fee, date))
                self.c.execute(
                    "UPDATE students SET roll = ? WHERE reg = ?", (reg, roll))
                self.conn.commit()
                QMessageBox.information(QMessageBox(), 'Successful', 'Payment is added successfully to the database.\n'
                                                                     'Reference ID = ' + str(receipt_no) +
                                        '\n Assigned Roll No is ' + str(roll))
            else:
                QMessageBox.warning(QMessageBox(), 'Error', 'Student with Reg No ' + str(reg) +
                                    ' has already paid for admisssion!')
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not add payment to the database.')

        self.c.close()
        self.conn.close()

    def searchPayment(self, reg):
        self.c.execute("SELECT * from payments WHERE reg = " + str(reg) + " ORDER BY receipt_no DESC")
        data = self.c.fetchone()
        if not data:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not find any payment recorded for Registration No ' +
                                str(reg))
            return None
        list = []
        for i in range(0, 4):
            list.append(data[i])
        self.c.close()
        self.conn.close()
        showPaymentFunction(list)


class Login(QDialog):

    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.userNameLabel = QLabel("Username")
        self.userPassLabel = QLabel("Password")
        self.textName = QLineEdit(self)
        self.textPass = QLineEdit(self)
        self.buttonLogin = QPushButton('Login', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        layout = QGridLayout(self)
        layout.addWidget(self.userNameLabel, 1, 1)
        layout.addWidget(self.userPassLabel, 2, 1)
        layout.addWidget(self.textName, 1, 2)
        layout.addWidget(self.textPass, 2, 2)
        layout.addWidget(self.buttonLogin, 3, 1, 1, 2)

        self.setWindowTitle("Login")

    def handleLogin(self):
        if (self.textName.text() == 'admin' and
                self.textPass.text() == 'admin'):
            self.accept()
        else:
            QMessageBox.warning(
                self, 'Error', 'Bad user or password')


def showStudent(list, total):
    if list[1] == -1:
        list[1] = '(Payment Not Received)'

    if list[5] == 0:
        list[5] = "Male"
    else:
        list[5] = "Female"

    if list[7] == 0:
        list[7] = "Mechanical Engineering"
    elif list[7] == 1:
        list[7] = "Civil Engineering"
    elif list[7] == 2:
        list[7] = "Electrical Engineering"
    elif list[7] == 3:
        list[7] = "Electronics and Communication Engineering"
    elif list[7] == 4:
        list[7] = "Computer Science and Engineering"
    elif list[7] == 5:
        list[7] = "Information Technology"

    labels = ["Registration No", "Roll No", "Name", "Mother's Name", "Father's Name",
              "Gender", "Date of Birth", "Branch", "Address", "Mobile", "Image", "Marksheet"]

    table = QTableWidget()
    tableItem = QTableWidgetItem()
    table.setWindowTitle("Student Registration Details")
    table.setRowCount(10)
    table.setColumnCount(2)
    imageArea = QLabel("Passport Sized Image")
    for x in range(10):
        table.setItem(x, 0, QTableWidgetItem(labels[x]))
        table.setItem(x, 1, QTableWidgetItem(str(list[x])))
        imageArea.setPixmap(QtGui.QPixmap(list[10]).scaledToHeight(220, Qt.SmoothTransformation))
    table.horizontalHeader().setStretchLastSection(True)
    table.show()

    dialog = QDialog()
    layout = QGridLayout(dialog)
    dialog.setWindowTitle("Viewing 1 out of " + str(total) + " Registered Students")
    dialog.resize(500, 350)
    dialog.setMinimumSize(500, 350)
    dialog.setMaximumSize(600, 350)
    layout.addWidget(imageArea, 0, 3)
    layout.addWidget(table, 0, 1, 2, 2)
    dialog.setLayout(layout)
    dialog.exec()


# function to show the payments records holding the roll number given
def showPaymentFunction(list):
    table = QTableWidget()
    tableItem = QTableWidgetItem()
    table.setWindowTitle("Student Payment Details")
    table.setRowCount(4)
    table.setColumnCount(2)

    labels = ["Receipt No", "Registration No", "Total Fee", "Receipt Date"]
    for i in range(4):
        table.setItem(i, 0, QTableWidgetItem(labels[i]))
        table.setItem(i, 1, QTableWidgetItem(str(list[i])))

    table.horizontalHeader().setStretchLastSection(True)
    table.show()
    dialog = QDialog()
    dialog.setWindowTitle("Student Payment Details")
    dialog.resize(500, 300)
    dialog.setLayout(QVBoxLayout())
    dialog.layout().addWidget(table)
    dialog.exec()


class AddStudent(QDialog):
    def uploadPDF(self):
        try:
            self.document, _ = QFileDialog.getOpenFileName(self, 'Upload Scanned 12th Marksheet', '~/', '*.pdf')
            self.documentName.setText(self.document)
        finally:
            return

    def uploadImage(self):
        self.image, _ = QFileDialog.getOpenFileName(self, 'Upload Passport Sized Image', '~/', '*.jpg;*.jpeg;*.png')
        self.imageArea.setPixmap(QtGui.QPixmap(self.image).scaledToHeight(
            self.imageArea.height(), Qt.SmoothTransformation))
        self.resize(600, 390)
        self.show()

    def __init__(self):
        super().__init__()
        self.grid = QGridLayout(self)
        self.document = ''
        self.image = ''
        self.marks = ''
        self.imageArea = QLabel("Upload Passport Sized Image")
        self.imageArea.setPixmap(QtGui.QPixmap("logo.png"))

        self.btnCancel = QPushButton("Cancel", self)
        self.btnReset = QPushButton("Reset", self)
        self.btnAdd = QPushButton("Submit Registration Details", self)
        self.btnCancel.setFixedHeight(30)
        self.btnReset.setFixedHeight(30)
        self.btnAdd.setFixedHeight(30)

        self.branchLabel = QLabel("Branch")
        self.branchCombo = QComboBox(self)
        self.branchCombo.addItem("Mechanical")
        self.branchCombo.addItem("Civil")
        self.branchCombo.addItem("Electrical")
        self.branchCombo.addItem("Electronics and Communication")
        self.branchCombo.addItem("Computer Science")
        self.branchCombo.addItem("Information Technology")

        self.nameLabel = QLabel("Full Name")
        self.nameText = QLineEdit(self)
        self.motherLabel = QLabel("Mother's Name")
        self.motherText = QLineEdit(self)
        self.fatherLabel = QLabel("Father's Name")
        self.fatherText = QLineEdit(self)

        self.documentName = QLabel("Photo max size 1mb, jpg, png only\nMarksheet 2mb, pdf only")
        self.addressLabel = QLabel("Address")
        self.mobLabel = QLabel("Mobile")
        self.academicYearLabel = QLabel("Academic Year")
        self.genderLabel = QLabel("Gender")
        self.dobLabel = QLabel("Date of Birth")
        self.marksLabel = QLabel("12th Marks in %")
        self.mathsLabel = QLabel("Maths %")
        self.englishLabel = QLabel("English %")
        self.physicsLabel = QLabel("Physics %")

        self.genderCombo = QComboBox(self)
        self.genderCombo.addItem("Male")
        self.genderCombo.addItem("Female")

        self.btnDocument = QPushButton("Upload Scanned 12th Marksheet", self)
        self.btnImage = QPushButton("Upload Passport-sized Photo", self)
        self.dobSelector = QDateEdit(calendarPopup=True)

        self.btnDocument.setFixedHeight(30)
        self.btnImage.setFixedHeight(30)
        self.dobSelector.setDateRange(QDate(1970, 1, 1), QDate(2004, 1, 31))
        self.dobSelector.setDate(QDate(2002, 1, 1))

        self.btnDocument.clicked.connect(self.uploadPDF)
        self.btnImage.clicked.connect(self.uploadImage)

        self.addressText = QLineEdit(self)
        self.mobText = QLineEdit(self)
        self.marks = QLineEdit(self)
        self.maths = QLineEdit(self)
        self.english = QLineEdit(self)
        self.physics = QLineEdit(self)

        self.grid.addWidget(self.imageArea, 1, 3, 5, 1)
        self.grid.addWidget(self.btnImage, 6, 3)
        self.grid.addWidget(self.btnDocument, 7, 3)
        self.grid.addWidget(self.documentName, 8, 3, 2, 1)

        self.grid.addWidget(self.nameLabel, 1, 1)
        self.grid.addWidget(self.motherLabel, 2, 1)
        self.grid.addWidget(self.fatherLabel, 3, 1)
        self.grid.addWidget(self.genderLabel, 4, 1)
        self.grid.addWidget(self.dobLabel, 5, 1)
        self.grid.addWidget(self.addressLabel, 6, 1)
        self.grid.addWidget(self.mobLabel, 7, 1)
        self.grid.addWidget(self.branchLabel, 8, 1)

        self.grid.addWidget(self.nameText, 1, 2)
        self.grid.addWidget(self.motherText, 2, 2)
        self.grid.addWidget(self.fatherText, 3, 2)
        self.grid.addWidget(self.genderCombo, 4, 2)
        self.grid.addWidget(self.dobSelector, 5, 2)
        self.grid.addWidget(self.addressText, 6, 2)
        self.grid.addWidget(self.mobText, 7, 2)
        self.grid.addWidget(self.branchCombo, 8, 2)
        self.marksArea = QGridLayout(self)
        self.marksArea.addWidget(self.marksLabel, 1, 1)
        self.marksArea.addWidget(self.mathsLabel, 1, 3)
        self.marksArea.addWidget(self.physicsLabel, 1, 5)
        self.marksArea.addWidget(self.englishLabel, 1, 7)
        self.marksArea.addWidget(self.marks, 1, 2)
        self.marksArea.addWidget(self.maths, 1, 4)
        self.marksArea.addWidget(self.physics, 1, 6)
        self.marksArea.addWidget(self.english, 1, 8)

        self.grid.addLayout(self.marksArea, 9, 1, 1, 2)

        # adding three buttons
        self.grid.addWidget(self.btnReset, 10, 1)
        self.grid.addWidget(self.btnCancel, 10, 3)
        self.grid.addWidget(self.btnAdd, 10, 2)

        # button connectors
        self.btnAdd.clicked.connect(self.addStudent)
        self.btnCancel.clicked.connect(self.close)
        self.btnReset.clicked.connect(self.reset)

        self.setLayout(self.grid)
        self.setWindowTitle("Register Student For UG Course")
        self.resize(600, 390)
        self.setMaximumWidth(600)
        self.setMaximumHeight(390)
        self.show()
        x = self.documentName.width()
        self.documentName.setMaximumWidth(x)
        self.documentName.setWordWrap(True)
        self.exec()

    def reset(self):
        self.nameText.setText("")
        self.addressText.setText("")
        self.mobText.setText("")
        self.marks.setText("")
        self.maths.setText("")
        self.english.setText("")
        self.physics.setText("")
        self.dobSelector.setDate(QDate(2002, 1, 1))
        self.documentName.setText("")
        self.imageArea.setPixmap(QtGui.QPixmap("logo.png"))

    def addStudent(self):
        self.marks_set = [self.marks.text(), self.maths.text(), self.english.text(), self.physics.text()]
        if self.check_eligibility():
            self.dbhelper = DBHelper()
            self.dbhelper.addStudent(self.nameText.text(), self.motherText.text(), self.fatherText.text(),
                                      self.genderCombo.currentIndex(), self.branchCombo.currentIndex(),
                                      self.dobSelector.date().toString('dd-MM-yyyy'), self.marks_set,
                                      self.addressText.text(), int(self.mobText.text()), self.image, self.document)
        else:
            self.branchCombo.focusWidget()

# function to check eligibility for admission in any branch:
    def check_eligibility(self):
        error = ''
        if self.nameText.text() == '':
            error += 'Enter student\'s full name.\n'
        if self.mobText.text() == '':
            error += 'Please enter a valid mobile number without STD code.\n'
        if self.addressText.text() == '':
            error += 'Enter student\'s permanent address.\n'
        if self.documentName.text() == '':
            error += 'Upload a scanned PDF of 12th marksheet.\n'
        if self.marks.text() == '':
            error += 'Please enter % marks gained in 12th standard.'
        if error != '':
            QMessageBox.warning(QMessageBox(), 'Incomplete Form', error)
            return False

        valid = True
        branch_id = self.branchCombo.currentIndex()
        labels = ["Mechanical", "Civil", "Electrical", "Electronics and Communication", "Computer Science", "Information Technology"]
        marks = ["12th Standard", "Maths", "English", "Physics"]
        required = [[75, 65, 50, 65], [75, 65, 50, 65], [75, 70, 50, 65], [75, 70, 50, 65], [75, 65, 50, 50], [75, 65, 50, 50]]

        for i in range(4):
            if self.marks_set[i] == '':
                QMessageBox.warning(QMessageBox(), 'Incomplete Form',
                                    'A minimum of ' + str(required[branch_id][i]) + '% is required in ' + marks[i] +
                                    ' for admission in ' + labels[branch_id])
            if int(self.marks_set[i]) < required[branch_id][i]:
                QMessageBox.warning(QMessageBox(), 'Failed!',
                                    'Student is not eligible for admission in ' + labels[branch_id] + '\n' +
                                    'The minimum marks required in ' + marks[i] + ' is ' +
                                    str(required[branch_id][i]) + '%')
                return False
        QMessageBox.information(QMessageBox(), 'Successful!', 'Student is eligible for ' + labels[branch_id])
        return True


class AddPayment(QDialog):
    def __init__(self):
        super().__init__()

        # general variables
        self.receipt_no = -1

        self.btnCancel = QPushButton("Cancel", self)
        self.btnReset = QPushButton("Reset", self)
        self.btnAdd = QPushButton("Submit Payment Details", self)

        self.btnCancel.setFixedHeight(30)
        self.btnReset.setFixedHeight(30)
        self.btnAdd.setFixedHeight(30)

        self.regLabel = QLabel("Registration No")
        self.feeLabel = QLabel("Total Fee")

        self.regText = QLineEdit(self)
        self.feeLabelText = QLineEdit(self)

        self.grid = QGridLayout(self)
        self.grid.addWidget(self.regLabel, 1, 1)
        self.grid.addWidget(self.feeLabel, 2, 1)

        self.grid.addWidget(self.regText, 1, 2)
        self.grid.addWidget(self.feeLabelText, 2, 2)

        # adding three buttons
        self.grid.addWidget(self.btnReset, 4, 1)
        self.grid.addWidget(self.btnCancel, 4, 3)
        self.grid.addWidget(self.btnAdd, 4, 2)

        # button connectors
        self.btnAdd.clicked.connect(self.addPayment)
        self.btnCancel.clicked.connect(self.close)
        self.btnReset.clicked.connect(self.reset)

        self.setLayout(self.grid)
        self.setWindowTitle("Add Payment Details")
        self.resize(400, 200)
        self.show()
        self.exec()

    def reset(self):
        self.regText.setText("")
        self.feeLabelText.setText("")

    def addPayment(self):
        if self.regText.text() == "":
            QMessageBox.warning(QMessageBox(), 'Missing Registration No', "Please enter Registration No to search.")
            return False
        if self.feeLabelText.text() == '':
            QMessageBox.warning(QMessageBox(), 'Missing Amount', "Please enter the amount paid!")
            return False

        self.dbhelper = DBHelper()
        self.dbhelper.addPayment(int(self.regText.text()), int(self.feeLabelText.text()))


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vbox = QVBoxLayout()
        self.text = QLabel("Enter the Reg No of the student")
        self.editField = QLineEdit()
        self.btnSearch = QPushButton("Search", self)
        self.btnSearch.clicked.connect(self.showStudent)
        self.vbox.addWidget(self.text)
        self.vbox.addWidget(self.editField)
        self.vbox.addWidget(self.btnSearch)
        self.dialog = QDialog()
        self.dialog.setWindowTitle("Enter Roll No")
        self.dialog.setLayout(self.vbox)

        self.vboxPayment = QVBoxLayout()
        self.textPayment = QLabel("Enter the Reg No of the student")
        self.editFieldPayment = QLineEdit()
        self.btnSearchPayment = QPushButton("Search", self)
        self.btnSearchPayment.clicked.connect(self.showStudentPayment)
        self.vboxPayment.addWidget(self.textPayment)
        self.vboxPayment.addWidget(self.editFieldPayment)
        self.vboxPayment.addWidget(self.btnSearchPayment)
        self.dialogPayment = QDialog()
        self.dialogPayment.setWindowTitle("Enter Reg No")
        self.dialogPayment.setLayout(self.vboxPayment)

        self.btnEnterStudent = QPushButton("Register New Student", self)
        self.btnEnterPayment = QPushButton("Confirm Student's Payment", self)
        self.btnShowStudentDetails = QPushButton("Check Registration Details", self)
        self.btnShowPaymentDetails = QPushButton("Check Payment Receipts", self)

        # picture
        self.picLabel = QLabel(self)
        self.picLabel.resize(190, 200)
        self.picLabel.move(150, 10)
        self.picLabel.setScaledContents(True)
        self.picLabel.setPixmap(QtGui.QPixmap("logo.png"))

        self.btnEnterStudent.move(15, 200)
        self.btnEnterStudent.resize(220, 40)
        self.btnEnterStudentFont = self.btnEnterStudent.font()
        self.btnEnterStudentFont.setPointSize(13)
        self.btnEnterStudent.setFont(self.btnEnterStudentFont)
        self.btnEnterStudent.clicked.connect(AddStudent)

        self.btnEnterPayment.move(245, 200)
        self.btnEnterPayment.resize(220, 40)
        self.btnEnterPaymentFont = self.btnEnterStudent.font()
        self.btnEnterPaymentFont.setPointSize(13)
        self.btnEnterPayment.setFont(self.btnEnterPaymentFont)
        self.btnEnterPayment.clicked.connect(AddPayment)

        self.btnShowStudentDetails.move(15, 250)
        self.btnShowStudentDetails.resize(220, 40)
        self.btnShowStudentDetailsFont = self.btnEnterStudent.font()
        self.btnShowStudentDetailsFont.setPointSize(13)
        self.btnShowStudentDetails.setFont(self.btnShowStudentDetailsFont)
        self.btnShowStudentDetails.clicked.connect(self.dialog.exec)

        self.btnShowPaymentDetails.move(245, 250)
        self.btnShowPaymentDetails.resize(220, 40)
        self.btnShowPaymentDetailsFont = self.btnEnterStudent.font()
        self.btnShowPaymentDetailsFont.setPointSize(13)
        self.btnShowPaymentDetails.setFont(self.btnShowPaymentDetailsFont)
        self.btnShowPaymentDetails.clicked.connect(self.dialogPayment.exec)

        self.resize(480, 300)
        self.picLabel.setStyleSheet("background-color: #00000000")
        self.btnEnterPayment.setStyleSheet("background-color: #ffffff")
        self.btnEnterStudent.setStyleSheet("background-color: #ffffff")
        self.btnShowPaymentDetails.setStyleSheet("background-color: #ffffff")
        self.btnShowStudentDetails.setStyleSheet("background-color: #ffffff")
        self.setStyleSheet("background-color: #bbbbbb")
        self.setWindowTitle("Student Admission System")

    def showStudent(self):
        if self.editField.text() == "":
            QMessageBox.warning(QMessageBox(), 'Error', 'You must give the Reg number to show the results for.')
            return None
        showstudent = DBHelper()
        showstudent.searchStudent(int(self.editField.text()))

    def showStudentPayment(self):
        if self.editFieldPayment.text() == "":
            QMessageBox.warning(QMessageBox(), 'Error', 'You must give the Reg number to show the results for.')
            return None
        showstudent = DBHelper()
        showstudent.searchPayment(int(self.editFieldPayment.text()))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("icon.jpg"))

    login = Login()

    if login.exec_() == QDialog.Accepted:
        window = Window()
        window.show()
    sys.exit(app.exec_())
