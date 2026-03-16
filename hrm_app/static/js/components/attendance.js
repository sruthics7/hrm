function calculateWorked(el) {
    const row = el.parentElement.parentElement;
    const startInput = row.cells[1].querySelector('input').value;
    const endInput = row.cells[2].querySelector('input').value;

    if (startInput && endInput) {
      const start = new Date("1970-01-01T" + startInput + "Z");
      const end = new Date("1970-01-01T" + endInput + "Z");
      let diff = (end - start) / 60000; // minutes

      if (diff < 0) diff += 1440; // handle past midnight

      const hours = Math.floor(diff / 60);
      const minutes = diff % 60;
      row.querySelector(".worked").textContent = `${hours}h ${minutes}m`;
    }
  }

  function deleteRow(btn) {
    const row = btn.parentElement.parentElement;
    row.remove();
  }
























