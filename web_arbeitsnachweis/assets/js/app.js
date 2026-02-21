const THEME_STORAGE_KEY = "arbeitsnachweis_theme";
const DAILY_STORAGE_PREFIX = "arbeitsnachweis_day_v1";
const INPUT_COLUMNS = ["begin", "end", "pause", "travel"];
const WEEKDAY_SHORT_NAMES = ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"];

const weekRows = Array.from(document.querySelectorAll("[data-week-row]"));
const errorList = document.getElementById("errorList");
const statusText = document.getElementById("statusText");
const refreshBtn = document.getElementById("refreshBtn");
const validateBtn = document.getElementById("validateBtn");
const resetBtn = document.getElementById("resetBtn");
const themeSelect = document.getElementById("themeSelect");
const installBtn = document.getElementById("installBtn");

let deferredInstallPrompt = null;

initializeTheme();
initializeInstallPrompt();
registerServiceWorker();
initializeDailyEntries();

refreshBtn.addEventListener("click", () => {
  recalculateAllRows(true);
  persistAllRows();
  errorList.innerHTML = "";
  setStatus("Berechnungen aktualisiert. Tagesdaten gespeichert.", "neutral");
});

validateBtn.addEventListener("click", () => {
  recalculateAllRows(true);
  persistAllRows();
  const errors = validateFormData();
  renderErrors(errors);
});

if (resetBtn) {
  resetBtn.addEventListener("click", () => {
    const confirmed = window.confirm(
      "Soll die aktuelle Woche wirklich zurueckgesetzt werden? Alle Eingaben dieser Woche werden geloescht."
    );

    if (!confirmed) {
      return;
    }

    resetCurrentWeek();
    errorList.innerHTML = "";
    setStatus("Aktuelle Woche wurde zurueckgesetzt.", "neutral");
  });
}

themeSelect.addEventListener("change", () => {
  setTheme(themeSelect.value);
});

weekRows.forEach((row) => {
  INPUT_COLUMNS.forEach((key) => {
    const input = getCellInput(row, key);

    input.addEventListener("input", () => {
      updateRow(row, { normalizeDurations: false });
      persistRow(row);
    });

    input.addEventListener("blur", () => {
      updateRow(row, { normalizeDurations: true });
      persistRow(row);
    });

    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        updateRow(row, { normalizeDurations: true });
        persistRow(row);
      }
    });
  });
});

function initializeTheme() {
  const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
  const theme = savedTheme === "light" || savedTheme === "dark" ? savedTheme : "dark";
  setTheme(theme);
}

function setTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem(THEME_STORAGE_KEY, theme);
  themeSelect.value = theme;
}

function initializeInstallPrompt() {
  if (!installBtn) {
    return;
  }

  installBtn.classList.add("is-hidden");

  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    deferredInstallPrompt = event;
    installBtn.classList.remove("is-hidden");
  });

  installBtn.addEventListener("click", async () => {
    if (!deferredInstallPrompt) {
      return;
    }

    deferredInstallPrompt.prompt();
    try {
      await deferredInstallPrompt.userChoice;
    } finally {
      deferredInstallPrompt = null;
      installBtn.classList.add("is-hidden");
    }
  });

  window.addEventListener("appinstalled", () => {
    deferredInstallPrompt = null;
    installBtn.classList.add("is-hidden");
    setStatus("App installiert.", "ok");
  });
}

function initializeDailyEntries() {
  const weekStartDate = getWeekStart(new Date());

  weekRows.forEach((row, index) => {
    const date = new Date(weekStartDate);
    date.setDate(weekStartDate.getDate() + index);

    const dateKey = toDateKey(date);
    row.dataset.dateKey = dateKey;
    row.cells[0].textContent = `${WEEKDAY_SHORT_NAMES[date.getDay()]} ${toDateLabel(date)}`;

    const savedEntry = readDayEntry(dateKey);
    if (!savedEntry) {
      return;
    }

    INPUT_COLUMNS.forEach((key) => {
      const value = savedEntry[key];
      if (typeof value === "string") {
        getCellInput(row, key).value = value;
      }
    });
  });
}

function getWeekStart(baseDate) {
  const date = new Date(baseDate);
  date.setHours(0, 0, 0, 0);
  const daysSinceMonday = (date.getDay() + 6) % 7;
  date.setDate(date.getDate() - daysSinceMonday);
  return date;
}

function toDateKey(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function toDateLabel(date) {
  const day = String(date.getDate()).padStart(2, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  return `${day}.${month}.`;
}

function getDayStorageKey(dateKey) {
  return `${DAILY_STORAGE_PREFIX}_${dateKey}`;
}

function readDayEntry(dateKey) {
  const raw = localStorage.getItem(getDayStorageKey(dateKey));
  if (!raw) {
    return null;
  }

  try {
    const data = JSON.parse(raw);
    return data && typeof data === "object" ? data : null;
  } catch {
    return null;
  }
}

function persistRow(row) {
  const dateKey = row.dataset.dateKey;
  if (!dateKey) {
    return;
  }

  const entry = {};
  let hasValue = false;

  INPUT_COLUMNS.forEach((key) => {
    const value = getCellInput(row, key).value.trim();
    entry[key] = value;
    if (value) {
      hasValue = true;
    }
  });

  const storageKey = getDayStorageKey(dateKey);
  if (!hasValue) {
    localStorage.removeItem(storageKey);
    return;
  }

  entry.updatedAt = new Date().toISOString();
  localStorage.setItem(storageKey, JSON.stringify(entry));
}

function persistAllRows() {
  weekRows.forEach((row) => persistRow(row));
}

function resetCurrentWeek() {
  weekRows.forEach((row) => {
    INPUT_COLUMNS.forEach((key) => {
      getCellInput(row, key).value = "";
    });
    getCellInput(row, "work").value = "";
    getCellInput(row, "total").value = "";

    const dateKey = row.dataset.dateKey;
    if (dateKey) {
      localStorage.removeItem(getDayStorageKey(dateKey));
    }
  });
}

function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) {
    return;
  }

  window.addEventListener("load", () => {
    navigator.serviceWorker.register("service-worker.js").catch((error) => {
      console.error("Service Worker konnte nicht registriert werden:", error);
    });
  });
}

function getCellInput(row, key) {
  return row.querySelector(`[data-col="${key}"]`);
}

function parseHHMMToMinutes(value) {
  if (!value) {
    return null;
  }

  const text = value.trim();
  const match = /^(\d{1,2}):(\d{2})$/.exec(text);
  if (!match) {
    return null;
  }

  const hours = Number(match[1]);
  const minutes = Number(match[2]);
  if (Number.isNaN(hours) || Number.isNaN(minutes)) {
    return null;
  }
  if (hours < 0 || hours > 23 || minutes < 0 || minutes > 59) {
    return null;
  }

  return hours * 60 + minutes;
}

function parseDurationToMinutes(value) {
  if (value == null) {
    return null;
  }

  const text = value.trim();
  if (!text) {
    return null;
  }

  if (text.includes(":")) {
    const match = /^(\d+):(\d{2})$/.exec(text);
    if (!match) {
      return null;
    }

    const hours = Number(match[1]);
    const minutes = Number(match[2]);
    if (Number.isNaN(hours) || Number.isNaN(minutes)) {
      return null;
    }
    if (hours < 0 || minutes < 0 || minutes > 59) {
      return null;
    }

    return hours * 60 + minutes;
  }

  const normalized = text.replace(",", ".");
  const hoursFloat = Number(normalized);
  if (Number.isNaN(hoursFloat) || hoursFloat < 0) {
    return null;
  }

  return Math.round(hoursFloat * 60);
}

function minutesToDecimalHours(totalMinutes) {
  const hoursValue = totalMinutes / 60;
  let decimalText = hoursValue.toFixed(2).replace(/\.0+$/, "").replace(/(\.\d*[1-9])0+$/, "$1");
  if (!decimalText.includes(".")) {
    decimalText += ".0";
  }
  return decimalText.replace(".", ",");
}

function updateRow(row, options = {}) {
  const normalizeDurations = Boolean(options.normalizeDurations);

  const beginInput = getCellInput(row, "begin");
  const endInput = getCellInput(row, "end");
  const pauseInput = getCellInput(row, "pause");
  const travelInput = getCellInput(row, "travel");
  const workInput = getCellInput(row, "work");
  const totalInput = getCellInput(row, "total");

  const begin = beginInput.value.trim();
  const end = endInput.value.trim();
  const pauseRaw = pauseInput.value.trim();
  const travelRaw = travelInput.value.trim();

  if (!begin && !end && !pauseRaw && !travelRaw) {
    workInput.value = "";
    totalInput.value = "";
    return;
  }

  const pauseMinutes = parseDurationToMinutes(pauseRaw || "00:00");
  const travelMinutes = parseDurationToMinutes(travelRaw || "00:00");

  if (pauseMinutes == null || travelMinutes == null) {
    workInput.value = "";
    totalInput.value = "";
    return;
  }

  if (normalizeDurations) {
    if (pauseRaw) {
      pauseInput.value = minutesToDecimalHours(pauseMinutes);
    }
    if (travelRaw) {
      travelInput.value = minutesToDecimalHours(travelMinutes);
    }
  }

  if (!begin || !end) {
    workInput.value = "";
    totalInput.value = "";
    return;
  }

  const beginMinutes = parseHHMMToMinutes(begin);
  const endMinutes = parseHHMMToMinutes(end);

  if (beginMinutes == null || endMinutes == null) {
    workInput.value = "";
    totalInput.value = "";
    return;
  }

  const totalMinutes = endMinutes - beginMinutes;
  if (totalMinutes < 0) {
    workInput.value = "";
    totalInput.value = "";
    return;
  }

  const workMinutes = totalMinutes - pauseMinutes - travelMinutes;
  if (workMinutes < 0) {
    workInput.value = "";
    totalInput.value = "";
    return;
  }

  totalInput.value = minutesToDecimalHours(totalMinutes);
  workInput.value = minutesToDecimalHours(workMinutes);
}

function recalculateAllRows(normalizeDurations) {
  weekRows.forEach((row) => updateRow(row, { normalizeDurations }));
}

function validateFormData() {
  const errors = [];

  weekRows.forEach((row) => {
    const day = row.cells[0].textContent.trim();

    const begin = getCellInput(row, "begin").value.trim();
    const end = getCellInput(row, "end").value.trim();
    const pause = getCellInput(row, "pause").value.trim();
    const travel = getCellInput(row, "travel").value.trim();

    if ((begin && !end) || (!begin && end)) {
      errors.push(`${day} Beginn und Ende bitte gemeinsam ausfuellen.`);
    }

    if (begin && parseHHMMToMinutes(begin) == null) {
      errors.push(`${day} Beginn ist ungueltig (HH:MM).`);
    }

    if (end && parseHHMMToMinutes(end) == null) {
      errors.push(`${day} Ende ist ungueltig (HH:MM).`);
    }

    if (pause && parseDurationToMinutes(pause) == null) {
      errors.push(`${day} Pause ist ungueltig (HH:MM oder Dezimal, z. B. 0,5).`);
    }

    if (travel && parseDurationToMinutes(travel) == null) {
      errors.push(`${day} Fahrt ist ungueltig (HH:MM oder Dezimal, z. B. 4,5).`);
    }

    const beginMinutes = parseHHMMToMinutes(begin);
    const endMinutes = parseHHMMToMinutes(end);
    const pauseMinutes = parseDurationToMinutes(pause || "00:00");
    const travelMinutes = parseDurationToMinutes(travel || "00:00");

    if (beginMinutes != null && endMinutes != null && endMinutes < beginMinutes) {
      errors.push(`${day} Ende liegt vor Beginn.`);
    }

    if (
      beginMinutes != null &&
      endMinutes != null &&
      pauseMinutes != null &&
      travelMinutes != null &&
      endMinutes - beginMinutes - pauseMinutes - travelMinutes < 0
    ) {
      errors.push(`${day} Summe aus Pause/Fahrt ist laenger als die Gesamtzeit.`);
    }
  });

  return errors;
}

function renderErrors(errors) {
  errorList.innerHTML = "";

  if (!errors.length) {
    setStatus("Eingaben sind gueltig.", "ok");
    return;
  }

  setStatus(`Es gibt ${errors.length} Problem(e).`, "error");
  errors.forEach((errorText) => {
    const li = document.createElement("li");
    li.textContent = errorText;
    errorList.appendChild(li);
  });
}

function setStatus(text, mode) {
  statusText.textContent = text;
  statusText.className = `status ${mode}`;
}

recalculateAllRows(false);
setStatus("Bereit. Eingaben werden taeglich automatisch gespeichert.", "neutral");
