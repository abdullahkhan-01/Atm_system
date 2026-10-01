# SmartATM - Python ATM System

A beginner-friendly, moderate-level ATM web application built using:

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript

## Features

1. ATM login using account number and PIN
2. Balance inquiry
3. Cash withdrawal
4. Cash deposit
5. Money transfer between demo accounts
6. Recent transaction history
7. SQLite database for persistent data
8. Responsive and clean interface
9. Indian names and ₹ currency

## Demo Accounts

| Name | Account Number | PIN | Starting Balance |
|---|---|---|---:|
| Aarav Sharma | 10010001 | 1234 | ₹25,000 |
| Priya Patil | 10010002 | 2345 | ₹18,500 |
| Rohan Deshmukh | 10010003 | 3456 | ₹42,000 |
| Ananya Kulkarni | 10010004 | 4567 | ₹12,750 |

## How to Run

### 1. Open the project folder

```bash
cd atm_system_project
```

### 2. Create a virtual environment (recommended)

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Mac/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Flask

```bash
pip install -r requirements.txt
```

### 4. Start the application

```bash
python app.py
```

### 5. Open in browser

Go to:

http://127.0.0.1:5000

The `atm.db` file is automatically created on first run.

## Important

This is an educational project. The PINs are intentionally stored as plain text to keep the project beginner-friendly. A real banking application would use secure password/PIN hashing, authentication controls, encryption, audit logging, rate limiting, and many additional security measures.
