# Blind SQL Injector </sub>with SQLMap API</sub>
This tool automates data extraction by leveraging the SQLMap API at manually identified Blind SQL injection points.

SQLMap is a tool designed to automatically detect SQL injection points and streamline the data extraction process. 

However, when SQLMap is unable to automatically identify injection points, there remains a need for efficient data extraction from manually detected vulnerabilities.

To address this, I developed a tool that utilizes the SQLMap API enabling automated data extraction from injection points identified manually by the tester.

## Getting started
```bash
pip install -r requirements.txt

python python sqlmapapi.py -s -H 127.0.0.1 -p 8775

python injector.py
```
