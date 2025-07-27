
# MedScheduler

**MedScheduler** is a modern, robust web platform for scheduling and managing medical appointments — designed for clinics that want to offer a complete, secure and user-friendly experience to patients, doctors, and admins.

---

## 🚀 About

MedScheduler is a Django + PostgreSQL project built with best practices for real-world clinic workflows: user management, appointments, notifications, audit trail, and even AI-powered triage.  
This project is designed to be extensible, well-tested, and easily adaptable to any health organization.

---

## 📋 Features (Scope)

### User Management
- Custom user model: patient, doctor, admin roles
- Registration, authentication, and profile editing
- Password reset, password change and delete account (with password confirmation)
- Admin dashboard: user list, filtering, edit, activate/deactivate, pagination

### Specialties Management
- Admin CRUD of medical specialties (create, edit, delete)
- Doctor profile linked to specialties (many-to-many)
- Only active specialties available for booking

### Medical Appointment Scheduling
- Patients book appointments by selecting doctor, specialty, date & time
- Smart conflict prevention (no double bookings for same doctor & time)
- Dynamic doctor selection by specialty (AJAX)
- 10+ professional validations: conflicts, working hours, weekends, holidays, limits per patient, per day, doctor availability, etc.
- Reason for booking: patient can describe symptoms/motive at scheduling

### AI-powered Triage (upcoming)
- Endpoint to receive symptoms and suggest the ideal medical specialty via AI

### Consultation History
- Patients and doctors can view past, upcoming and cancelled appointments (with filters)
- CSV export for patients/doctors

### Smart Cancellation/Rebooking Rules
- Cancel up to 24h before, up to 2 rebookings per week

### Notifications (Simulated)
- Appointment reminders via simulated notifications

### Feedback/Review (upcoming)
- Patient rates their appointment (1-5 stars + comments)

### Automated Testing & Documentation
- Unit and integration tests
- Interactive API docs (Swagger/OpenAPI)

### DevOps & Deploy
- Docker/Docker Compose support
- Ready for cloud deployment (Render, Railway, etc.)

---

## 🏗️ Features Done

- User registration and login (patients/doctors)
- Profile management and role-based access
- Password reset, change, and delete account (LGPD-ready)
- Admin dashboard for user management (list, filter, activate/deactivate, edit)
- CRUD of specialties (admin only)
- Specialty-doctor relationship (many-to-many)
- Responsive interface with Tailwind CSS (via CDN)
- Medical appointment scheduling with dynamic doctor filtering by specialty (AJAX)
- 10 essential validations for safe, real-world booking (conflict, working hours, weekends, holidays, limits per patient, doctor availability, specialty consistency, etc.)
- Secure, DRY and extensible backend

---

## 🛣️ Roadmap

- Specialties CRUD (admin)
- Appointment scheduling
- Conflict checking logic
- Reverse search of doctors
- AI triage endpoint
- Appointment history & export
- Smart cancellation & rebooking
- Notifications (simulated)
- Feedback post-consultation
- Automated tests and CI/CD
- API docs and further polish

---

## 🖥️ Tech Stack

- **Backend:** Django (Python 3.10+)
- **Database:** PostgreSQL
- **Frontend:** Django Templates + Tailwind CSS (CDN)
- **Testing:** pytest
- **Documentation:** Swagger/OpenAPI (drf-yasg)
- **DevOps:** Docker, Docker Compose

---

## 📦 Setup & Installation

```bash
git clone https://github.com/yourusername/medscheduler.git
cd medscheduler
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # update settings as needed
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Access at [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📝 Usage

- Register as patient or doctor.
- Admins manage users at `/users/` or via `/admin/`.
- Password flows and delete account are available from login/profile.
- Specialties managed only via admin.
- Appointment history, filters, and CSV export for patients/doctors.
- Bulk actions and export in admin.
- More features coming soon (see Roadmap!).

---

## 👤 Roles

- **Admin:** manage users, specialties, appointments (full access)
- **Doctor/Patient:** can update their own profile, book/see appointments, delete account, export history

---

## 📅 Project Status

- **User management:** Complete
- **Specialties management:** Complete
- **Appointment scheduling:** Core booking, dynamic filtering, and all key validations implemented
- **Admin:** Complete (bulk actions, filters, export, dashboard)
- **Next:** Feedback, notifications, AI triage, testing, deployment

---

## 🏥 License

MIT License.

---

## ✨ Author

- [Rafael Aquino](https://github.com/rafael-acerqueira) – Senior Django Developer

---

*Project built for modern healthtech scenarios, learning and production readiness! Contributions and feedback welcome.*