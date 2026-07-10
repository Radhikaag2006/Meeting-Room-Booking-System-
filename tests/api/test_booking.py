from datetime import date, timedelta

import pytest

from app.core.security import hash_password
from app.models.meeting_room import MeetingRoom, RoomStatus
from app.models.user import User, UserRole, UserStatus
from tests.conftest import TEST_PASSWORD

TOMORROW = date.today() + timedelta(days=1)
YESTERDAY = date.today() - timedelta(days=1)


@pytest.fixture()
def meeting_room(db_session, office):
    room = MeetingRoom(
        office_id=office.office_id,
        room_name="Booking Room",
        capacity=3,
        floor=1,
        status=RoomStatus.ACTIVE,
    )
    db_session.add(room)
    db_session.commit()
    db_session.refresh(room)
    return room


@pytest.fixture()
def second_employee(db_session, office):
    user = User(
        first_name="Second",
        last_name="Employee",
        email="second_employee@test.com",
        password_hash=hash_password(TEST_PASSWORD),
        role=UserRole.EMPLOYEE,
        office_id=office.office_id,
        status=UserStatus.ACTIVE,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _booking_payload(
    room_id,
    attendees=None,
    meeting_date=TOMORROW,
    start_time="10:00:00",
    end_time="11:00:00",
    title="Standup",
):
    return {
        "meeting_title": title,
        "description": "desc",
        "room_id": room_id,
        "meeting_date": meeting_date.isoformat(),
        "start_time": start_time,
        "end_time": end_time,
        "attendees": attendees or [],
    }


# ---------------------------------------------------------------------------
# POST /bookings -- happy path + validation
# ---------------------------------------------------------------------------

def test_create_booking_happy_path(client, employee_headers, employee_user, meeting_room):
    resp = client.post(
        "/bookings", json=_booking_payload(meeting_room.room_id), headers=employee_headers
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["organizer_id"] == employee_user.user_id
    assert body["status"] == "SCHEDULED"


def test_create_booking_meeting_date_in_past(client, employee_headers, meeting_room):
    resp = client.post(
        "/bookings",
        json=_booking_payload(meeting_room.room_id, meeting_date=YESTERDAY),
        headers=employee_headers,
    )
    assert resp.status_code == 400


def test_create_booking_duplicate_attendees(
    client, employee_headers, meeting_room, second_employee
):
    resp = client.post(
        "/bookings",
        json=_booking_payload(
            meeting_room.room_id, attendees=[second_employee.user_id, second_employee.user_id]
        ),
        headers=employee_headers,
    )
    assert resp.status_code == 400


def test_create_booking_start_after_end(client, employee_headers, meeting_room):
    resp = client.post(
        "/bookings",
        json=_booking_payload(meeting_room.room_id, start_time="11:00:00", end_time="10:00:00"),
        headers=employee_headers,
    )
    assert resp.status_code == 400


def test_create_booking_room_not_found(client, employee_headers):
    resp = client.post(
        "/bookings", json=_booking_payload(999999), headers=employee_headers
    )
    assert resp.status_code == 404


def test_create_booking_room_inactive(client, employee_headers, db_session, office):
    room = MeetingRoom(
        office_id=office.office_id,
        room_name="Inactive Room",
        capacity=3,
        floor=1,
        status=RoomStatus.INACTIVE,
    )
    db_session.add(room)
    db_session.commit()
    db_session.refresh(room)

    resp = client.post(
        "/bookings", json=_booking_payload(room.room_id), headers=employee_headers
    )
    assert resp.status_code == 400


def test_create_booking_room_other_office_forbidden(
    client, employee_headers, db_session, other_office
):
    room = MeetingRoom(
        office_id=other_office.office_id,
        room_name="Other Office Room",
        capacity=3,
        floor=1,
        status=RoomStatus.ACTIVE,
    )
    db_session.add(room)
    db_session.commit()
    db_session.refresh(room)

    resp = client.post(
        "/bookings", json=_booking_payload(room.room_id), headers=employee_headers
    )
    assert resp.status_code == 403


def test_create_booking_invited_user_not_found(client, employee_headers, meeting_room):
    resp = client.post(
        "/bookings",
        json=_booking_payload(meeting_room.room_id, attendees=[999999]),
        headers=employee_headers,
    )
    assert resp.status_code == 404


def test_create_booking_invited_user_not_employee(
    client, employee_headers, meeting_room, super_admin_user
):
    resp = client.post(
        "/bookings",
        json=_booking_payload(meeting_room.room_id, attendees=[super_admin_user.user_id]),
        headers=employee_headers,
    )
    assert resp.status_code == 400


def test_create_booking_invited_employee_inactive(
    client, employee_headers, meeting_room, db_session, office
):
    inactive_employee = User(
        first_name="Inactive",
        last_name="Employee",
        email="inactive_invitee@test.com",
        password_hash=hash_password(TEST_PASSWORD),
        role=UserRole.EMPLOYEE,
        office_id=office.office_id,
        status=UserStatus.INACTIVE,
    )
    db_session.add(inactive_employee)
    db_session.commit()
    db_session.refresh(inactive_employee)

    resp = client.post(
        "/bookings",
        json=_booking_payload(meeting_room.room_id, attendees=[inactive_employee.user_id]),
        headers=employee_headers,
    )
    assert resp.status_code == 400


def test_create_booking_invited_employee_other_office_forbidden(
    client, employee_headers, meeting_room, db_session, other_office
):
    other_office_employee = User(
        first_name="Other",
        last_name="Office Employee",
        email="other_office_invitee@test.com",
        password_hash=hash_password(TEST_PASSWORD),
        role=UserRole.EMPLOYEE,
        office_id=other_office.office_id,
        status=UserStatus.ACTIVE,
    )
    db_session.add(other_office_employee)
    db_session.commit()
    db_session.refresh(other_office_employee)

    resp = client.post(
        "/bookings",
        json=_booking_payload(meeting_room.room_id, attendees=[other_office_employee.user_id]),
        headers=employee_headers,
    )
    assert resp.status_code == 403


def test_create_booking_capacity_exceeded(
    client, employee_headers, db_session, office, second_employee
):
    small_room = MeetingRoom(
        office_id=office.office_id,
        room_name="Tiny Room",
        capacity=1,
        floor=1,
        status=RoomStatus.ACTIVE,
    )
    db_session.add(small_room)
    db_session.commit()
    db_session.refresh(small_room)

    resp = client.post(
        "/bookings",
        json=_booking_payload(small_room.room_id, attendees=[second_employee.user_id]),
        headers=employee_headers,
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# POST /bookings -- conflict detection (the core business rule)
# ---------------------------------------------------------------------------

def test_create_booking_overlapping_time_conflicts(client, employee_headers, meeting_room):
    first = client.post(
        "/bookings", json=_booking_payload(meeting_room.room_id), headers=employee_headers
    )
    assert first.status_code == 201

    second = client.post(
        "/bookings",
        json=_booking_payload(meeting_room.room_id, start_time="10:30:00", end_time="11:30:00"),
        headers=employee_headers,
    )
    assert second.status_code == 409


def test_create_booking_adjacent_times_both_succeed(client, employee_headers, meeting_room):
    first = client.post(
        "/bookings", json=_booking_payload(meeting_room.room_id), headers=employee_headers
    )
    assert first.status_code == 201

    second = client.post(
        "/bookings",
        json=_booking_payload(meeting_room.room_id, start_time="11:00:00", end_time="12:00:00"),
        headers=employee_headers,
    )
    assert second.status_code == 201


def test_cancelled_booking_does_not_block_rebooking(client, employee_headers, meeting_room):
    first = client.post(
        "/bookings", json=_booking_payload(meeting_room.room_id), headers=employee_headers
    )
    booking_id = first.json()["booking_id"]

    cancel_resp = client.patch(f"/bookings/{booking_id}/cancel", headers=employee_headers)
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELLED"

    rebook = client.post(
        "/bookings", json=_booking_payload(meeting_room.room_id), headers=employee_headers
    )
    assert rebook.status_code == 201


# ---------------------------------------------------------------------------
# GET /bookings/my-meetings
# ---------------------------------------------------------------------------

def test_get_my_bookings_includes_organizer_and_attendee(
    client, employee_headers, meeting_room, second_employee
):
    create_resp = client.post(
        "/bookings",
        json=_booking_payload(meeting_room.room_id, attendees=[second_employee.user_id]),
        headers=employee_headers,
    )
    booking_id = create_resp.json()["booking_id"]

    organizer_view = client.get("/bookings/my-meetings", headers=employee_headers)
    assert booking_id in [b["booking_id"] for b in organizer_view.json()]

    attendee_headers = _login(client, second_employee.email)
    attendee_view = client.get("/bookings/my-meetings", headers=attendee_headers)
    assert booking_id in [b["booking_id"] for b in attendee_view.json()]


def _login(client, email):
    resp = client.post("/auth/login", json={"email": email, "password": TEST_PASSWORD})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# GET /bookings/{booking_id}
# ---------------------------------------------------------------------------

def test_get_booking_by_id_organizer_can_view(client, employee_headers, meeting_room):
    create_resp = client.post(
        "/bookings", json=_booking_payload(meeting_room.room_id), headers=employee_headers
    )
    booking_id = create_resp.json()["booking_id"]

    resp = client.get(f"/bookings/{booking_id}", headers=employee_headers)
    assert resp.status_code == 200


def test_get_booking_by_id_attendee_can_view(
    client, employee_headers, meeting_room, second_employee
):
    create_resp = client.post(
        "/bookings",
        json=_booking_payload(meeting_room.room_id, attendees=[second_employee.user_id]),
        headers=employee_headers,
    )
    booking_id = create_resp.json()["booking_id"]

    attendee_headers = _login(client, second_employee.email)
    resp = client.get(f"/bookings/{booking_id}", headers=attendee_headers)
    assert resp.status_code == 200


def test_get_booking_by_id_unrelated_employee_forbidden(
    client, employee_headers, meeting_room, second_employee
):
    create_resp = client.post(
        "/bookings", json=_booking_payload(meeting_room.room_id), headers=employee_headers
    )
    booking_id = create_resp.json()["booking_id"]

    unrelated_headers = _login(client, second_employee.email)
    resp = client.get(f"/bookings/{booking_id}", headers=unrelated_headers)
    assert resp.status_code == 403


def test_get_booking_by_id_not_found(client, employee_headers):
    resp = client.get("/bookings/999999", headers=employee_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PUT /bookings/{booking_id}
# ---------------------------------------------------------------------------

def test_update_booking_organizer_can_update(client, employee_headers, meeting_room):
    create_resp = client.post(
        "/bookings", json=_booking_payload(meeting_room.room_id), headers=employee_headers
    )
    booking_id = create_resp.json()["booking_id"]

    resp = client.put(
        f"/bookings/{booking_id}",
        json={"meeting_title": "Renamed Meeting"},
        headers=employee_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["meeting_title"] == "Renamed Meeting"


def test_update_booking_non_organizer_forbidden(
    client, employee_headers, meeting_room, second_employee
):
    create_resp = client.post(
        "/bookings", json=_booking_payload(meeting_room.room_id), headers=employee_headers
    )
    booking_id = create_resp.json()["booking_id"]

    other_headers = _login(client, second_employee.email)
    resp = client.put(
        f"/bookings/{booking_id}",
        json={"meeting_title": "Hijacked"},
        headers=other_headers,
    )
    assert resp.status_code == 403


def test_update_booking_not_found(client, employee_headers):
    resp = client.put(
        "/bookings/999999", json={"meeting_title": "Nobody"}, headers=employee_headers
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /bookings/{booking_id}/cancel
# ---------------------------------------------------------------------------

def test_cancel_booking_non_organizer_forbidden(
    client, employee_headers, meeting_room, second_employee
):
    create_resp = client.post(
        "/bookings", json=_booking_payload(meeting_room.room_id), headers=employee_headers
    )
    booking_id = create_resp.json()["booking_id"]

    other_headers = _login(client, second_employee.email)
    resp = client.patch(f"/bookings/{booking_id}/cancel", headers=other_headers)
    assert resp.status_code == 403


def test_cancel_booking_not_found(client, employee_headers):
    resp = client.patch("/bookings/999999/cancel", headers=employee_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Role check on /bookings/*
# ---------------------------------------------------------------------------

def test_bookings_rejects_office_admin(client, office_admin_headers):
    resp = client.get("/bookings/my-meetings", headers=office_admin_headers)
    assert resp.status_code == 403


def test_bookings_rejects_super_admin(client, super_admin_headers):
    resp = client.get("/bookings/my-meetings", headers=super_admin_headers)
    assert resp.status_code == 403
