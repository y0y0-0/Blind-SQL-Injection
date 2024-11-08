# Blind SQL Injectior
This tool automates data extraction by leveraging the sqlmap API at manually identified Blind SQL injection points.

sqlmap is a tool designed to automatically detect SQL injection points and streamline the data extraction process. 

However, when sqlmap is unable to automatically identify injection points, there remains a need for efficient data extraction from manually detected vulnerabilities.

To address this, I developed a tool that utilizes the sqlmap API, enabling automated data extraction from injection points identified manually by the tester.

## Getting started
```bash
pip install -r requirements.txt

python injector.py
```
