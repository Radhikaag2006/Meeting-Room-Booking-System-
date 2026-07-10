OFFICE_PAYLOAD = {
    "office_name": "New Office",
    "address": "1 New St",
    "city": "Newtown",
    "state": "CA",
    "country": "USA",
}


# POST /offices/


def test_create_office_success(client, super_admin_headers):
    resp = client.post("/offices/", json=OFFICE_PAYLOAD, headers=super_admin_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["office_name"] == OFFICE_PAYLOAD["office_name"]
    assert "office_id" in body


def test_create_office_duplicate_name(client, super_admin_headers, office):
    payload = {**OFFICE_PAYLOAD, "office_name": office.office_name}
    resp = client.post("/offices/", json=payload, headers=super_admin_headers)
    assert resp.status_code == 409


def test_create_office_rejects_office_admin(client, office_admin_headers):
    resp = client.post("/offices/", json=OFFICE_PAYLOAD, headers=office_admin_headers)
    assert resp.status_code == 403


def test_create_office_rejects_employee(client, employee_headers):
    resp = client.post("/offices/", json=OFFICE_PAYLOAD, headers=employee_headers)
    assert resp.status_code == 403


def test_create_office_rejects_unauthenticated(client):
    resp = client.post("/offices/", json=OFFICE_PAYLOAD)
    assert resp.status_code == 401


# GET /offices/  and  GET /offices/{office_id}


def test_get_all_offices(client, super_admin_headers, office):
    resp = client.get("/offices/", headers=super_admin_headers)
    assert resp.status_code == 200
    ids = [o["office_id"] for o in resp.json()]
    assert office.office_id in ids


def test_get_all_offices_rejects_employee(client, employee_headers):
    resp = client.get("/offices/", headers=employee_headers)
    assert resp.status_code == 403


def test_get_office_by_id_success(client, super_admin_headers, office):
    resp = client.get(f"/offices/{office.office_id}", headers=super_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["office_id"] == office.office_id


def test_get_office_by_id_not_found(client, super_admin_headers):
    resp = client.get("/offices/999999", headers=super_admin_headers)
    assert resp.status_code == 404



# PUT /offices/{office_id}


def test_update_office_success(client, super_admin_headers, office):
    resp = client.put(
        f"/offices/{office.office_id}",
        json={"office_name": "Renamed Office"},
        headers=super_admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["office_name"] == "Renamed Office"


def test_update_office_duplicate_name(client, super_admin_headers, office, other_office):
    resp = client.put(
        f"/offices/{office.office_id}",
        json={"office_name": other_office.office_name},
        headers=super_admin_headers,
    )
    assert resp.status_code == 409


def test_update_office_not_found(client, super_admin_headers):
    resp = client.put(
        "/offices/999999",
        json={"office_name": "Doesn't Matter"},
        headers=super_admin_headers,
    )
    assert resp.status_code == 404


def test_update_office_rejects_office_admin(client, office_admin_headers, office):
    resp = client.put(
        f"/offices/{office.office_id}",
        json={"office_name": "Renamed Office"},
        headers=office_admin_headers,
    )
    assert resp.status_code == 403


# DELETE /offices/{office_id}


def test_delete_office_success(client, super_admin_headers, office):
    resp = client.delete(f"/offices/{office.office_id}", headers=super_admin_headers)
    assert resp.status_code == 200

    follow_up = client.get(f"/offices/{office.office_id}", headers=super_admin_headers)
    assert follow_up.status_code == 404


def test_delete_office_not_found(client, super_admin_headers):
    resp = client.delete("/offices/999999", headers=super_admin_headers)
    assert resp.status_code == 404


def test_delete_office_rejects_employee(client, employee_headers, office):
    resp = client.delete(f"/offices/{office.office_id}", headers=employee_headers)
    assert resp.status_code == 403
