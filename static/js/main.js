// simple helper to render a list into an element
function renderList(container, items, renderFn) {
  const el = document.getElementById(container);
  if (!el) return;
  el.innerHTML = items.map(renderFn).join('') || '<p>No results</p>';
}

/* Books search */
const bookSearch = document.getElementById('bookSearch');
if (bookSearch) {
  bookSearch.addEventListener('input', async (e) => {
    const q = e.target.value;
    const res = await fetch('/books/search?q=' + encodeURIComponent(q));
    const data = await res.json();
    renderList('bookResults', data, b => `
      <div class="card">
        <strong>${b.Title}</strong> — ${b.Author} (${b.Category || 'N/A'}) [Copies: ${b.Copies}]
      </div>
    `);
  });
}

/* Members search */
const memberSearch = document.getElementById('memberSearch');
if (memberSearch) {
  memberSearch.addEventListener('input', async (e) => {
    const q = e.target.value;
    const res = await fetch('/members/search?q=' + encodeURIComponent(q));
    const data = await res.json();
    renderList('memberResults', data, m => `
      <div class="card">
        <strong>${m.Name}</strong> — ${m.Contact || 'N/A'}
      </div>
    `);
  });
}

/* Borrowings search */
const borrowSearch = document.getElementById('borrowSearch');
if (borrowSearch) {
  borrowSearch.addEventListener('input', async (e) => {
    const q = e.target.value;
    const res = await fetch('/borrowings/search?q=' + encodeURIComponent(q));
    const data = await res.json();
    renderList('borrowResults', data, br => `
      <div class="card">
        <strong>${br.MemberName}</strong> borrowed <em>${br.BookTitle}</em> on ${br.BorrowDate} ${br.ReturnDate ? ' — returned ' + br.ReturnDate : ''}
      </div>
    `);
  });
}
