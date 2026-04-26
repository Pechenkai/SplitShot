(function () {
  var state = {
    total: 2980,
    participants: ["Аня", "Миша", "Оля"],
    theme: "light",
    language: "Русский",
    notifications: true,
    byPeople: {},
    selectedParticipant: "Аня",
    items: {"Аня":[{name:"Паста",price:990}],"Миша":[{name:"Пицца",price:1290}],"Оля":[]},
    history: [{type:"draft"}],
    fortuneWinner: "Аня",
    fortuneAngle: 0,
    fortuneSpinning: false
  };

  var locales = {
    "Русский": {
      participantsTitle: "Добавьте<br>участников",
      participantsSubtitle: "Начните с команды, а потом переходите к делению счета",
      participantsNow: "Участников сейчас",
      participantPlaceholder: "Имя участника",
      continue: "Продолжить",
      homeTitle: "Как хотите<br>разделить счет?",
      homeSubtitle: "Сначала выберите режим, затем подтвердите расчет",
      billTotal: "Итого по счету",
      apply: "Применить",
      mainFlow: "main flow",
      splitBill: "Разделить счет",
      splitBillSub: "Поровну, по людям или по позициям",
      payFull: "Оплатить счет целиком",
      payFullSub: "Один участник берет на себя весь счет",
      fullPaymentTitle: "Оплата целиком",
      toPay: "К оплате",
      payer: "Плательщик",
      payerSub: "Один участник оплачивает всю сумму",
      onePerson: "1 чел.",
      participantsInGroup: "Участников в компании",
      participantsInGroupSub: "Для истории и дальнейших сценариев",
      confirm: "Подтвердить",
      splitModeTitle: "Режим деления",
      splitModeSubtitle: "Выберите подходящий способ распределения суммы",
      equalSplit: "Поровну",
      equalSplitSub: "Сумма делится на всех участников одинаково",
      byPeople: "По людям",
      byPeopleSub: "Введите отдельную сумму для каждого участника",
      byItems: "По позициям",
      byItemsSub: "Выберите участника и добавляйте его блюда/позиции",
      fortuneWheel: "Колесо фортуны",
      fortuneWheelSub: "Случайным образом выберите, кто оплатит счет",
      equalSplitTitle: "Деление поровну",
      totalAmount: "Общая сумма",
      participantsCount: "Количество участников",
      participantsCountSub: "Равное деление на всех из списка",
      eachPays: "Каждый платит",
      eachPaysSub: "Итоговая сумма на человека",
      saveCalculation: "Сохранить расчет",
      splitByPeopleTitle: "Деление по людям",
      assignedToParticipants: "Назначено участникам",
      splitByItemsTitle: "Деление по позициям",
      itemNamePlaceholder: "Название позиции",
      pricePlaceholder: "₽",
      assignedByItems: "Назначено по позициям",
      currentResult: "Текущий результат",
      fortuneHint: "В колесо попадают все участники, добавленные на первом экране",
      fortuneScreenSub: "Рандомно выбирает, кто оплатит счет",
      participantsInWheel: "Участники в колесе",
      spinWheel: "Крутить колесо",
      saveToHistory: "Сохранить в историю",
      profileTitle: "Профиль",
      localProfile: "Локальный профиль приложения",
      theme: "Тема",
      themeSub: "Переключение между светлой и темной",
      history: "История",
      historySub: "Ранее сохраненные разделения счета",
      settings: "Настройки",
      settingsSub: "Язык интерфейса и уведомления",
      savedCalculations: "Сохраненные расчеты",
      language: "Язык",
      languageSub: "Выберите язык интерфейса",
      notifications: "Уведомления",
      notificationsSub: "Напоминания и системные сообщения",
      currentSettings: "Текущие настройки",
      light: "Светлая",
      dark: "Темная",
      on: "Вкл",
      off: "Выкл",
      participantIndex: "Участник #{index}",
      individualAmount: "Индивидуальная сумма",
      remaining: "Остаток: {amount}",
      assignedItemTo: "Позиция назначена участнику {name}",
      noItemsYet: "Пока нет позиций",
      historyDraftTitle: "Стартовый пример",
      historyDraftDetails: "Подготовлен экран для презентации",
      historyEqualTitle: "Деление поровну",
      historyEqualDetails: "{count} участников · по {amount} каждому",
      historyPeopleTitle: "Деление по людям",
      historyPeopleDetails: "Назначено {assigned} · остаток {remaining}",
      historyItemsTitle: "Деление по позициям",
      historyItemsDetails: "{count} позиций · назначено {assigned}",
      historyFullTitle: "Оплата целиком",
      historyFullDetails: "Один участник оплатил {amount}",
      historyFortuneTitle: "Колесо фортуны",
      historyFortuneDetails: "Счет оплачивает {winner}"
    },
    "English": {
      participantsTitle: "Add<br>participants",
      participantsSubtitle: "Start with the group, then continue to bill splitting",
      participantsNow: "Participants now",
      participantPlaceholder: "Participant name",
      continue: "Continue",
      homeTitle: "How do you want<br>to split the bill?",
      homeSubtitle: "Choose a mode first, then confirm the calculation",
      billTotal: "Bill total",
      apply: "Apply",
      mainFlow: "main flow",
      splitBill: "Split the bill",
      splitBillSub: "Equally, by people, or by items",
      payFull: "Pay the full bill",
      payFullSub: "One participant covers the whole bill",
      fullPaymentTitle: "Full payment",
      toPay: "To pay",
      payer: "Payer",
      payerSub: "One participant pays the whole amount",
      onePerson: "1 person",
      participantsInGroup: "Participants in group",
      participantsInGroupSub: "Used for history and follow-up flows",
      confirm: "Confirm",
      splitModeTitle: "Split mode",
      splitModeSubtitle: "Choose the preferred way to distribute the amount",
      equalSplit: "Equal split",
      equalSplitSub: "The total is split equally among all participants",
      byPeople: "By people",
      byPeopleSub: "Enter a separate amount for each participant",
      byItems: "By items",
      byItemsSub: "Choose a participant and add their items",
      fortuneWheel: "Wheel of fortune",
      fortuneWheelSub: "Randomly choose who pays the bill",
      equalSplitTitle: "Equal split",
      totalAmount: "Total amount",
      participantsCount: "Participants count",
      participantsCountSub: "Equal split across everyone in the list",
      eachPays: "Each pays",
      eachPaysSub: "Final amount per person",
      saveCalculation: "Save calculation",
      splitByPeopleTitle: "Split by people",
      assignedToParticipants: "Assigned to participants",
      splitByItemsTitle: "Split by items",
      itemNamePlaceholder: "Item name",
      pricePlaceholder: "$",
      assignedByItems: "Assigned by items",
      currentResult: "Current result",
      fortuneHint: "All participants added on the first screen are included in the wheel",
      fortuneScreenSub: "Randomly chooses who pays the bill",
      participantsInWheel: "Participants in wheel",
      spinWheel: "Spin the wheel",
      saveToHistory: "Save to history",
      profileTitle: "Profile",
      localProfile: "Local app profile",
      theme: "Theme",
      themeSub: "Switch between light and dark",
      history: "History",
      historySub: "Previously saved bill splits",
      settings: "Settings",
      settingsSub: "Interface language and notifications",
      savedCalculations: "Saved calculations",
      language: "Language",
      languageSub: "Choose the interface language",
      notifications: "Notifications",
      notificationsSub: "Reminders and system messages",
      currentSettings: "Current settings",
      light: "Light",
      dark: "Dark",
      on: "On",
      off: "Off",
      participantIndex: "Participant #{index}",
      individualAmount: "Individual amount",
      remaining: "Remaining: {amount}",
      assignedItemTo: "Item assigned to {name}",
      noItemsYet: "No items yet",
      historyDraftTitle: "Starter example",
      historyDraftDetails: "Presentation screen prepared",
      historyEqualTitle: "Equal split",
      historyEqualDetails: "{count} participants · {amount} each",
      historyPeopleTitle: "Split by people",
      historyPeopleDetails: "Assigned {assigned} · remaining {remaining}",
      historyItemsTitle: "Split by items",
      historyItemsDetails: "{count} items · assigned {assigned}",
      historyFullTitle: "Full payment",
      historyFullDetails: "One participant paid {amount}",
      historyFortuneTitle: "Wheel of fortune",
      historyFortuneDetails: "{winner} pays the bill"
    },
    "Deutsch": {
      participantsTitle: "Teilnehmer<br>hinzufügen",
      participantsSubtitle: "Starte mit der Gruppe und gehe dann zur Aufteilung der Rechnung",
      participantsNow: "Teilnehmer aktuell",
      participantPlaceholder: "Name des Teilnehmers",
      continue: "Weiter",
      homeTitle: "Wie möchtet ihr<br>die Rechnung teilen?",
      homeSubtitle: "Wähle zuerst einen Modus und bestätige dann die Berechnung",
      billTotal: "Rechnung gesamt",
      apply: "Anwenden",
      mainFlow: "main flow",
      splitBill: "Rechnung teilen",
      splitBillSub: "Gleichmäßig, nach Personen oder nach Positionen",
      payFull: "Komplett bezahlen",
      payFullSub: "Eine Person übernimmt die ganze Rechnung",
      fullPaymentTitle: "Komplettzahlung",
      toPay: "Zu zahlen",
      payer: "Zahler",
      payerSub: "Eine Person zahlt den Gesamtbetrag",
      onePerson: "1 Person",
      participantsInGroup: "Teilnehmer in der Gruppe",
      participantsInGroupSub: "Für Verlauf und weitere Abläufe",
      confirm: "Bestätigen",
      splitModeTitle: "Teilungsmodus",
      splitModeSubtitle: "Wähle die passende Art der Verteilung",
      equalSplit: "Gleichmäßig",
      equalSplitSub: "Der Gesamtbetrag wird gleichmäßig auf alle verteilt",
      byPeople: "Nach Personen",
      byPeopleSub: "Gib für jede Person einen eigenen Betrag ein",
      byItems: "Nach Positionen",
      byItemsSub: "Wähle eine Person und füge ihre Positionen hinzu",
      fortuneWheel: "Glücksrad",
      fortuneWheelSub: "Wähle zufällig aus, wer die Rechnung bezahlt",
      equalSplitTitle: "Gleichmäßige Teilung",
      totalAmount: "Gesamtbetrag",
      participantsCount: "Anzahl Teilnehmer",
      participantsCountSub: "Gleichmäßig auf alle in der Liste verteilt",
      eachPays: "Jede Person zahlt",
      eachPaysSub: "Endbetrag pro Person",
      saveCalculation: "Berechnung speichern",
      splitByPeopleTitle: "Nach Personen teilen",
      assignedToParticipants: "Teilnehmern zugewiesen",
      splitByItemsTitle: "Nach Positionen teilen",
      itemNamePlaceholder: "Name der Position",
      pricePlaceholder: "€",
      assignedByItems: "Nach Positionen zugewiesen",
      currentResult: "Aktuelles Ergebnis",
      fortuneHint: "Alle Teilnehmer vom ersten Screen werden in das Rad aufgenommen",
      fortuneScreenSub: "Wählt zufällig aus, wer die Rechnung bezahlt",
      participantsInWheel: "Teilnehmer im Rad",
      spinWheel: "Rad drehen",
      saveToHistory: "Im Verlauf speichern",
      profileTitle: "Profil",
      localProfile: "Lokales App-Profil",
      theme: "Thema",
      themeSub: "Zwischen hell und dunkel wechseln",
      history: "Verlauf",
      historySub: "Frühere gespeicherte Aufteilungen",
      settings: "Einstellungen",
      settingsSub: "Sprache und Benachrichtigungen",
      savedCalculations: "Gespeicherte Berechnungen",
      language: "Sprache",
      languageSub: "Wähle die Sprache der Oberfläche",
      notifications: "Benachrichtigungen",
      notificationsSub: "Erinnerungen und Systemmeldungen",
      currentSettings: "Aktuelle Einstellungen",
      light: "Hell",
      dark: "Dunkel",
      on: "An",
      off: "Aus",
      participantIndex: "Teilnehmer #{index}",
      individualAmount: "Individueller Betrag",
      remaining: "Rest: {amount}",
      assignedItemTo: "Position zugewiesen an {name}",
      noItemsYet: "Noch keine Positionen",
      historyDraftTitle: "Startbeispiel",
      historyDraftDetails: "Präsentationsscreen vorbereitet",
      historyEqualTitle: "Gleichmäßige Teilung",
      historyEqualDetails: "{count} Teilnehmer · jeweils {amount}",
      historyPeopleTitle: "Nach Personen teilen",
      historyPeopleDetails: "{assigned} zugewiesen · Rest {remaining}",
      historyItemsTitle: "Nach Positionen teilen",
      historyItemsDetails: "{count} Positionen · {assigned} zugewiesen",
      historyFullTitle: "Komplettzahlung",
      historyFullDetails: "Eine Person zahlte {amount}",
      historyFortuneTitle: "Glücksrad",
      historyFortuneDetails: "{winner} bezahlt die Rechnung"
    }
  };

  var screens = document.querySelectorAll(".screen");
  var wheelColors = ["#ff9dcf", "#7e7bff", "#6cd8bb", "#ffd970", "#b791ff", "#66c8ff", "#ffb36b", "#9fe870"];

  function tr(key, params) {
    var dict = locales[state.language] || locales["Русский"];
    var text = dict[key] || key;
    params = params || {};
    Object.keys(params).forEach(function (k) {
      text = text.replace(new RegExp("\\{" + k + "\\}", "g"), params[k]);
    });
    return text;
  }

  function localeCode() {
    if (state.language === "English") return "en-US";
    if (state.language === "Deutsch") return "de-DE";
    return "ru-RU";
  }

  function currencySymbol() {
    if (state.language === "English") return "$";
    if (state.language === "Deutsch") return "€";
    return "₽";
  }

  function formatCurrency(n) {
    n = Number(n || 0);
    return n.toLocaleString(localeCode(), {maximumFractionDigits: 2}) + " " + currencySymbol();
  }

  function initials(name) {
    return (name || "?").trim().charAt(0).toUpperCase();
  }

  function ensureState() {
    var count = Math.max(state.participants.length, 1);
    var each = +(state.total / count).toFixed(2);
    state.participants.forEach(function (name) {
      if (state.byPeople[name] === undefined) state.byPeople[name] = each;
      if (!state.items[name]) state.items[name] = [];
    });
    Object.keys(state.byPeople).forEach(function(name) {
      if (state.participants.indexOf(name) === -1) delete state.byPeople[name];
    });
    Object.keys(state.items).forEach(function(name) {
      if (state.participants.indexOf(name) === -1) delete state.items[name];
    });
    if (state.participants.indexOf(state.selectedParticipant) === -1) {
      state.selectedParticipant = state.participants[0] || "";
    }
    if (state.participants.indexOf(state.fortuneWinner) === -1) {
      state.fortuneWinner = state.participants[0] || "";
    }
  }

  function historyText(entry) {
    if (entry.type === "equal") {
      return {title: tr("historyEqualTitle"), details: tr("historyEqualDetails", {count: entry.count, amount: formatCurrency(entry.per)})};
    }
    if (entry.type === "people") {
      return {title: tr("historyPeopleTitle"), details: tr("historyPeopleDetails", {assigned: formatCurrency(entry.assigned), remaining: formatCurrency(entry.remaining)})};
    }
    if (entry.type === "items") {
      return {title: tr("historyItemsTitle"), details: tr("historyItemsDetails", {count: entry.count, assigned: formatCurrency(entry.assigned)})};
    }
    if (entry.type === "full") {
      return {title: tr("historyFullTitle"), details: tr("historyFullDetails", {amount: formatCurrency(entry.amount)})};
    }
    if (entry.type === "fortune") {
      return {title: tr("historyFortuneTitle"), details: tr("historyFortuneDetails", {winner: entry.winner})};
    }
    return {title: tr("historyDraftTitle"), details: tr("historyDraftDetails")};
  }

  function applyStaticTranslations() {
    document.documentElement.lang = state.language === "English" ? "en" : (state.language === "Deutsch" ? "de" : "ru");
    Array.prototype.forEach.call(document.querySelectorAll("[data-i18n]"), function (el) {
      el.innerHTML = tr(el.getAttribute("data-i18n"));
    });
    Array.prototype.forEach.call(document.querySelectorAll("[data-placeholder]"), function (el) {
      el.placeholder = tr(el.getAttribute("data-placeholder"));
    });
    document.getElementById("languageSelect").value = state.language;
  }

  function showScreen(id) {
    Array.prototype.forEach.call(screens, function (screen) {
      screen.classList.remove("active");
      screen.style.display = "none";
    });
    var next = document.getElementById(id);
    next.style.display = "flex";
    next.classList.add("active");
    if (id === "fortuneWheel") renderFortuneWheel();
  }

  function renderParticipants() {
    ensureState();
    var box = document.getElementById("participantsList");
    box.innerHTML = "";
    state.participants.forEach(function (name, index) {
      var div = document.createElement("div");
      div.className = "participant";
      div.innerHTML =
        '<div class="participant-left">' +
          '<div class="avatar">' + initials(name) + '</div>' +
          '<div><div class="participant-name">' + name + '</div><div class="participant-meta">' + tr("participantIndex", {index: index + 1}) + '</div></div>' +
        '</div>' +
        '<button class="mini-btn" data-remove="' + name + '">×</button>';
      box.appendChild(div);
    });
    document.getElementById("participantsCountValue").textContent = String(state.participants.length);
    document.getElementById("goToHomeBtn").disabled = state.participants.length === 0;
    document.getElementById("fullParticipantsTail").textContent = String(state.participants.length);
  }

  function renderHome() {
    document.getElementById("homeTotalValue").textContent = formatCurrency(state.total);
    document.getElementById("homeAmountChip").textContent = formatCurrency(state.total);
    document.getElementById("fullPaymentValue").textContent = formatCurrency(state.total);
    document.getElementById("equalTotalValue").textContent = formatCurrency(state.total);
    document.getElementById("totalAmountInput").value = String(state.total);
  }

  function renderEqual() {
    var count = Math.max(state.participants.length, 1);
    var per = +(state.total / count).toFixed(2);
    document.getElementById("equalParticipantsValue").textContent = String(count);
    document.getElementById("equalPerPersonValue").textContent = formatCurrency(per);
  }

  function renderPeople() {
    ensureState();
    var box = document.getElementById("peopleAssignList");
    box.innerHTML = "";
    var assigned = 0;
    state.participants.forEach(function (name) {
      var value = Number(state.byPeople[name] || 0);
      assigned += value;
      var row = document.createElement("div");
      row.className = "participant";
      row.innerHTML =
        '<div class="participant-left">' +
          '<div class="avatar">' + initials(name) + '</div>' +
          '<div><div class="participant-name">' + name + '</div><div class="participant-meta">' + tr("individualAmount") + '</div></div>' +
        '</div>' +
        '<input class="number-input people-input" data-name="' + name + '" type="number" min="0" step="1" value="' + value + '">';
      box.appendChild(row);
    });
    var remaining = +(state.total - assigned).toFixed(2);
    document.getElementById("peopleAssignedTotal").textContent = formatCurrency(assigned);
    var hint = document.getElementById("peopleRemainingHint");
    hint.textContent = tr("remaining", {amount: formatCurrency(remaining)});
    hint.style.color = Math.abs(remaining) < 0.01 ? "var(--success)" : "var(--warning)";
  }

  function renderItems() {
    ensureState();
    var pills = document.getElementById("itemParticipantsPills");
    pills.innerHTML = "";
    state.participants.forEach(function (name) {
      var p = document.createElement("button");
      p.className = "pill" + (state.selectedParticipant === name ? " active" : "");
      p.textContent = name;
      p.addEventListener("click", function () {
        state.selectedParticipant = name;
        renderItems();
      });
      pills.appendChild(p);
    });

    var box = document.getElementById("itemsList");
    box.innerHTML = "";
    var assigned = 0;

    state.participants.forEach(function (name) {
      var list = state.items[name] || [];
      var subtotal = 0;
      list.forEach(function (item) { subtotal += Number(item.price || 0); });
      assigned += subtotal;

      var wrap = document.createElement("div");
      wrap.className = "list-box";
      var html = '<div class="list-title">' + name + ' · ' + formatCurrency(subtotal) + '</div>';
      if (list.length) {
        list.forEach(function (item) {
          html += '<div class="history-item"><div class="history-top"><span>' + item.name + '</span><span>' + formatCurrency(item.price) + '</span></div><div class="history-sub">' + tr("assignedItemTo", {name: name}) + '</div></div>';
        });
      } else {
        html += '<div class="history-sub">' + tr("noItemsYet") + '</div>';
      }
      wrap.innerHTML = html;
      box.appendChild(wrap);
    });

    var remaining = +(state.total - assigned).toFixed(2);
    document.getElementById("itemsAssignedTotal").textContent = formatCurrency(assigned);
    var hint = document.getElementById("itemsRemainingHint");
    hint.textContent = tr("remaining", {amount: formatCurrency(remaining)});
    hint.style.color = Math.abs(remaining) < 0.01 ? "var(--success)" : "var(--warning)";
  }

  function renderFortuneWheel() {
    ensureState();
    var wheel = document.getElementById("fortuneWheelGraphic");
    var labels = document.getElementById("fortuneWheelLabels");
    var pills = document.getElementById("fortuneParticipantsPills");
    var winner = document.getElementById("fortuneWinnerValue");
    winner.textContent = state.fortuneWinner || (state.participants[0] || "");

    var count = Math.max(state.participants.length, 1);
    var step = 360 / count;
    var gradientParts = [];
    labels.innerHTML = "";
    pills.innerHTML = "";

    state.participants.forEach(function(name, index) {
      var color = wheelColors[index % wheelColors.length];
      gradientParts.push(color + " " + (index * step) + "deg " + ((index + 1) * step) + "deg");

      var label = document.createElement("div");
      label.className = "wheel-label";

      var angleDeg = index * step + step / 2 - 90;
      var angleRad = angleDeg * Math.PI / 180;

      var wheelSize = wheel.offsetWidth || 292;
      var center = wheelSize / 2;
      var textRadius = wheelSize * 0.31;

      var x = center + Math.cos(angleRad) * textRadius;
      var y = center + Math.sin(angleRad) * textRadius;

      label.style.left = x + "px";
      label.style.top = y + "px";
      label.textContent = name;

      labels.appendChild(label);

      var pill = document.createElement("span");
      pill.className = "fortune-pill";
      pill.textContent = name;
      pills.appendChild(pill);
    });

    wheel.classList.add("dynamic");
    wheel.style.setProperty("--wheel-gradient", "conic-gradient(" + gradientParts.join(",") + ")");
    wheel.style.transform = "rotate(" + state.fortuneAngle + "deg)";
  }

  function renderProfile() {
    document.getElementById("themeTail").textContent = state.theme === "dark" ? tr("dark") : tr("light");
  }

  function renderHistory() {
    var box = document.getElementById("historyList");
    box.innerHTML = "";
    state.history.forEach(function (entry) {
      var loc = historyText(entry);
      var div = document.createElement("div");
      div.className = "history-item";
      div.innerHTML =
        '<div class="history-top"><span>' + loc.title + '</span><span>' + formatCurrency(entry.amount || state.total) + '</span></div>' +
        '<div class="history-sub">' + loc.details + (entry.date ? " · " + entry.date : "") + '</div>';
      box.appendChild(div);
    });
  }

  function renderSettings() {
    document.getElementById("languageSelect").value = state.language;
    document.getElementById("notificationsToggle").classList.toggle("on", state.notifications);
    document.getElementById("settingsSummaryValue").textContent = state.language + " · " + (state.notifications ? tr("on") : tr("off"));
  }

  function applyTheme() {
    document.body.classList.toggle("dark", state.theme === "dark");
    renderProfile();
  }

  function normalizeAfterTotal() {
    var each = +(state.total / Math.max(state.participants.length, 1)).toFixed(2);
    state.participants.forEach(function (name) {
      state.byPeople[name] = each;
    });
  }

  function renderAll() {
    applyStaticTranslations();
    renderParticipants();
    renderHome();
    renderEqual();
    renderPeople();
    renderItems();
    renderFortuneWheel();
    renderProfile();
    renderHistory();
    renderSettings();
  }

  function spinWheel() {
    if (!state.participants.length || state.fortuneSpinning) return;
    state.fortuneSpinning = true;
    var winnerIndex = Math.floor(Math.random() * state.participants.length);
    var count = state.participants.length;
    var step = 360 / count;
    var centerAngle = winnerIndex * step + step / 2;
    var finalAngle = 360 - centerAngle;
    var extraSpins = 360 * (4 + Math.floor(Math.random() * 3));
    state.fortuneAngle = state.fortuneAngle + extraSpins + finalAngle;
    state.fortuneWinner = state.participants[winnerIndex];

    var wheel = document.getElementById("fortuneWheelGraphic");
    wheel.style.transform = "rotate(" + state.fortuneAngle + "deg)";
    setTimeout(function() {
      state.fortuneSpinning = false;
      document.getElementById("fortuneWinnerValue").textContent = state.fortuneWinner;
    }, 4000);
  }

  document.addEventListener("click", function (e) {
    var goEl = e.target.closest("[data-go]");
    if (goEl) {
      showScreen(goEl.getAttribute("data-go"));
      return;
    }

    var removeEl = e.target.closest("[data-remove]");
    if (removeEl) {
      var name = removeEl.getAttribute("data-remove");
      state.participants = state.participants.filter(function (p) { return p !== name; });
      delete state.byPeople[name];
      delete state.items[name];
      renderAll();
      return;
    }
  });

  document.getElementById("participantNameInput").addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      document.getElementById("addParticipantBtn").click();
    }
  });

  document.getElementById("addParticipantBtn").addEventListener("click", function () {
    var input = document.getElementById("participantNameInput");
    var value = input.value.trim();
    if (!value) return;
    state.participants.push(value);
    state.byPeople[value] = +(state.total / Math.max(state.participants.length, 1)).toFixed(2);
    state.items[value] = [];
    state.selectedParticipant = value;
    state.fortuneWinner = value;
    input.value = "";
    renderAll();
  });

  document.getElementById("goToHomeBtn").addEventListener("click", function () {
    showScreen("home");
  });

  document.getElementById("saveTotalBtn").addEventListener("click", function () {
    var next = Number(document.getElementById("totalAmountInput").value || 0);
    state.total = Math.max(0, next);
    normalizeAfterTotal();
    renderAll();
  });

  document.getElementById("themeRow").addEventListener("click", function () {
    state.theme = state.theme === "dark" ? "light" : "dark";
    applyTheme();
  });

  document.getElementById("languageSelect").addEventListener("change", function (e) {
    state.language = e.target.value;
    renderAll();
  });

  document.getElementById("notificationsToggle").addEventListener("click", function () {
    state.notifications = !state.notifications;
    renderSettings();
  });

  document.getElementById("peopleAssignList").addEventListener("input", function (e) {
    if (!e.target.classList.contains("people-input")) return;
    state.byPeople[e.target.getAttribute("data-name")] = Number(e.target.value || 0);
    renderPeople();
  });

  document.getElementById("addItemBtn").addEventListener("click", function () {
    var name = document.getElementById("itemNameInput").value.trim();
    var price = Number(document.getElementById("itemPriceInput").value || 0);
    if (!name || !price || !state.selectedParticipant) return;
    state.items[state.selectedParticipant].push({name: name, price: price});
    document.getElementById("itemNameInput").value = "";
    document.getElementById("itemPriceInput").value = "";
    renderItems();
  });

  document.getElementById("confirmFullPaymentBtn").addEventListener("click", function () {
    state.history.unshift({type: "full", amount: state.total, date: new Date().toLocaleString(localeCode())});
    renderHistory();
    showScreen("historyScreen");
  });

  document.getElementById("saveEqualSplitBtn").addEventListener("click", function () {
    var per = +(state.total / Math.max(state.participants.length, 1)).toFixed(2);
    state.history.unshift({type: "equal", amount: state.total, count: state.participants.length, per: per, date: new Date().toLocaleString(localeCode())});
    renderHistory();
    showScreen("historyScreen");
  });

  document.getElementById("savePeopleSplitBtn").addEventListener("click", function () {
    var assigned = 0;
    state.participants.forEach(function (name) { assigned += Number(state.byPeople[name] || 0); });
    var remaining = +(state.total - assigned).toFixed(2);
    state.history.unshift({type: "people", amount: state.total, assigned: assigned, remaining: remaining, date: new Date().toLocaleString(localeCode())});
    renderHistory();
    showScreen("historyScreen");
  });

  document.getElementById("saveItemsSplitBtn").addEventListener("click", function () {
    var assigned = 0;
    var count = 0;
    state.participants.forEach(function (name) {
      (state.items[name] || []).forEach(function (item) {
        assigned += Number(item.price || 0);
        count += 1;
      });
    });
    state.history.unshift({type: "items", amount: state.total, assigned: assigned, count: count, date: new Date().toLocaleString(localeCode())});
    renderHistory();
    showScreen("historyScreen");
  });

  document.getElementById("spinWheelBtn").addEventListener("click", spinWheel);

  document.getElementById("saveFortuneBtn").addEventListener("click", function () {
    if (!state.fortuneWinner) return;
    state.history.unshift({type: "fortune", amount: state.total, winner: state.fortuneWinner, date: new Date().toLocaleString(localeCode())});
    renderHistory();
    showScreen("historyScreen");
  });

  renderAll();
  applyTheme();
  showScreen("participants");
})();
