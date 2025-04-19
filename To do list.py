import sys
import json
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont


class TodoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Todo List")
        self.setGeometry(300, 300, 400, 600)
        self.setStyleSheet("background-color: #f7d1d0;")

        self.tasks = self.load_tasks()
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("My Tasks")
        header.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header.setStyleSheet("color: #9e3e3d; margin-bottom: 20px;")
        layout.addWidget(header)

        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
            QListWidget {
                background: white;
                border-radius: 10px;
                padding: 10px;
            }
            QListWidget::item {
                border-bottom: 1px solid #EEEEEE;
                padding: 12px;
            }
        """)
        self.update_task_list()
        layout.addWidget(self.task_list)

        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Add new task...")
        self.task_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #9e3e3d;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        input_layout.addWidget(self.task_input)

        add_btn = QPushButton("+")
        add_btn.setFixedSize(40, 40)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #9e3e3d;
                color: white;
                border-radius: 20px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color:#bf4e4d;
            }
        """)
        add_btn.clicked.connect(self.add_task)
        input_layout.addWidget(add_btn)
        layout.addLayout(input_layout)

    def create_task_item(self, text, completed=False):
        widget = QWidget()
        layout = QHBoxLayout(widget)

        checkbox = QCheckBox()
        checkbox.setChecked(completed)
        checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #9e3e3d;
                border-radius: 2px;
            }
            QCheckBox::indicator:checked {
                background-color: #9e3e3d;
            }
        """)

        label = QLabel(text)
        label.setFont(QFont("Arial", 12))
        if completed:
            label.setStyleSheet("color: #95a5a6; text-decoration: line-through;")

        checkbox.stateChanged.connect(lambda state, l=label: self.toggle_task(l, state))

        delete_btn = QPushButton("✕")
        delete_btn.setFixedSize(30, 30)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6666;
                color: white;
                border-radius: 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color:#ff4d4d;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_task(text))

        layout.addWidget(checkbox)
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(delete_btn)

        return widget

    def update_task_list(self):
        self.task_list.clear()
        for task in self.tasks:
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 70))
            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, self.create_task_item(task["task"], task["completed"]))

    def toggle_task(self, label, state):
        if state == Qt.CheckState.Checked.value:
            label.setStyleSheet("color: #95a5a6; text-decoration: line-through;")
        else:
            label.setStyleSheet("color: black; text-decoration: none;")
        self.save_tasks()

    def add_task(self):
        text = self.task_input.text().strip()
        if text:
            self.tasks.append({"task": text, "completed": False})
            self.task_input.clear()
            self.update_task_list()
            self.save_tasks()

    def delete_task(self, task_text):
        self.tasks = [task for task in self.tasks if task["task"] != task_text]
        self.update_task_list()
        self.save_tasks()

    def load_tasks(self):
        try:
            with open("tasks.json", "r") as f:
                return json.load(f)
        except:
            return []

    def save_tasks(self):
        with open("tasks.json", "w") as f:
            json.dump(self.tasks, f)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TodoApp()
    window.show()
    sys.exit(app.exec())
