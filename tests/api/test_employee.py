def _payload(email="new_employee@test.com"):
    return {
        "first_name": "New",
        "last_name": "Employee",
        "email": email,
        "password": "Test@1234",
    }

# POST /employees

def test_create_employee_success(client, office_admin_headers, office):
    resp = client.post("/employees", json=_payload(), headers=office_admin_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "new_employee@test.com"
    assert body["office_id"] == office.office_id


def test_create_employee_duplicate_email(client, office_admin_headers, employee_user):
    resp = client.post(
        "/employees", json=_payload(email=employee_user.email), headers=office_admin_headers
    )
    assert resp.status_code == 409


def test_create_employee_rejects_super_admin(client, super_admin_headers):
    resp = client.post("/employees", json=_payload(), headers=super_admin_headers)
    assert resp.status_code == 403


def test_create_employee_rejects_employee(client, employee_headers):
    resp = client.post("/employees", json=_payload(), headers=employee_headers)
    assert resp.status_code == 403


# GET /employees  and  GET /employees/{user_id}   office isolation

def test_get_all_employees_is_scoped_to_own_office(
    client, office_admin_headers, other_office_admin_headers, employee_user
):
    # employee_user belongs to office_admin_headers' office.
    other_resp = client.post(
        "/employees",
        json=_payload(email="other_office_employee@test.com"),
        headers=other_office_admin_headers,
    )
    assert other_resp.status_code == 201
    other_employee_id = other_resp.json()["user_id"]

    resp = client.get("/employees", headers=office_admin_headers)
    assert resp.status_code == 200
    ids = [e["user_id"] for e in resp.json()]
    assert employee_user.user_id in ids
    assert other_employee_id not in ids


def test_get_employee_by_id_success(client, office_admin_headers, employee_user):
    resp = client.get(f"/employees/{employee_user.user_id}", headers=office_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["user_id"] == employee_user.user_id


def test_get_employee_by_id_not_found(client, office_admin_headers):
    resp = client.get("/employees/999999", headers=office_admin_headers)
    assert resp.status_code == 404


def test_get_employee_by_id_cross_office_is_not_found(
    client, office_admin_headers, other_office_admin_headers
):
    other_resp = client.post(
        "/employees",
        json=_payload(email="other_office_employee2@test.com"),
        headers=other_office_admin_headers,
    )
    other_employee_id = other_resp.json()["user_id"]

    resp = client.get(f"/employees/{other_employee_id}", headers=office_admin_headers)
    assert resp.status_code == 404


# PUT /employees/{user_id}


def test_update_employee_success(client, office_admin_headers, employee_user):
    resp = client.put(
        f"/employees/{employee_user.user_id}",
        json={"first_name": "Updated"},
        headers=office_admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["first_name"] == "Updated"


def test_update_employee_duplicate_email(
    client, office_admin_headers, employee_user, super_admin_user
):
    resp = client.put(
        f"/employees/{employee_user.user_id}",
        json={"email": super_admin_user.email},
        headers=office_admin_headers,
    )
    assert resp.status_code == 409

# DELETE /employees/{user_id}

def test_delete_employee_success(client, office_admin_headers, employee_user):
    resp = client.delete(f"/employees/{employee_user.user_id}", headers=office_admin_headers)
    assert resp.status_code == 200

    follow_up = client.get(f"/employees/{employee_user.user_id}", headers=office_admin_headers)
    assert follow_up.status_code == 404


def test_delete_employee_not_found(client, office_admin_headers):
    resp = client.delete("/employees/999999", headers=office_admin_headers)
    assert resp.status_code == 404
