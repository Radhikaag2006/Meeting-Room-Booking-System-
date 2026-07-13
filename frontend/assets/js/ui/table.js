// Renders an array of objects into a <table> given a column spec. Shared by
// every admin list page (offices, office admins, employees, meeting rooms,
// my-meetings) so table markup and empty-state handling live in one place.
//
// columns: [{ label: string, render: (row) => string }]
export function renderTable(container, { columns, rows, emptyMessage = "Nothing to show yet." }) {
  const headerHtml = columns.map((col) => `<th>${col.label}</th>`).join("");

  // data-label lets the ≤768px layout (components.css) render each cell as
  // a labelled row instead of a column, without duplicating markup per page.
  const bodyHtml = rows.length
    ? rows
        .map(
          (row) =>
            `<tr>${columns.map((col) => `<td data-label="${col.label}">${col.render(row)}</td>`).join("")}</tr>`
        )
        .join("")
    : `<tr class="empty-row"><td colspan="${columns.length}">${emptyMessage}</td></tr>`;

  container.innerHTML = `
    <table class="data-table">
      <thead><tr>${headerHtml}</tr></thead>
      <tbody>${bodyHtml}</tbody>
    </table>
  `;
}
