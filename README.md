# QR Check-In Django App

## Steps to Run:
1. Create virtual environment and install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
3. Load attendees from CSV:
   ```bash
   python manage.py load_csv attendees.csv
   ```
4. Start server:
   ```bash
   conda activate e2s
   python manage.py runserver
   ```
5. Open browser at http://127.0.0.1:8000

## Features:
- QR code scanning using html5-qrcode
- CSV upload via management command
- Simple UI for check-in

