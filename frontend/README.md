# MRBS Frontend

Vanilla HTML/CSS/JS multi-page app that talks to the FastAPI backend in `../app`.
No build step, no framework.

## Running locally

1. Start the backend (from the repo root, with the venv active):
   ```
   uvicorn app.main:app --reload
   ```
   It listens on `http://localhost:8000`.

2. Serve this folder as a static site:
   ```
   cd frontend
   python -m http.server 5500
   ```
   Then open `http://localhost:5500/index.html`.

   The backend's CORS config (`app/main.py`) only allows
   `http://localhost:5500` / `http://127.0.0.1:5500` — if you serve the
   frontend on a different port, add it there too.

3. If the API isn't on `localhost:8000`, update `API_BASE_URL` in
   `assets/js/config.js`.

## Layout

- `index.html` — login (entry point)
- `super-admin/`, `office-admin/`, `employee/` — one folder per role, each page a real `.html` file
- `assets/css/` — `tokens.css` (design tokens) → `base.css` → `layout.css` → `components.css`, plus `pages/*.css` for page-specific styles
- `assets/js/`
  - `config.js` — API base URL
  - `api.js` — the only module that calls `fetch()`
  - `auth.js` — token storage (sessionStorage) + role decoding
  - `guard.js` — `requireRole(role)`, run at the top of every protected page; confirms the token server-side via `GET /auth/me`
  - `layout.js` — injects the sidebar/topbar chrome based on role
  - `ui/` — `toast.js`, `modal.js`, `table.js`, `error-state.js` shared widgets
  - `validators.js` — shared form validation helpers
  - `utils.js` — `escapeHtml`, used everywhere user-generated text is interpolated into innerHTML
  - `pages/...` — one controller file per HTML page

## Status

All 5 planned build phases are complete:

- **Phase 1 (shell & auth)** — login, role-based redirect, guarded dashboards.
- **Phase 2 (Super Admin area)** — offices CRUD, office admins CRUD, dashboard stat cards.
- **Phase 3 (Office Admin area)** — employees CRUD, meeting rooms CRUD, dashboard stat cards.
- **Phase 4 (Employee booking flow)** — dashboard (upcoming meetings), new-booking form
  (room + attendee pickers), my-meetings list, booking-detail (view/edit/cancel,
  organizer-only edit/cancel enforced both client- and server-side).
- **Phase 5 (polish/QA)** — done. Responsive: tables collapse into labelled-row
  cards below 768px (`table.js` emits `data-label`, CSS in `components.css`);
  mobile sidebar is a proper drawer with a click-to-close backdrop. Error states:
  every list/dashboard page shows a persistent error+retry box (`ui/error-state.js`)
  instead of an indefinite loading skeleton when its initial data fetch fails, and
  `guard.js` distinguishes "server unreachable" (`NetworkError`, session preserved,
  shows a retry page) from "session actually invalid" (logged out, redirected) —
  previously any `/auth/me` failure logged the user out, even a network blip.
  Accessibility: both modal types close on Escape, `confirmModal` auto-focuses
  Cancel; badge/toast colors (`--color-success`, `--color-warning`) were darkened
  to meet WCAG AA contrast. Also fixed two bugs found only by exercising these
  paths: `confirmModal` interpolated `title`/`message` without escaping (stored-XSS
  via any user-supplied name shown in a delete-confirm dialog), and `apiRequest`
  treated *any* 401 as "log the session out" — including the login endpoint itself
  rejecting bad credentials — so a wrong-password attempt silently reloaded the
  login page instead of showing the inline error.

Two open backend gaps identified during planning were resolved (not stubbed)
while building Phase 4: added `GET /meeting-rooms/available` and `GET /employees/colleagues`,
both employee-facing, read-only, scoped to the caller's own office — see
`app/api/meeting_room.py` / `app/api/employee.py`. The third open item (an
employee-accessible endpoint to resolve an arbitrary organizer's name) was
sidestepped rather than added: booking-detail resolves the organizer's name
by cross-referencing the already-fetched colleagues list, which covers every
case that matters (same-office, active employees).

`MeetingRoomResponse` now returns `status` (fixed 2026-07-13; was previously
missing even though `MeetingRoomUpdate` accepted it). `MeetingRoomUpdate.status`
was also tightened from `Optional[str]` to `Optional[RoomStatus]` for proper
422 validation instead of relying on SQLAlchemy to reject a bad value at
commit time. The office-admin meeting-rooms screen now shows a Status badge
and lets you toggle Active/Inactive from the edit modal; verified that
deactivating a room correctly removes it from the employee-facing
`GET /meeting-rooms/available` room picker.
