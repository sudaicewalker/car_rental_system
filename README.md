# EaseDrive — Car Rental Management System

A web-based car rental and fleet management platform developed with Django and Bootstrap 5. The application provides dedicated portals for system administrators and customers to manage vehicle hiring, reservations, driver allocations, billing, and real-time revenue analytics.

---

##  Group Members

| No. | Full Name | Registration Number | Role / Contribution |
| :---: | :--- | :---: | :--- |
| **1** | **Tamuzadde Suadice** | `224-063011-29270` | Group Member |
| **2** | **Janke Kaba Koita** | `244-063011-29154` | Group Member |

---

##  Project Overview

**EaseDrive** streamlines vehicle rental operations for car rental businesses. It handles customer accounts, fleet status updates, booking workflows, driver assignments, payment tracking, and financial analytics from an interactive administrative dashboard.

###  Key Features

####  Administrative Portal
- **Fleet Management:** Add, update, and remove vehicles with images, registration plates, rental rates, and real-time status (`Available`, `Rented`, `Maintenance`).
- **Hiring & Reservations:** Review all customer booking requests, assign available drivers, and confirm rentals.
- **Driver Management:** Maintain driver records, contact info, licenses, salaries, and birth dates.
- **Billing & Payments:** Record and manage customer transactions across Bank, Mobile Money, and Cash methods.
- **Revenue & Fleet Analytics:** Visual summaries of collected revenue, pending invoices, top rented vehicles, and customer expenditure breakdown.

####  Customer Portal
- **Self-Service Registration & Login:** Create an account and manage rental profile.
- **Browse Fleet:** View available vehicles, specifications, daily rates, and photos.
- **Online Booking:** Select pickup and return dates with optional chauffeur (with driver) or self-driving packages.
- **My Bookings & Payments:** Track booking approvals and submit payments directly.

---

##  Technology Stack

- **Backend:** Python 3.14+, Django 5.x
- **Frontend:** HTML5, CSS3, Bootstrap 5.3, Font Awesome 6.5, Kaiadmin Dashboard Template
- **Forms & Formatting:** Django Crispy Forms (Bootstrap 5 pack)
- **Database:** SQLite3 (Default relational database)
- **Image Handling:** Pillow (ImageField upload to media directory)

---

##  Getting Started & Installation

### Prerequisites
- Python 3.10 or higher installed
- `pip` package manager

### 1. Clone or Download Repository
Open your terminal or PowerShell in the project directory:
```bash
cd c:\Users\kabak\Desktop\final
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install django django-crispy-forms crispy-bootstrap5 pillow
```

### 4. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create an Administrator Account
```bash
python manage.py createsuperuser
```

### 6. Start the Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

---

##  Project Structure

```text
final/
├── carapplication/             # Core Django application
│   ├── migrations/             # Database migration files
│   ├── templates/              # HTML templates (Admin & Customer portals)
│   │   ├── base.html           # Main administrative layout & navigation
│   │   ├── index.html          # Homepage & fleet showcase
│   │   ├── add_car.html        # Fleet management & vehicle additions
│   │   ├── add_hiring.html     # Rental booking records & driver assignment
│   │   ├── add_driver.html     # Driver registration & management
│   │   ├── add_payment.html    # Billing & transaction history
│   │   ├── add_customer.html   # Customer database
│   │   ├── admin_analytics.html# Revenue & performance analytics
│   │   ├── customer_book.html  # Customer vehicle booking
│   │   └── my_bookings.html    # Customer booking history & payments
│   ├── admin.py                # Django admin registration
│   ├── forms.py                # Form definitions & validation
│   ├── models.py               # Data models (Car, Customer, Driver, Hiring, Payment)
│   └── views.py                # Application controllers and views
├── carweb/                     # Project configuration directory
│   ├── settings.py             # Django settings
│   ├── urls.py                 # URL routing configuration
│   └── wsgi.py                 # WSGI entry point
├── media/                      # Uploaded car vehicle images
├── static/                     # CSS, JS, and vendor asset libraries
├── db.sqlite3                  # Relational database file
├── manage.py                   # Django CLI management utility
└── README.md                   # Project documentation
```

---

##  License & Academic Note

This project is submitted as an academic course project for car rental operations and management. All rights reserved &copy; 2026.
