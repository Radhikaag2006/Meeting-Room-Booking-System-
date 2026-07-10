def _payload(room_name="Room A", capacity=10, floor=1):
    return {"room_name": room_name, "capacity": capacity, "floor": floor}



# POST /meeting-rooms

def test_create_room_success(client, office_admin_headers, office):
    resp = client.post("/meeting-rooms", json=_payload(), headers=office_admin_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["room_name"] == "Room A"
    assert body["office_id"] == office.office_id


def test_create_room_duplicate_name(client, office_admin_headers):
    client.post("/meeting-rooms", json=_payload(), headers=office_admin_headers)
    resp = client.post("/meeting-rooms", json=_payload(), headers=office_admin_headers)
    assert resp.status_code == 409


def test_create_room_invalid_capacity(client, office_admin_headers):
    resp = client.post(
        "/meeting-rooms", json=_payload(capacity=0), headers=office_admin_headers
    )
    assert resp.status_code == 400


def test_create_room_invalid_floor(client, office_admin_headers):
    resp = client.post(
        "/meeting-rooms", json=_payload(floor=-1), headers=office_admin_headers
    )
    assert resp.status_code == 400


def test_create_room_rejects_super_admin(client, super_admin_headers):
    resp = client.post("/meeting-rooms", json=_payload(), headers=super_admin_headers)
    assert resp.status_code == 403


def test_create_room_rejects_employee(client, employee_headers):
    resp = client.post("/meeting-rooms", json=_payload(), headers=employee_headers)
    assert resp.status_code == 403


# GET /meeting-rooms  and  GET /meeting-rooms/{room_id}


def test_get_all_rooms_is_scoped_to_own_office(
    client, office_admin_headers, other_office_admin_headers
):
    client.post("/meeting-rooms", json=_payload(), headers=office_admin_headers)
    other_resp = client.post(
        "/meeting-rooms", json=_payload(room_name="Other Room"), headers=other_office_admin_headers
    )
    other_room_id = other_resp.json()["room_id"]

    resp = client.get("/meeting-rooms", headers=office_admin_headers)
    assert resp.status_code == 200
    ids = [r["room_id"] for r in resp.json()]
    assert other_room_id not in ids


def test_get_room_by_id_success(client, office_admin_headers):
    create_resp = client.post("/meeting-rooms", json=_payload(), headers=office_admin_headers)
    room_id = create_resp.json()["room_id"]

    resp = client.get(f"/meeting-rooms/{room_id}", headers=office_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["room_id"] == room_id


def test_get_room_by_id_not_found(client, office_admin_headers):
    resp = client.get("/meeting-rooms/999999", headers=office_admin_headers)
    assert resp.status_code == 404


def test_get_room_by_id_cross_office_is_forbidden(
    client, office_admin_headers, other_office_admin_headers
):
    other_resp = client.post(
        "/meeting-rooms", json=_payload(), headers=other_office_admin_headers
    )
    other_room_id = other_resp.json()["room_id"]

    resp = client.get(f"/meeting-rooms/{other_room_id}", headers=office_admin_headers)
    assert resp.status_code == 403


# PUT /meeting-rooms/{room_id}

def test_update_room_success(client, office_admin_headers):
    create_resp = client.post("/meeting-rooms", json=_payload(), headers=office_admin_headers)
    room_id = create_resp.json()["room_id"]

    resp = client.put(
        f"/meeting-rooms/{room_id}", json={"capacity": 25}, headers=office_admin_headers
    )
    assert resp.status_code == 200
    assert resp.json()["capacity"] == 25


def test_update_room_invalid_capacity(client, office_admin_headers):
    create_resp = client.post("/meeting-rooms", json=_payload(), headers=office_admin_headers)
    room_id = create_resp.json()["room_id"]

    resp = client.put(
        f"/meeting-rooms/{room_id}", json={"capacity": 0}, headers=office_admin_headers
    )
    assert resp.status_code == 400


def test_update_room_duplicate_name(client, office_admin_headers):
    client.post("/meeting-rooms", json=_payload(room_name="Room A"), headers=office_admin_headers)
    room_b = client.post(
        "/meeting-rooms", json=_payload(room_name="Room B"), headers=office_admin_headers
    ).json()

    resp = client.put(
        f"/meeting-rooms/{room_b['room_id']}",
        json={"room_name": "Room A"},
        headers=office_admin_headers,
    )
    assert resp.status_code == 409

# DELETE /meeting-rooms/{room_id}

def test_delete_room_success(client, office_admin_headers):
    create_resp = client.post("/meeting-rooms", json=_payload(), headers=office_admin_headers)
    room_id = create_resp.json()["room_id"]

    resp = client.delete(f"/meeting-rooms/{room_id}", headers=office_admin_headers)
    assert resp.status_code == 200

    follow_up = client.get(f"/meeting-rooms/{room_id}", headers=office_admin_headers)
    assert follow_up.status_code == 404


def test_delete_room_cross_office_is_forbidden(
    client, office_admin_headers, other_office_admin_headers
):
    other_resp = client.post(
        "/meeting-rooms", json=_payload(), headers=other_office_admin_headers
    )
    other_room_id = other_resp.json()["room_id"]

    resp = client.delete(f"/meeting-rooms/{other_room_id}", headers=office_admin_headers)
    assert resp.status_code == 403
