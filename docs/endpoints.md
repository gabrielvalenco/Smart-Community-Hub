# Smart Community Hub API Endpoints

This document provides detailed information about the RESTful API endpoints available in the Smart Community Hub application.

## Authentication

Most endpoints require authentication. The API uses token-based authentication.

## API Base URL

All API endpoints are prefixed with `/api/`.

## Endpoints

### Users

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/api/users/` | GET | List all users | Required (Admin only) |
| `/api/users/` | POST | Create a new user | Not required |
| `/api/users/{id}/` | GET | Retrieve user details | Required (Owner or Admin) |
| `/api/users/{id}/` | PUT | Update all user fields | Required (Owner or Admin) |
| `/api/users/{id}/` | PATCH | Partially update user | Required (Owner or Admin) |
| `/api/users/{id}/` | DELETE | Delete a user | Required (Owner or Admin) |
| `/api/users/{id}/attend_event/` | POST | Register user for an event | Required (Owner or Admin) |

#### Request Body (POST/PUT)

```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe",
  "address": "123 Main St",
  "phone_number": "555-123-4567",
  "bio": "Community member since 2020"
}
```

### Service Providers

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/api/providers/` | GET | List all service providers | Not required |
| `/api/providers/` | POST | Create a new service provider | Required |
| `/api/providers/{id}/` | GET | Retrieve provider details | Not required |
| `/api/providers/{id}/` | PUT | Update all provider fields | Required (Owner or Admin) |
| `/api/providers/{id}/` | PATCH | Partially update provider | Required (Owner or Admin) |
| `/api/providers/{id}/` | DELETE | Delete a provider | Required (Owner or Admin) |

#### Request Body (POST/PUT)

```json
{
  "user_id": 1,
  "business_name": "Quick Fix Plumbing",
  "service_type": "Plumbing",
  "description": "Professional plumbing services for all your needs",
  "hourly_rate": "45.00",
  "is_available": true
}
```

### Community Events

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/api/events/` | GET | List all events | Not required |
| `/api/events/` | POST | Create a new event | Required |
| `/api/events/{id}/` | GET | Retrieve event details | Not required |
| `/api/events/{id}/` | PUT | Update all event fields | Required (Organizer or Admin) |
| `/api/events/{id}/` | PATCH | Partially update event | Required (Organizer or Admin) |
| `/api/events/{id}/` | DELETE | Delete an event | Required (Organizer or Admin) |
| `/api/events/{id}/register/` | POST | Register for an event | Required |
| `/api/events/{id}/unregister/` | POST | Unregister from an event | Required |

#### Request Body (POST/PUT)

```json
{
  "title": "Community Cleanup Day",
  "description": "Join us for a day of cleaning up our neighborhood parks",
  "organizer_id": 1,
  "location": "Central Park",
  "start_date": "2025-05-15T09:00:00Z",
  "end_date": "2025-05-15T12:00:00Z",
  "max_attendees": 50,
  "is_free": true,
  "fee": null
}
```

### Resources

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/api/resources/` | GET | List all resources | Not required |
| `/api/resources/` | POST | Create a new resource | Required (Admin only) |
| `/api/resources/{id}/` | GET | Retrieve resource details | Not required |
| `/api/resources/{id}/` | PUT | Update all resource fields | Required (Admin only) |
| `/api/resources/{id}/` | PATCH | Partially update resource | Required (Admin only) |
| `/api/resources/{id}/` | DELETE | Delete a resource | Required (Admin only) |

#### Request Body (POST/PUT)

```json
{
  "name": "Community Center Meeting Room",
  "description": "Large meeting room with projector and seating for 30 people",
  "category": "Space",
  "location": "Community Center",
  "is_available": true,
  "hourly_rate": "25.00"
}
```

### Bookings

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/api/bookings/` | GET | List user's bookings | Required |
| `/api/bookings/` | POST | Create a new booking | Required |
| `/api/bookings/{id}/` | GET | Retrieve booking details | Required (Owner or Admin) |
| `/api/bookings/{id}/` | PUT | Update all booking fields | Required (Owner or Admin) |
| `/api/bookings/{id}/` | PATCH | Partially update booking | Required (Owner or Admin) |
| `/api/bookings/{id}/` | DELETE | Delete a booking | Required (Owner or Admin) |
| `/api/bookings/{id}/cancel/` | POST | Cancel a booking | Required (Owner or Admin) |

#### Request Body (POST/PUT)

```json
{
  "user_id": 1,
  "resource_id": 1,
  "start_time": "2025-05-10T14:00:00Z",
  "end_time": "2025-05-10T16:00:00Z",
  "notes": "Team meeting for project planning"
}
```

### Reviews

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/api/reviews/` | GET | List all reviews | Not required |
| `/api/reviews/` | POST | Create a new review | Required |
| `/api/reviews/{id}/` | GET | Retrieve review details | Not required |
| `/api/reviews/{id}/` | PUT | Update all review fields | Required (Owner or Admin) |
| `/api/reviews/{id}/` | PATCH | Partially update review | Required (Owner or Admin) |
| `/api/reviews/{id}/` | DELETE | Delete a review | Required (Owner or Admin) |

#### Request Body (POST/PUT)

```json
{
  "user_id": 1,
  "service_provider_id": 1,  // Either service_provider_id or event_id must be provided, not both
  "event_id": null,
  "rating": 5,
  "comment": "Excellent service, very professional and prompt!"
}
```

## Query Parameters

Most list endpoints support the following query parameters:

- `search`: Search for items matching the query
- Filtering by model fields (e.g., `?is_free=true` for events)

## Status Codes

The API returns the following status codes:

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Request successful, no content to return
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## API Documentation

Interactive API documentation is available at:

- Swagger UI: `/api/swagger/`
- ReDoc: `/api/redoc/`
