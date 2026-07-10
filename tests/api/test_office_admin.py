def _payload(office_id, email="new_office_admin@test.com"):
    return {
        "first_name": "New",
        "last_name": "Admin",
        "email": email,
        "password": "Test@1234",
        "office_id": office_id,
    }


# POST /office-admins


def test_create_office_admin_success(client, super_admin_headers, office):
    resp = client.post(
        "/office-admins", json=_payload(office.office_id), headers=super_admin_headers
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "new_office_admin@test.com"
    assert body["office_id"] == office.office_id


def test_create_office_admin_office_not_found(client, super_admin_headers):
    resp = client.post(
        "/office-admins", json=_payload(999999), headers=super_admin_headers
    )
    assert resp.status_code == 404


def test_create_office_admin_office_already_has_admin(
    client, super_admin_headers, office, office_admin_user
):
    resp = client.post(
        "/office-admins", json=_payload(office.office_id), headers=super_admin_headers
    )
    assert resp.status_code == 409


def test_create_office_admin_duplicate_email(
    client, super_admin_headers, office, other_office, office_admin_user
):
    resp = client.post(
        "/office-admins",
        json=_payload(other_office.office_id, email=office_admin_user.email),
        headers=super_admin_headers,
    )
    assert resp.status_code == 409


def test_create_office_admin_rejects_office_admin(client, office_admin_headers, office):
    resp = client.post(
        "/office-admins", json=_payload(office.office_id), headers=office_admin_headers
    )
    assert resp.status_code == 403


def test_create_office_admin_rejects_employee(client, employee_headers, office):
    resp = client.post(
        "/office-admins", json=_payload(office.office_id), headers=employee_headers
    )
    assert resp.status_code == 403


# GET /office-admins  and  GET /office-admins/{user_id}


def test_get_all_office_admins(client, super_admin_headers, office_admin_user):
    resp = client.get("/office-admins", headers=super_admin_headers)
    assert resp.status_code == 200
    ids = [a["user_id"] for a in resp.json()]
    assert office_admin_user.user_id in ids


def test_get_office_admin_by_id_success(client, super_admin_headers, office_admin_user):
    resp = client.get(
        f"/office-admins/{office_admin_user.user_id}", headers=super_admin_headers
    )
    assert resp.status_code == 200
    assert resp.json()["user_id"] == office_admin_user.user_id


def test_get_office_admin_by_id_not_found(client, super_admin_headers):
    resp = client.get("/office-admins/999999", headers=super_admin_headers)
    assert resp.status_code == 404


def test_get_office_admin_by_id_rejects_non_admin_user(
    client, super_admin_headers, employee_user
):
    # employee_user exists but is not an OFFICE_ADMIN, so it should look "not found"
    resp = client.get(
        f"/office-admins/{employee_user.user_id}", headers=super_admin_headers
    )
    assert resp.status_code == 404



# PUT /office-admins/{user_id}


def test_update_office_admin_success(client, super_admin_headers, office_admin_user):
    resp = client.put(
        f"/office-admins/{office_admin_user.user_id}",
        json={"first_name": "Updated"},
        headers=super_admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["first_name"] == "Updated"


def test_update_office_admin_duplicate_email(
    client, super_admin_headers, office_admin_user, other_office_admin_user
):
    resp = client.put(
        f"/office-admins/{office_admin_user.user_id}",
        json={"email": other_office_admin_user.email},
        headers=super_admin_headers,
    )
    assert resp.status_code == 409


def test_update_office_admin_not_found(client, super_admin_headers):
    resp = client.put(
        "/office-admins/999999",
        json={"first_name": "Nobody"},
        headers=super_admin_headers,
    )
    assert resp.status_code == 404


# DELETE /office-admins/{user_id}


def test_delete_office_admin_success(client, super_admin_headers, office_admin_user):
    resp = client.delete(
        f"/office-admins/{office_admin_user.user_id}", headers=super_admin_headers
    )
    assert resp.status_code == 200

    follow_up = client.get(
        f"/office-admins/{office_admin_user.user_id}", headers=super_admin_headers
    )
    assert follow_up.status_code == 404


def test_delete_office_admin_not_found(client, super_admin_headers):
    resp = client.delete("/office-admins/999999", headers=super_admin_headers)
    assert resp.status_code == 404


def test_delete_office_admin_rejects_employee(client, employee_headers, office_admin_user):
    resp = client.delete(
        f"/office-admins/{office_admin_user.user_id}", headers=employee_headers
    )
    assert resp.status_code == 403
