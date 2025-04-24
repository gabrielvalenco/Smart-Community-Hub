# Smart Community Hub API

A RESTful API built with Django and Django REST Framework to manage shared resources and services within a small community. This project supports CRUD operations across 5 interconnected tables and ensures data integrity through model relationships and validations.

## 🌐 Features

- 📅 Event scheduling and participation
- 🛠️ Local service provider directory
- 🧾 Resource booking system (e.g., coworking spaces, bikes, tools)
- 🗣️ Community user management
- 💬 User-to-user service reviews

## 📦 Technologies

- Python
- Django
- Django REST Framework
- MySQL
- Swagger for API documentation (recommended)

## 🧱 Database Models Overview

1. **User**: Residents of the community.
2. **ServiceProvider**: Local professionals offering services (e.g., tutors, electricians).
3. **CommunityEvent**: Events organized by or for residents.
4. **Booking**: Reservations for shared resources.
5. **Review**: Feedback on services or events.

### 🔗 Relationships

- `ServiceProvider` → `User` (One-to-One)
- `Review` → `User` & `ServiceProvider` (ForeignKey)
- `Booking` → `User` & `Resource`
- `CommunityEvent` ↔ `User` (Many-to-Many: attendees)

## 🔌 API Endpoints (RESTful)

| Endpoint                     | Method | Description                    |
|-----------------------------|--------|--------------------------------|
| `/users/`                   | GET/POST | List or create users          |
| `/users/<id>/`              | PUT/PATCH/DELETE | Update or delete user |
| `/providers/`               | GET/POST | List or create providers      |
| `/events/`                  | GET/POST | Manage community events       |
| `/bookings/`                | GET/POST | Manage resource bookings      |
| `/reviews/`                 | GET/POST | Manage service reviews        |

Full documentation can be found in [docs/endpoints.md](./docs/endpoints.md).

## 🧪 Testing

Use Postman or Insomnia to test all endpoints (CRUD). Be sure to test:
- Deletion cascading (e.g., deleting a user affects bookings)
- Unique validations (e.g., no duplicate reviews by the same user)
- Required fields enforcement

## 🔒 Validations

Implemented at both model and serializer levels, including:
- Field length and format checks
- Unique constraints (e.g., one review per user/provider pair)
- Numerical range validations (e.g., rating scores from 1 to 5)

## 🚧 Setup

```bash
git clone https://github.com/yourusername/smart-community-hub.git
cd smart-community-hub/backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
