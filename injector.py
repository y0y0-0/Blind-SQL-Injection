import sys
import requests
import json
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QWidget, QFileDialog

class SQLMapGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blind SQL Injector with SQLMap")
        self.setGeometry(100, 100, 800, 600)
        
        # Current task ID
        self.task_id = None
        self.stop_flag = False

        # Main layout
        main_layout = QVBoxLayout()

        # Request file section (-r option)
        request_file_layout = QHBoxLayout()
        request_file_label = QLabel("Request File :")
        self.request_file_input = QLineEdit()
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_request_file)
        request_file_layout.addWidget(request_file_label)
        request_file_layout.addWidget(self.request_file_input)
        request_file_layout.addWidget(browse_button)
        main_layout.addLayout(request_file_layout)

        # Parameter section
        param_layout = QHBoxLayout()
        param_label = QLabel("Parameter :")
        self.param_input = QLineEdit()
        param_layout.addWidget(param_label)
        param_layout.addWidget(self.param_input)
        main_layout.addLayout(param_layout)

        # Prefix and Suffix section
        prefix_suffix_layout = QHBoxLayout()
        prefix_label = QLabel("Prefix:")
        self.prefix_input = QLineEdit()
        suffix_label = QLabel("Suffix:")
        self.suffix_input = QLineEdit()
        prefix_suffix_layout.addWidget(prefix_label)
        prefix_suffix_layout.addWidget(self.prefix_input)
        prefix_suffix_layout.addWidget(suffix_label)
        prefix_suffix_layout.addWidget(self.suffix_input)
        main_layout.addLayout(prefix_suffix_layout)

        # String and Tamper section
        string_tamper_layout = QHBoxLayout()
        string_label = QLabel("String:")
        self.string_input = QLineEdit()
        tamper_label = QLabel("Tamper:")
        self.tamper_input = QLineEdit()
        string_tamper_layout.addWidget(string_label)
        string_tamper_layout.addWidget(self.string_input)
        string_tamper_layout.addWidget(tamper_label)
        string_tamper_layout.addWidget(self.tamper_input)
        main_layout.addLayout(string_tamper_layout)

        # Proxy section
        proxy_layout = QHBoxLayout()
        proxy_label = QLabel("Proxy:")
        self.proxy_input = QLineEdit("http://127.0.0.1:8888")
        proxy_layout.addWidget(proxy_label)
        proxy_layout.addWidget(self.proxy_input)
        main_layout.addLayout(proxy_layout)

        # Output TextArea
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        main_layout.addWidget(self.output)

        # Start and Stop buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_test)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_test)
        button_layout.addWidget(self.stop_button)

        main_layout.addLayout(button_layout)

        # Set main widget and layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def browse_request_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Request File")
        if file_name:
            self.request_file_input.setText(file_name)

    def start_test(self):
        self.stop_flag = False
        api_url = "http://127.0.0.1:8775"

        # 1. Create a new task
        task_response = requests.get(f"{api_url}/task/new")
        self.task_id = task_response.json()["taskid"]
        # self.output.append("New Task Created. Task ID: " + self.task_id)

        # 2. Set options
        options_url = f"{api_url}/option/{self.task_id}/set"
        options = {
            "method": "GET",
            "proxy": self.proxy_input.text(),
            "batch": True,
            "flushSession": False,
            "p": self.param_input.text(),
            "suffix": self.suffix_input.text(),
            "prefix": self.prefix_input.text(),
            "string": self.string_input.text(),
            "tamper": self.tamper_input.text(),
            "getCurrentDb": True,
            "getBanner": True,
            "getCurrentUser": True,
            "getDbs": True,
            "getTables": False    
        }

        # Include the -r option if a request file is specified
        if self.request_file_input.text():
            options["requestFile"] = self.request_file_input.text()

        # Debug output to verify options being sent
        # self.output.append("Options being sent to API:")
        formatted_options = json.dumps(options, indent=4)
        # self.output.append(formatted_options)

        # Set options request
        options_response = requests.post(options_url, data=formatted_options, headers={"Content-Type": "application/json"})

        # 3. Start scan
        scan_url = f"{api_url}/scan/{self.task_id}/start"
        scan_response = requests.post(scan_url, data=json.dumps(options), headers={"Content-Type": "application/json"})
        if scan_response.json()["success"]:
            self.output.append("Scan started successfully")

        # 4. Check scan progress and get results
        status_url = f"{api_url}/scan/{self.task_id}/status"
        result_url = f"{api_url}/scan/{self.task_id}/data"

        while not self.stop_flag:
            status_response = requests.get(status_url)
            status = status_response.json()["status"]
            if status == "terminated":
                self.output.append("Scan terminated.")
                break
            else:
                self.output.append("Scan in progress...")
                QApplication.processEvents()
                time.sleep(5)

        if not self.stop_flag:
            result_response = requests.get(result_url)
            scan_results = result_response.json()
            self.display_formatted_results(scan_results)

    def display_formatted_results(self, scan_results):
        # Format and display each entry in scan results
        if "data" in scan_results and scan_results["data"]:
            self.output.append("\nScan Results:")
            for entry in scan_results["data"]:
                # Filter out unwanted types
                if entry.get("type") in [0, 1, 5]:  # Skip types 0 1 5
                    continue
                
                if entry.get("type") == 4:  # Current user
                    self.output.append(f"\nCurrent user: [*] '{entry['value']}'")
                elif entry.get("type") == 3:  # Database version
                    self.output.append(f"Database version: [*] '{entry['value']}'")
                elif entry.get("type") == 12:  # Databases
                    self.output.append("\nAvailable databases:")
                    for db in entry["value"]:
                        self.output.append(f"[*] '{db}'")
                elif entry.get("type") == 13:  # Tables in each database
                    self.output.append("\nTables in databases:")
                    for db_name, tables in entry["value"].items():
                        self.output.append(f"Database: '{db_name}'")
                        for table in tables:
                            self.output.append(f"    [*] '{table}'")
                else:
                    # Generic display if structure is different
                    self.output.append(json.dumps(entry, indent=4))
        else:
            self.output.append("No data found or scan returned empty results.")

    def stop_test(self):
        if self.task_id:
            api_url = "http://127.0.0.1:8775"
            stop_url = f"{api_url}/scan/{self.task_id}/stop"
            stop_response = requests.get(stop_url)
            if stop_response.json()["success"]:
                self.output.append("Scan stopped successfully")
                self.stop_flag = True
            else:
                self.output.append("Failed to stop the scan")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SQLMapGUI()
    window.show()
    sys.exit(app.exec_())
