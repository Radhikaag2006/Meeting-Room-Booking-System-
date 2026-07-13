import { requireRole } from "../../guard.js";
import { initLayout } from "../../layout.js";
import { apiRequest } from "../../api.js";
import { renderTable } from "../../ui/table.js";
import { formModal, confirmModal } from "../../ui/modal.js";
import { showToast } from "../../ui/toast.js";
import { renderErrorState } from "../../ui/error-state.js";
import { escapeHtml } from "../../utils.js";

const STATUS_OPTIONS = [
  { value: "ACTIVE", label: "Active" },
  { value: "INACTIVE", label: "Inactive" },
];

const ROOM_FIELDS = [
  { name: "room_name", label: "Room Name" },
  { name: "capacity", label: "Capacity", type: "number", min: 1 },
  { name: "floor", label: "Floor", type: "number", min: 0 },
];

const EDIT_ROOM_FIELDS = [
  ...ROOM_FIELDS,
  { name: "status", label: "Status", type: "select", options: STATUS_OPTIONS },
];

const tableContainer = document.getElementById("table-container");

async function loadRooms() {
  const rooms = await apiRequest("/meeting-rooms");
  renderTable(tableContainer, {
    columns: [
      { label: "Room Name", render: (r) => escapeHtml(r.room_name) },
      { label: "Capacity", render: (r) => escapeHtml(r.capacity) },
      { label: "Floor", render: (r) => escapeHtml(r.floor) },
      {
        label: "Status",
        render: (r) =>
          r.status === "ACTIVE"
            ? '<span class="badge badge-success">Active</span>'
            : '<span class="badge badge-neutral">Inactive</span>',
      },
      {
        label: "",
        render: (r) => `
          <div class="row-actions">
            <button type="button" class="btn btn-secondary" data-action="edit" data-id="${r.room_id}">Edit</button>
            <button type="button" class="btn btn-danger" data-action="delete" data-id="${r.room_id}">Delete</button>
          </div>
        `,
      },
    ],
    rows: rooms,
    emptyMessage: "No meeting rooms yet. Create the first one to get started.",
  });

  tableContainer.querySelectorAll('[data-action="edit"]').forEach((btn) => {
    btn.addEventListener("click", () => editRoom(Number(btn.dataset.id), rooms));
  });
  tableContainer.querySelectorAll('[data-action="delete"]').forEach((btn) => {
    btn.addEventListener("click", () => deleteRoom(Number(btn.dataset.id), rooms));
  });
}

async function createRoom() {
  const values = await formModal({ title: "New Meeting Room", fields: ROOM_FIELDS, submitLabel: "Create" });
  if (!values) return;

  try {
    await apiRequest("/meeting-rooms", {
      method: "POST",
      body: { room_name: values.room_name, capacity: Number(values.capacity), floor: Number(values.floor) },
    });
    showToast("Meeting room created", "success");
    await loadRooms();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function editRoom(roomId, rooms) {
  const room = rooms.find((r) => r.room_id === roomId);
  const values = await formModal({
    title: "Edit Meeting Room",
    fields: EDIT_ROOM_FIELDS,
    initialValues: room,
    submitLabel: "Save",
  });
  if (!values) return;

  try {
    await apiRequest(`/meeting-rooms/${roomId}`, {
      method: "PUT",
      body: {
        room_name: values.room_name,
        capacity: Number(values.capacity),
        floor: Number(values.floor),
        status: values.status,
      },
    });
    showToast("Meeting room updated", "success");
    await loadRooms();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function deleteRoom(roomId, rooms) {
  const room = rooms.find((r) => r.room_id === roomId);
  const confirmed = await confirmModal({
    title: "Delete meeting room",
    message: `Delete "${room.room_name}"? This cannot be undone.`,
    confirmLabel: "Delete",
  });
  if (!confirmed) return;

  try {
    await apiRequest(`/meeting-rooms/${roomId}`, { method: "DELETE" });
    showToast("Meeting room deleted", "success");
    await loadRooms();
  } catch (err) {
    showToast(err.message, "error");
  }
}

const user = await requireRole("OFFICE_ADMIN");
if (user) {
  initLayout({ role: "OFFICE_ADMIN", user });
  document.getElementById("new-room-btn").addEventListener("click", createRoom);
  try {
    await loadRooms();
  } catch (err) {
    showToast(err.message, "error");
    renderErrorState(tableContainer, "Couldn't load meeting rooms.", loadRooms);
  }
}
