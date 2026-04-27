(function () {
    var STORAGE_KEY = "splitshot.app.v2";
    var state = {
      total: 2980,
      tips: 0,
      equalTips: 0,
      itemsTips: 0,
      participants: ["Аня", "Миша", "Оля"],
      theme: "light",
      language: "Русский",
      notifications: true,
      byPeople: {},
      selectedParticipant: "Аня",
      selectedItemParticipants: ["Аня"],
      itemsPayer: "Аня",
      peoplePayer: "Аня",
      items: {"Аня":[{name:"Паста",price:990}],"Миша":[{name:"Пицца",price:1290}],"Оля":[]},
      detailedItems: [],
      history: [{type:"draft"}],
      debts: [],
      companyId: null,
      participantIds: {},
      gameSessionIds: {},
      backendOnline: false,
      inviteCode: null,
      wheelRotation: 0,
      fortuneWinner: "Аня",
      fortuneSpinning: false,
      sobriety: {next: 1, errors: 0, startedAt: 0, running: false},
      tongue: {passes: 0, fails: 0},
      recording: {active: false}
    };
    var mediaRecorder = null;
    var recordedChunks = [];
    var wheelColors = ["#ff9dcf", "#7e7bff", "#6cd8bb", "#ffd970", "#b791ff", "#66c8ff", "#ffb36b", "#9fe870"];
    var participantsPollTimer = null;
    var participantsPollInFlight = false;

    function loadState() {
      try {
        var saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
        if (saved && typeof saved === "object") state = Object.assign(state, saved);
      } catch (e) {}
    }

    function saveState() {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    }

    function apiFetch(path, options) {
      options = options || {};
      var headers = Object.assign({"Content-Type": "application/json"}, options.headers || {});
      return fetch(path, Object.assign({}, options, {headers: headers})).then(function (response) {
        if (!response.ok) {
          return response.json().catch(function () { return {}; }).then(function (body) {
            throw new Error(body.detail || response.statusText || "API error");
          });
        }
        if (response.status === 204) return null;
        return response.json();
      });
    }

    function participantId(name) {
      return state.participantIds && state.participantIds[name];
    }

    function participantNameById(id) {
      var found = state.participants.find(function (name) {
        return Number(participantId(name)) === Number(id);
      });
      return found || ("#" + id);
    }

    function toApiAmount(value) {
      return Number(value || 0).toFixed(2);
    }

    function apiBody(body) {
      return {method: "POST", body: JSON.stringify(body)};
    }

    function markBackendOnline() {
      state.backendOnline = true;
      saveState();
    }

    function handleApiError(error) {
      state.backendOnline = false;
      saveState();
      notify("Backend: " + error.message);
      throw error;
    }

    function ensureBackendCompany() {
      if (state.companyId) {
        return syncParticipantsToBackend().then(function () { return state.companyId; });
      }
      return apiFetch("/api/companies", apiBody({title: "SplitShot party"}))
        .then(function (company) {
          state.companyId = company.id;
          state.inviteCode = company.invite_code;
          markBackendOnline();
          return syncParticipantsToBackend().then(function () { return company.id; });
        })
        .catch(handleApiError);
    }

    function syncParticipantsToBackend() {
      state.participantIds = state.participantIds || {};
      if (!state.companyId) return Promise.resolve();
      var chain = Promise.resolve();
      state.participants.forEach(function (name) {
        if (state.participantIds[name]) return;
        chain = chain.then(function () {
          return apiFetch("/api/companies/" + state.companyId + "/participants", apiBody({name: name}))
            .then(function (participant) {
              state.participantIds[name] = participant.id;
              markBackendOnline();
            });
        });
      });
      return chain.then(saveState);
    }

    function applyBackendParticipants(participants) {
      var nextNames = participants.map(function (participant) { return participant.name; });
      var changed = nextNames.length !== state.participants.length ||
        nextNames.some(function (name, index) { return state.participants[index] !== name; });

      state.participantIds = {};
      participants.forEach(function (participant) {
        state.participantIds[participant.name] = participant.id;
        if (state.byPeople[participant.name] === undefined) {
          state.byPeople[participant.name] = 0;
        }
        if (!state.items[participant.name]) state.items[participant.name] = [];
      });

      Object.keys(state.byPeople).forEach(function (name) {
        if (nextNames.indexOf(name) === -1) delete state.byPeople[name];
      });
      Object.keys(state.items).forEach(function (name) {
        if (nextNames.indexOf(name) === -1) delete state.items[name];
      });
      state.selectedItemParticipants = (state.selectedItemParticipants || []).filter(function (name) {
        return nextNames.indexOf(name) !== -1;
      });
      state.detailedItems = (state.detailedItems || []).map(function (item) {
        item.participants = item.participants.filter(function (name) { return nextNames.indexOf(name) !== -1; });
        return item;
      }).filter(function (item) { return item.participants.length > 0; });

      state.participants = nextNames;
      ensureState();
      if (changed) {
        state.debts = [];
        renderAll();
      } else {
        saveState();
      }
      return changed;
    }

    function refreshParticipantsFromBackend(silent) {
      if (!state.companyId || participantsPollInFlight) return Promise.resolve(false);
      participantsPollInFlight = true;
      return apiFetch("/api/companies/" + state.companyId + "/participants")
        .then(function (participants) {
          markBackendOnline();
          return applyBackendParticipants(participants);
        })
        .catch(function (error) {
          state.backendOnline = false;
          saveState();
          if (!silent) notify("Backend: " + error.message);
          return false;
        })
        .then(function (changed) {
          participantsPollInFlight = false;
          return changed;
        });
    }

    function startParticipantsPolling() {
      if (participantsPollTimer) return;
      participantsPollTimer = window.setInterval(function () {
        refreshParticipantsFromBackend(true);
      }, 3000);
    }

    document.addEventListener("visibilitychange", function () {
      if (!document.hidden) refreshParticipantsFromBackend(true);
    });

    function loadBackendCompanyByCode(inviteCode) {
      return apiFetch("/api/companies/by-code/" + encodeURIComponent(inviteCode))
        .then(function (company) {
          state.companyId = company.id;
          state.inviteCode = company.invite_code;
          markBackendOnline();
          return apiFetch("/api/companies/" + company.id + "/participants");
        })
        .then(function (participants) {
          applyBackendParticipants(participants);
          notify("Компания загружена");
        })
        .catch(handleApiError);
    }

    function createBackendParticipant(name) {
      return ensureBackendCompany().then(function () {
        if (state.participantIds[name]) return state.participantIds[name];
        return apiFetch("/api/companies/" + state.companyId + "/participants", apiBody({name: name}))
          .then(function (participant) {
            state.participantIds[name] = participant.id;
            markBackendOnline();
            return participant.id;
          });
      });
    }

    function deleteBackendParticipant(name) {
      var id = participantId(name);
      delete state.participantIds[name];
      if (!id) return Promise.resolve();
      return apiFetch("/api/participants/" + id, {method: "DELETE"}).then(markBackendOnline).catch(function () {});
    }

    function backendDebtsToState(debts) {
      state.debts = (debts || []).map(function (debt) {
        return {
          id: debt.id,
          debtor: participantNameById(debt.debtor_id),
          creditor: participantNameById(debt.creditor_id),
          amount: Number(debt.amount)
        };
      });
      markBackendOnline();
      renderDebts();
      return state.debts;
    }

    function notifySplitError(error) {
      notify("Сплиттер: " + error.message);
    }

    function createGameSession(gameType) {
      return ensureBackendCompany().then(function () {
        if (state.gameSessionIds && state.gameSessionIds[gameType]) return state.gameSessionIds[gameType];
        return apiFetch("/api/companies/" + state.companyId + "/game-sessions", apiBody({game_type: gameType}))
          .then(function (session) {
            state.gameSessionIds = state.gameSessionIds || {};
            state.gameSessionIds[gameType] = session.id;
            markBackendOnline();
            return session.id;
          });
      });
    }

    function saveGameResult(gameType, participantName, resultValue, resultData) {
      return ensureBackendCompany()
        .then(function () {
          var id = participantId(participantName);
          if (!id) return null;
          return createGameSession(gameType).then(function (sessionId) {
            return apiFetch("/api/game-sessions/" + sessionId + "/results", apiBody({
              participant_id: id,
              result_value: resultValue,
              result_data: resultData || null
            }));
          });
        })
        .then(markBackendOnline)
        .catch(function (error) { notify("Backend: " + error.message); });
    }

    function inviteUrl() {
      if (!state.inviteCode) return window.location.origin + window.location.pathname;
      return window.location.origin + window.location.pathname + "?company=" + encodeURIComponent(state.inviteCode);
    }
  
    var locales = {
      "Русский": {
        notesTitle: "SplitShot — working prototype",
        notesText: "Исправленная версия: участники отображаются, добавляются, сумма меняется, язык меняется во всем приложении.",
        chip1: "Участники", chip2: "Сумма счета", chip3: "Язык", chip4: "История",
        participantsTitle: "Добавьте<br>участников",
        participantsSubtitle: "Начните с команды, а потом переходите к делению счета",
        participantsNow: "Участников сейчас",
        participantPlaceholder: "Имя участника",
        continue: "Продолжить",
        homeTitle: "Как хотите<br>разделить счет?",
        homeSubtitle: "Сначала выберите режим, затем подтвердите расчет",
        billTotal: "Итого по счету",
        editBill: "Изменить сумму счета",
        editBillSub: "Новое значение применяется ко всем экранам",
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
        gamesHub: "Игры за столом",
        gamesHubSub: "Колесо, тест на трезвость и скороговорка",
        tips: "Чаевые",
        payerSelect: "Кто оплатил счет",
        debts: "Долги",
        copyDebts: "Копировать долги",
        splitResultTitle: "Результат",
        copied: "Скопировано",
        byItemsHint: "Выберите одного или нескольких участников для позиции",
        wheelTitle: "Колесо фортуны",
        wheelSub: "Случайно выбирает участника",
        wheelResult: "Результат",
        spin: "Крутить",
        spinWheel: "Крутить колесо",
        saveToHistory: "Сохранить в историю",
        currentResult: "Текущий результат",
        fortuneHint: "В колесо попадают все участники, добавленные на первом экране",
        fortuneScreenSub: "Рандомно выбирает, кто не платит сегодня",
        participantsInWheel: "Участники в колесе",
        wheelPays: "Сегодня не платит {name}",
        sobrietyTitle: "Тест на трезвость",
        sobrietySub: "Нажмите числа 1–20 по порядку",
        start: "Старт",
        sobrietyResult: "{name}: индекс {score}%",
        tongueTitle: "Скороговорка",
        tongueSub: "Караоке-режим с голосованием",
        phrase: "Фраза",
        passed: "Зачет",
        failed: "Фант",
        forfeit: "Фант",
        newPhrase: "Новая фраза",
        participantLimit: "Можно добавить от 1 до 15 участников",
        copyInvite: "Копировать ссылку компании",
        splitAll: "Разделить на всех",
        record: "Записать",
        stop: "Стоп"
      },
      "English": {
        notesTitle: "SplitShot — working prototype",
        notesText: "Fixed version: participants render correctly, can be added, total price changes, and language updates across the whole app.",
        chip1: "Participants", chip2: "Bill total", chip3: "Language", chip4: "History",
        participantsTitle: "Add<br>participants",
        participantsSubtitle: "Start with the group, then continue to bill splitting",
        participantsNow: "Participants now",
        participantPlaceholder: "Participant name",
        continue: "Continue",
        homeTitle: "How do you want<br>to split the bill?",
        homeSubtitle: "Choose a mode first, then confirm the calculation",
        billTotal: "Bill total",
        editBill: "Edit bill amount",
        editBillSub: "The new value is applied on all screens",
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
        gamesHub: "Table games",
        gamesHubSub: "Wheel, sobriety test, and tongue twister",
        tips: "Tips",
        payerSelect: "Who paid the bill",
        debts: "Debts",
        copyDebts: "Copy debts",
        splitResultTitle: "Result",
        copied: "Copied",
        byItemsHint: "Select one or more participants for the item",
        wheelTitle: "Wheel of fortune",
        wheelSub: "Randomly selects a participant",
        wheelResult: "Result",
        spin: "Spin",
        spinWheel: "Spin the wheel",
        saveToHistory: "Save to history",
        currentResult: "Current result",
        fortuneHint: "All participants added on the first screen are included in the wheel",
        fortuneScreenSub: "Randomly chooses who does not pay today",
        participantsInWheel: "Participants in wheel",
        wheelPays: "{name} does not pay today",
        sobrietyTitle: "Sobriety test",
        sobrietySub: "Tap numbers 1–20 in order",
        start: "Start",
        sobrietyResult: "{name}: index {score}%",
        tongueTitle: "Tongue twister",
        tongueSub: "Karaoke mode with voting",
        phrase: "Phrase",
        passed: "Pass",
        failed: "Forfeit",
        forfeit: "Forfeit",
        newPhrase: "New phrase",
        participantLimit: "You can add 1 to 15 participants",
        copyInvite: "Copy company link",
        splitAll: "Split among all",
        record: "Record",
        stop: "Stop"
      },
      "Deutsch": {
        notesTitle: "SplitShot — funktionierender Prototyp",
        notesText: "Korrigierte Version: Teilnehmer werden angezeigt, können hinzugefügt werden, der Gesamtbetrag ändert sich und die Sprache aktualisiert die ganze App.",
        chip1: "Teilnehmer", chip2: "Rechnungsbetrag", chip3: "Sprache", chip4: "Verlauf",
        participantsTitle: "Teilnehmer<br>hinzufügen",
        participantsSubtitle: "Starte mit der Gruppe und gehe dann zur Aufteilung der Rechnung",
        participantsNow: "Teilnehmer aktuell",
        participantPlaceholder: "Name des Teilnehmers",
        continue: "Weiter",
        homeTitle: "Wie möchtet ihr<br>die Rechnung teilen?",
        homeSubtitle: "Wähle zuerst einen Modus und bestätige dann die Berechnung",
        billTotal: "Rechnung gesamt",
        editBill: "Rechnungsbetrag ändern",
        editBillSub: "Der neue Wert gilt auf allen Screens",
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
        gamesHub: "Tischspiele",
        gamesHubSub: "Rad, Nüchternheitstest und Zungenbrecher",
        tips: "Trinkgeld",
        payerSelect: "Wer hat bezahlt",
        debts: "Schulden",
        copyDebts: "Schulden kopieren",
        splitResultTitle: "Ergebnis",
        copied: "Kopiert",
        byItemsHint: "Wähle eine oder mehrere Personen für die Position",
        wheelTitle: "Glücksrad",
        wheelSub: "Wählt zufällig eine Person",
        wheelResult: "Ergebnis",
        spin: "Drehen",
        spinWheel: "Rad drehen",
        saveToHistory: "Im Verlauf speichern",
        currentResult: "Aktuelles Ergebnis",
        fortuneHint: "Alle Teilnehmer vom ersten Screen werden in das Rad aufgenommen",
        fortuneScreenSub: "Wählt zufällig aus, wer heute nicht zahlt",
        participantsInWheel: "Teilnehmer im Rad",
        wheelPays: "{name} zahlt heute nicht",
        sobrietyTitle: "Nüchternheitstest",
        sobrietySub: "Tippe die Zahlen 1–20 der Reihe nach",
        start: "Start",
        sobrietyResult: "{name}: Index {score}%",
        tongueTitle: "Zungenbrecher",
        tongueSub: "Karaoke-Modus mit Abstimmung",
        phrase: "Satz",
        passed: "Bestanden",
        failed: "Pfand",
        forfeit: "Pfand",
        newPhrase: "Neuer Satz",
        participantLimit: "Du kannst 1 bis 15 Personen hinzufügen",
        copyInvite: "Einladungslink kopieren",
        splitAll: "Auf alle teilen",
        record: "Aufnehmen",
        stop: "Stopp"
      }
    };
    var tongueTwisters = [
      "Карл у Клары украл кораллы, а Клара у Карла украла кларнет.",
      "Шла Саша по шоссе и сосала сушку.",
      "На дворе трава, на траве дрова.",
      "От топота копыт пыль по полю летит."
    ];
    var forfeits = [
      "Скажи тост за стол за 10 секунд.",
      "Изобрази официанта с самым серьезным лицом.",
      "Придумай новое название вашей компании.",
      "Сделай комплимент каждому участнику."
    ];
  
    var screens = document.querySelectorAll(".screen");
  
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
      state.participantIds = state.participantIds || {};
      state.gameSessionIds = state.gameSessionIds || {};
      state.detailedItems = state.detailedItems || [];
      if (state.equalTips === undefined) state.equalTips = Number(state.tips || 0);
      if (state.itemsTips === undefined) state.itemsTips = Number(state.tips || 0);
      state.participants.forEach(function (name) {
        if (state.byPeople[name] === undefined) state.byPeople[name] = 0;
        if (!state.items[name]) state.items[name] = [];
      });
      if (state.participants.indexOf(state.selectedParticipant) === -1) {
        state.selectedParticipant = state.participants[0] || "";
      }
      if (state.participants.indexOf(state.itemsPayer) === -1) {
        state.itemsPayer = state.participants[0] || "";
      }
      if (state.participants.indexOf(state.peoplePayer) === -1) {
        state.peoplePayer = state.participants[0] || "";
      }
      state.selectedItemParticipants = (state.selectedItemParticipants || []).filter(function (name) {
        return state.participants.indexOf(name) !== -1;
      });
      if (!state.selectedItemParticipants.length && state.participants[0]) {
        state.selectedItemParticipants = [state.participants[0]];
      }
      if (state.participants.indexOf(state.fortuneWinner) === -1) {
        state.fortuneWinner = state.participants[0] || "";
      }
    }

    function notify(text) {
      var box = document.getElementById("appNotice");
      if (!box) return;
      box.textContent = text;
      box.hidden = false;
      window.setTimeout(function () { box.hidden = true; }, 2200);
    }

    function payerName() {
      return document.getElementById("payerSelect").value || state.participants[0] || "";
    }

    function rebuildItemsFromDetailedItems() {
      var rebuilt = {};
      state.participants.forEach(function (name) { rebuilt[name] = []; });
      (state.detailedItems || []).forEach(function (item) {
        var participants = (item.participants || []).filter(function (name) {
          return state.participants.indexOf(name) !== -1;
        });
        if (!participants.length) return;
        var share = +(Number(item.price || 0) / participants.length).toFixed(2);
        participants.forEach(function (name) {
          rebuilt[name].push({name: item.title, price: share});
        });
      });
      state.items = rebuilt;
    }

    function debtMessage() {
      if (!state.debts.length) return "SplitShot: долгов нет";
      return ["SplitShot: долги по счету"].concat(state.debts.map(function (debt) {
        return debt.debtor + " -> " + debt.creditor + ": " + formatCurrency(debt.amount);
      })).join("\n");
    }

    function cloneDebts() {
      return state.debts.map(function (debt) {
        return {
          debtor: debt.debtor,
          creditor: debt.creditor,
          amount: Number(debt.amount || 0)
        };
      });
    }

    function renderDebtList(elementId, debts) {
      var box = document.getElementById(elementId);
      if (!box) return;
      box.innerHTML = "";
      debts = debts || [];
      if (!debts.length) {
        box.innerHTML = '<div class="history-sub">—</div>';
        return;
      }
      debts.forEach(function (debt) {
        var row = document.createElement("div");
        row.className = "history-item";
        row.innerHTML = '<div class="history-top"><span>' + debt.debtor + ' → ' + debt.creditor + '</span><span>' + formatCurrency(debt.amount) + '</span></div>';
        box.appendChild(row);
      });
    }

    function showSplitResult(summary) {
      document.getElementById("splitResultSummary").textContent = summary || formatCurrency(state.total + Number(state.tips || 0));
      renderDebtList("resultDebtsList", state.debts);
      showScreen("splitResult");
    }

    function syncDebtsMessageFromBackend() {
      if (!state.companyId) return Promise.resolve(debtMessage());
      return apiFetch("/api/companies/" + state.companyId + "/debts/message")
        .then(function (data) {
          markBackendOnline();
          return data.message || debtMessage();
        })
        .catch(function () { return debtMessage(); });
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
      return {title: tr("historyDraftTitle"), details: tr("historyDraftDetails")};
    }

    function historyDetailsHtml(entry) {
      var rows = [];
      if (entry.debts && entry.debts.length) {
        rows.push('<div class="history-sub"><strong>' + tr("debts") + '</strong></div>');
        entry.debts.forEach(function (debt) {
          rows.push('<div class="history-sub">' + debt.debtor + ' → ' + debt.creditor + ': ' + formatCurrency(debt.amount) + '</div>');
        });
      }
      if (entry.items && entry.items.length) {
        rows.push('<div class="history-sub"><strong>' + tr("byItems") + '</strong></div>');
        entry.items.forEach(function (item) {
          rows.push('<div class="history-sub">' + item.title + ' · ' + formatCurrency(item.price) + ' · ' + item.participants.join(", ") + '</div>');
        });
      }
      if (!rows.length) rows.push('<div class="history-sub">—</div>');
      return rows.join("");
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
          '<div class="participant-actions"><button class="mini-btn" data-edit="' + name + '">✎</button><button class="mini-btn" data-remove="' + name + '">×</button></div>';
        box.appendChild(div);
      });
      document.getElementById("participantsCountValue").textContent = String(state.participants.length);
      document.getElementById("goToHomeBtn").disabled = state.participants.length === 0;
      document.getElementById("addParticipantBtn").disabled = state.participants.length >= 15;
      document.getElementById("fullParticipantsTail").textContent = String(state.participants.length);
      document.getElementById("participantsLimitHint").textContent = state.participants.length + "/15 · " + tr("participantLimit");
      if (state.companyId) {
        document.getElementById("participantsLimitHint").textContent += " · API #" + state.companyId;
      }
    }
  
    function renderHome() {
      document.getElementById("homeTotalValue").textContent = formatCurrency(state.total);
      document.getElementById("homeAmountChip").textContent = formatCurrency(state.total);
      document.getElementById("fullPaymentValue").textContent = formatCurrency(state.total);
      document.getElementById("equalTotalValue").textContent = formatCurrency(state.total);
      document.getElementById("totalAmountInput").value = String(state.total);
      document.getElementById("tipsAmountInput").value = String(state.equalTips || 0);
      renderParticipantSelect("payerSelect", payerName());
      renderParticipantSelect("peoplePayerSelect", state.peoplePayer || state.participants[0]);
      renderParticipantSelect("itemsPayerSelect", state.itemsPayer || state.participants[0]);
      document.getElementById("itemsTipsAmountInput").value = String(state.itemsTips || 0);
    }
  
    function renderEqual() {
      var count = Math.max(state.participants.length, 1);
      var per = +((state.total + Number(state.equalTips || 0)) / count).toFixed(2);
      document.getElementById("equalParticipantsValue").textContent = String(count);
      document.getElementById("equalPerPersonValue").textContent = formatCurrency(per);
      renderDebts();
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
      document.getElementById("peopleAssignedTotal").textContent = formatCurrency(assigned);
      var hint = document.getElementById("peopleRemainingHint");
      hint.textContent = "Итого к распределению: " + formatCurrency(assigned);
      hint.style.color = "var(--muted)";
    }
  
    function renderItems() {
      ensureState();
      rebuildItemsFromDetailedItems();
      var pills = document.getElementById("itemParticipantsPills");
      pills.innerHTML = "";
      state.participants.forEach(function (name) {
        var p = document.createElement("button");
        p.className = "pill" + (state.selectedItemParticipants.indexOf(name) !== -1 ? " active" : "");
        p.textContent = name;
        p.addEventListener("click", function () {
          var i = state.selectedItemParticipants.indexOf(name);
          if (i === -1) state.selectedItemParticipants.push(name);
          else if (state.selectedItemParticipants.length > 1) state.selectedItemParticipants.splice(i, 1);
          renderItems();
          saveState();
        });
        pills.appendChild(p);
      });
  
      var box = document.getElementById("itemsList");
      box.innerHTML = "";
      var assigned = 0;
  
      (state.detailedItems || []).forEach(function (item, index) {
        assigned += Number(item.price || 0);
        var wrap = document.createElement("div");
        wrap.className = "list-box";
        wrap.innerHTML =
          '<div class="history-top"><span>' + item.title + '</span><span>' + formatCurrency(item.price) + '</span></div>' +
          '<div class="history-sub">' + (item.participants || []).join(", ") + '</div>' +
          '<div class="participant-actions" style="margin-top:10px">' +
            '<button class="mini-btn" data-edit-item="' + index + '">✎</button>' +
            '<button class="mini-btn" data-remove-item="' + index + '">×</button>' +
          '</div>';
        box.appendChild(wrap);
      });
      if (!(state.detailedItems || []).length) box.innerHTML = '<div class="history-sub">' + tr("noItemsYet") + '</div>';
  
      var remaining = +(state.total - assigned).toFixed(2);
      document.getElementById("itemsAssignedTotal").textContent = formatCurrency(assigned);
      var hint = document.getElementById("itemsRemainingHint");
      hint.textContent = "Позиции: " + formatCurrency(assigned) + " · " + tr("tips") + ": " + formatCurrency(state.itemsTips || 0);
      hint.style.color = "var(--muted)";
    }
  
    function renderProfile() {
      document.getElementById("themeTail").textContent = state.theme === "dark" ? tr("dark") : tr("light");
    }
  
    function renderHistory() {
      var box = document.getElementById("historyList");
      box.innerHTML = "";
      state.history.forEach(function (entry, index) {
        var loc = historyText(entry);
        var div = document.createElement("div");
        div.className = "history-item";
        div.innerHTML =
          '<div class="history-top"><span>' + loc.title + '</span><span>' + formatCurrency(entry.amount || state.total) + '</span></div>' +
          '<div class="history-sub">' + loc.details + (entry.date ? " · " + entry.date : "") + '</div>' +
          '<button class="mini-save history-details-btn" data-history-details="' + index + '">Подробнее</button>' +
          '<div class="history-details" id="historyDetails' + index + '" hidden>' + historyDetailsHtml(entry) + '</div>';
        box.appendChild(div);
      });
    }

    function renderParticipantSelect(id, selected) {
      var el = document.getElementById(id);
      if (!el) return;
      el.innerHTML = "";
      state.participants.forEach(function (name) {
        var option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        el.appendChild(option);
      });
      if (selected && state.participants.indexOf(selected) !== -1) el.value = selected;
    }

    function renderDebts() {
      renderDebtList("debtsList", state.debts);
      renderDebtList("resultDebtsList", state.debts);
    }

    function renderFortuneWheel() {
      ensureState();
      var wheel = document.getElementById("fortuneWheelGraphic");
      var labels = document.getElementById("fortuneWheelLabels");
      var pills = document.getElementById("fortuneParticipantsPills");
      var winner = document.getElementById("fortuneWinnerValue");
      if (!wheel || !labels || !pills || !winner) return;

      winner.textContent = state.fortuneWinner || (state.participants[0] || "—");
      labels.innerHTML = "";
      pills.innerHTML = "";

      var count = Math.max(state.participants.length, 1);
      var step = 360 / count;
      var gradientParts = [];

      state.participants.forEach(function (name, index) {
        var color = wheelColors[index % wheelColors.length];
        gradientParts.push(color + " " + (index * step) + "deg " + ((index + 1) * step) + "deg");

        var label = document.createElement("div");
        label.className = "wheel-label";
        var angleDeg = index * step + step / 2 - 90;
        var angleRad = angleDeg * Math.PI / 180;
        var wheelSize = wheel.offsetWidth || 290;
        var center = wheelSize / 2;
        var textRadius = wheelSize * 0.31;
        var labelRotation = angleDeg + 90;
        label.style.left = center + Math.cos(angleRad) * textRadius + "px";
        label.style.top = center + Math.sin(angleRad) * textRadius + "px";
        label.style.transform = "translate(-50%, -50%) rotate(" + labelRotation + "deg)";
        label.textContent = name;
        labels.appendChild(label);

        var pill = document.createElement("span");
        pill.className = "pill";
        pill.textContent = name;
        pills.appendChild(pill);
      });

      wheel.classList.add("dynamic");
      wheel.style.setProperty("--wheel-gradient", "conic-gradient(" + gradientParts.join(",") + ")");
      wheel.style.transform = "rotate(" + state.wheelRotation + "deg)";
    }

    function renderGames() {
      renderParticipantSelect("sobrietyParticipantSelect", state.participants[0]);
      renderParticipantSelect("tongueParticipantSelect", state.participants[0]);
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
  
    function syncTotalInput() {
      var totalInput = document.getElementById("totalAmountInput");
      if (totalInput) state.total = Math.max(0, Number(totalInput.value || 0));
    }

    function syncEqualInputs() {
      syncTotalInput();
      var tipsInput = document.getElementById("tipsAmountInput");
      if (tipsInput) state.equalTips = Math.max(0, Number(tipsInput.value || 0));
    }

    function syncPeopleInputs() {
      var peoplePayerSelect = document.getElementById("peoplePayerSelect");
      if (peoplePayerSelect) state.peoplePayer = peoplePayerSelect.value || state.peoplePayer;
    }

    function syncItemsInputs() {
      var itemsTipsInput = document.getElementById("itemsTipsAmountInput");
      if (itemsTipsInput) state.itemsTips = Math.max(0, Number(itemsTipsInput.value || 0));
      var itemsPayerSelect = document.getElementById("itemsPayerSelect");
      if (itemsPayerSelect) state.itemsPayer = itemsPayerSelect.value || state.itemsPayer;
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
      renderGames();
      saveState();
    }
  
    document.addEventListener("click", function (e) {
      var goEl = e.target.closest("[data-go]");
      if (goEl) {
        showScreen(goEl.getAttribute("data-go"));
        return;
      }

      var detailsEl = e.target.closest("[data-history-details]");
      if (detailsEl) {
        var detailsBox = document.getElementById("historyDetails" + detailsEl.getAttribute("data-history-details"));
        if (detailsBox) detailsBox.hidden = !detailsBox.hidden;
        return;
      }

      var editItemEl = e.target.closest("[data-edit-item]");
      if (editItemEl) {
        var editIndex = Number(editItemEl.getAttribute("data-edit-item"));
        var item = state.detailedItems[editIndex];
        if (!item) return;
        var nextTitle = window.prompt("Название позиции", item.title);
        if (!nextTitle) return;
        var nextPrice = Number(window.prompt("Цена позиции", String(item.price)) || 0);
        if (!nextPrice) return;
        var nextParticipantsText = window.prompt("Участники через запятую", item.participants.join(", "));
        if (!nextParticipantsText) return;
        var nextParticipants = nextParticipantsText.split(",").map(function (name) {
          return name.trim();
        }).filter(function (name) {
          return state.participants.indexOf(name) !== -1;
        });
        if (!nextParticipants.length) {
          notify("Выберите хотя бы одного участника");
          return;
        }
        state.detailedItems[editIndex] = {title: nextTitle.trim(), price: nextPrice, participants: nextParticipants};
        rebuildItemsFromDetailedItems();
        renderItems();
        saveState();
        return;
      }

      var removeItemEl = e.target.closest("[data-remove-item]");
      if (removeItemEl) {
        state.detailedItems.splice(Number(removeItemEl.getAttribute("data-remove-item")), 1);
        rebuildItemsFromDetailedItems();
        renderItems();
        saveState();
        return;
      }

      var editEl = e.target.closest("[data-edit]");
      if (editEl) {
        var oldName = editEl.getAttribute("data-edit");
        var nextName = window.prompt("Новое имя", oldName);
        if (!nextName) return;
        nextName = nextName.trim();
        if (!nextName || nextName === oldName) return;
        var participantDbId = participantId(oldName);
        var index = state.participants.indexOf(oldName);
        if (index !== -1) state.participants[index] = nextName;
        state.byPeople[nextName] = state.byPeople[oldName];
        delete state.byPeople[oldName];
        state.items[nextName] = state.items[oldName] || [];
        delete state.items[oldName];
        state.selectedItemParticipants = state.selectedItemParticipants.map(function (name) {
          return name === oldName ? nextName : name;
        });
        state.detailedItems = (state.detailedItems || []).map(function (item) {
          item.participants = item.participants.map(function (name) { return name === oldName ? nextName : name; });
          return item;
        });
        if (participantDbId) {
          delete state.participantIds[oldName];
          state.participantIds[nextName] = participantDbId;
          apiFetch("/api/participants/" + participantDbId, {method: "PATCH", body: JSON.stringify({name: nextName})})
            .then(markBackendOnline)
            .catch(function (error) { notify("Backend: " + error.message); });
        }
        renderAll();
        return;
      }
  
      var removeEl = e.target.closest("[data-remove]");
      if (removeEl) {
        var name = removeEl.getAttribute("data-remove");
        deleteBackendParticipant(name);
        state.participants = state.participants.filter(function (p) { return p !== name; });
        delete state.byPeople[name];
        delete state.items[name];
        state.detailedItems = (state.detailedItems || []).filter(function (item) {
          item.participants = item.participants.filter(function (participant) { return participant !== name; });
          return item.participants.length > 0;
        });
        state.debts = [];
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
      if (state.participants.length >= 15) {
        notify(tr("participantLimit"));
        return;
      }
      state.participants.push(value);
      state.byPeople[value] = 0;
      state.items[value] = [];
      state.selectedParticipant = value;
      input.value = "";
      renderAll();
      createBackendParticipant(value).then(renderAll).catch(function () {});
    });
  
    document.getElementById("goToHomeBtn").addEventListener("click", function () {
      ensureBackendCompany().then(function () {
        renderAll();
        showScreen("home");
      }).catch(function () {
        showScreen("home");
      });
    });
  
    document.getElementById("saveTotalBtn").addEventListener("click", function () {
      syncTotalInput();
      renderAll();
    });

    document.getElementById("saveTipsBtn").addEventListener("click", function () {
      syncEqualInputs();
      renderEqual();
      saveState();
    });

    document.getElementById("saveItemsTipsBtn").addEventListener("click", function () {
      syncItemsInputs();
      renderItems();
      saveState();
    });

    document.getElementById("itemsPayerSelect").addEventListener("change", function (e) {
      state.itemsPayer = e.target.value;
      saveState();
    });

    document.getElementById("peoplePayerSelect").addEventListener("change", function (e) {
      state.peoplePayer = e.target.value;
      saveState();
    });

    document.getElementById("copyInviteBtn").addEventListener("click", function () {
      ensureBackendCompany().then(function () {
        var text = inviteUrl();
        if (navigator.clipboard) navigator.clipboard.writeText(text);
        notify(tr("copied"));
        renderAll();
      }).catch(function () {});
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
      saveState();
    });
  
    document.getElementById("peopleAssignList").addEventListener("input", function (e) {
      if (!e.target.classList.contains("people-input")) return;
      state.byPeople[e.target.getAttribute("data-name")] = Number(e.target.value || 0);
      renderPeople();
      saveState();
    });
  
    document.getElementById("addItemBtn").addEventListener("click", function () {
      var name = document.getElementById("itemNameInput").value.trim();
      var price = Number(document.getElementById("itemPriceInput").value || 0);
      if (!name || !price || !state.selectedItemParticipants.length) return;
      state.detailedItems = state.detailedItems || [];
      state.detailedItems.push({
        title: name,
        price: price,
        participants: state.selectedItemParticipants.slice()
      });
      state.selectedItemParticipants.forEach(function (participant) {
        state.items[participant].push({name: name, price: +(price / state.selectedItemParticipants.length).toFixed(2)});
      });
      document.getElementById("itemNameInput").value = "";
      document.getElementById("itemPriceInput").value = "";
      renderItems();
      saveState();
    });

    document.getElementById("selectAllItemParticipantsBtn").addEventListener("click", function () {
      state.selectedItemParticipants = state.participants.slice();
      renderItems();
      saveState();
    });
  
    document.getElementById("confirmFullPaymentBtn").addEventListener("click", function () {
      state.history.unshift({type: "full", amount: state.total, date: new Date().toLocaleString(localeCode())});
      renderHistory();
      showScreen("historyScreen");
      saveState();
    });
  
    document.getElementById("saveEqualSplitBtn").addEventListener("click", function () {
      syncEqualInputs();
      var per = +((state.total + Number(state.equalTips || 0)) / Math.max(state.participants.length, 1)).toFixed(2);
      var payer = payerName();
      ensureBackendCompany()
        .then(function () {
          return apiFetch("/api/companies/" + state.companyId + "/split/quick", apiBody({
            total_amount: toApiAmount(state.total),
            tips_amount: toApiAmount(state.equalTips),
            payer_id: participantId(payer)
          }));
        })
        .then(function (debts) {
          backendDebtsToState(debts);
          state.history.unshift({type: "equal", amount: state.total, count: state.participants.length, per: per, debts: cloneDebts(), date: new Date().toLocaleString(localeCode())});
          renderHistory();
          saveState();
          showSplitResult(formatCurrency(state.total + Number(state.equalTips || 0)));
        })
        .catch(notifySplitError);
    });
  
    document.getElementById("savePeopleSplitBtn").addEventListener("click", function () {
      syncPeopleInputs();
      var assigned = 0;
      state.participants.forEach(function (name) { assigned += Number(state.byPeople[name] || 0); });
      ensureBackendCompany()
        .then(function () {
          var apiItems = state.participants.map(function (name) {
            return {
              title: name,
              price: toApiAmount(state.byPeople[name] || 0),
              participant_ids: [participantId(name)].filter(Boolean)
            };
          }).filter(function (item) {
            return Number(item.price) > 0 && item.participant_ids.length > 0;
          });
          return apiFetch("/api/companies/" + state.companyId + "/split/detailed", apiBody({
            items: apiItems,
            tips_amount: "0.00",
            payer_id: participantId(state.peoplePayer || state.participants[0])
          }));
        })
        .then(function (debts) {
          if (debts && debts.length !== undefined) backendDebtsToState(debts);
          state.history.unshift({type: "people", amount: assigned, assigned: assigned, remaining: 0, debts: cloneDebts(), date: new Date().toLocaleString(localeCode())});
          renderHistory();
          saveState();
          showSplitResult(formatCurrency(assigned));
        })
        .catch(notifySplitError);
    });
  
    document.getElementById("saveItemsSplitBtn").addEventListener("click", function () {
      syncItemsInputs();
      rebuildItemsFromDetailedItems();
      var assigned = 0;
      var count = 0;
      state.participants.forEach(function (name) {
        (state.items[name] || []).forEach(function (item) {
          assigned += Number(item.price || 0);
          count += 1;
        });
      });
      var itemsPayer = state.itemsPayer || state.participants[0];
      ensureBackendCompany()
        .then(function () {
          var apiItems = (state.detailedItems || []).map(function (item) {
            return {
              title: item.title,
              price: toApiAmount(item.price),
              participant_ids: item.participants.map(participantId).filter(Boolean)
            };
          }).filter(function (item) { return item.participant_ids.length > 0; });
          return apiFetch("/api/companies/" + state.companyId + "/split/detailed", apiBody({
            items: apiItems,
            tips_amount: toApiAmount(state.itemsTips),
            payer_id: participantId(itemsPayer)
          }));
        })
        .then(function (debts) {
          if (debts && debts.length !== undefined) backendDebtsToState(debts);
          state.history.unshift({
            type: "items",
            amount: assigned + Number(state.itemsTips || 0),
            assigned: assigned,
            count: count,
            debts: cloneDebts(),
            items: (state.detailedItems || []).map(function (item) {
              return {title: item.title, price: item.price, participants: item.participants.slice()};
            }),
            date: new Date().toLocaleString(localeCode())
          });
          renderHistory();
          saveState();
          showSplitResult(formatCurrency(assigned + Number(state.itemsTips || 0)));
        })
        .catch(notifySplitError);
    });

    document.getElementById("copyDebtsBtn").addEventListener("click", function () {
      syncDebtsMessageFromBackend().then(function (text) {
      if (navigator.clipboard) navigator.clipboard.writeText(text);
      notify(tr("copied"));
      });
    });

    document.getElementById("copyResultDebtsBtn").addEventListener("click", function () {
      syncDebtsMessageFromBackend().then(function (text) {
        if (navigator.clipboard) navigator.clipboard.writeText(text);
        notify(tr("copied"));
      });
    });

    document.getElementById("spinWheelBtn").addEventListener("click", function () {
      if (!state.participants.length || state.fortuneSpinning) return;
      state.fortuneSpinning = true;
      var index = Math.floor(Math.random() * state.participants.length);
      var name = state.participants[index];
      var step = 360 / state.participants.length;
      var centerAngle = index * step + step / 2;
      state.wheelRotation = state.wheelRotation + 360 * (4 + Math.floor(Math.random() * 3)) + (360 - centerAngle);
      state.fortuneWinner = name;
      document.getElementById("fortuneWheelGraphic").style.transform = "rotate(" + state.wheelRotation + "deg)";
      window.setTimeout(function () {
        state.fortuneSpinning = false;
        document.getElementById("fortuneWinnerValue").textContent = state.fortuneWinner;
        saveState();
      }, 4000);
      state.history.unshift({type: "game", amount: 0, date: new Date().toLocaleString(localeCode())});
      saveState();
      saveGameResult("wheel", name, tr("wheelPays", {name: name}), {selected_name: name});
    });

    document.getElementById("saveFortuneBtn").addEventListener("click", function () {
      if (!state.fortuneWinner) return;
      state.history.unshift({
        type: "game",
        amount: state.total,
        date: new Date().toLocaleString(localeCode())
      });
      saveGameResult("wheel", state.fortuneWinner, tr("wheelPays", {name: state.fortuneWinner}), {
        selected_name: state.fortuneWinner,
        saved_to_history: true
      });
      renderHistory();
      showScreen("historyScreen");
      saveState();
    });

    function shuffle(numbers) {
      return numbers.sort(function () { return Math.random() - 0.5; });
    }

    function startSobriety() {
      state.sobriety = {next: 1, errors: 0, startedAt: Date.now(), running: true};
      var grid = document.getElementById("sobrietyGrid");
      grid.innerHTML = "";
      shuffle(Array.from({length: 20}, function (_, i) { return i + 1; })).forEach(function (number) {
        var btn = document.createElement("button");
        btn.className = "number-cell";
        btn.textContent = String(number);
        btn.dataset.number = String(number);
        grid.appendChild(btn);
      });
      document.getElementById("sobrietyStats").textContent = "0.0 c · 0 ошибок";
    }

    document.getElementById("startSobrietyBtn").addEventListener("click", startSobriety);
    document.getElementById("sobrietyGrid").addEventListener("click", function (e) {
      var btn = e.target.closest(".number-cell");
      if (!btn || !state.sobriety.running) return;
      var number = Number(btn.dataset.number);
      if (number === state.sobriety.next) {
        btn.classList.add("done");
        state.sobriety.next += 1;
      } else {
        state.sobriety.errors += 1;
      }
      var seconds = (Date.now() - state.sobriety.startedAt) / 1000;
      document.getElementById("sobrietyStats").textContent = seconds.toFixed(1) + " c · " + state.sobriety.errors + " ошибок";
      if (state.sobriety.next > 20) {
        state.sobriety.running = false;
        var score = Math.max(0, Math.min(100, Math.round(((20 / seconds) - state.sobriety.errors * 0.05) * 100)));
        var player = document.getElementById("sobrietyParticipantSelect").value || "Guest";
        var resultText = tr("sobrietyResult", {name: player, score: score}) + " · " + seconds.toFixed(1) + " c · " + state.sobriety.errors + " ошибок";
        document.getElementById("sobrietyStats").textContent = resultText;
        state.history.unshift({type: "game", amount: score, date: new Date().toLocaleString(localeCode())});
        saveState();
        saveGameResult("sobriety", player, resultText, {
          time_seconds: Number(seconds.toFixed(2)),
          errors: state.sobriety.errors,
          sobriety_index: score
        });
      }
    });

    function newTongue() {
      document.getElementById("tonguePhrase").textContent = tongueTwisters[Math.floor(Math.random() * tongueTwisters.length)];
      apiFetch("/api/tongue-twisters/random")
        .then(function (item) {
          document.getElementById("tonguePhrase").textContent = item.text;
          markBackendOnline();
        })
        .catch(function () {});
      document.getElementById("forfeitValue").textContent = "—";
      state.tongue = {passes: 0, fails: 0};
      saveState();
    }

    document.getElementById("newTongueBtn").addEventListener("click", newTongue);
    document.getElementById("recordTongueBtn").addEventListener("click", function () {
      if (!navigator.mediaDevices || !window.MediaRecorder) {
        notify("Запись недоступна в этом браузере");
        return;
      }
      navigator.mediaDevices.getUserMedia({audio: true}).then(function (stream) {
        recordedChunks = [];
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.addEventListener("dataavailable", function (event) {
          if (event.data.size > 0) recordedChunks.push(event.data);
        });
        mediaRecorder.addEventListener("stop", function () {
          stream.getTracks().forEach(function (track) { track.stop(); });
          var blob = new Blob(recordedChunks, {type: "audio/webm"});
          var audio = document.getElementById("tongueAudio");
          audio.src = URL.createObjectURL(blob);
          audio.hidden = false;
          state.recording.active = false;
          saveState();
        });
        state.recording.active = true;
        mediaRecorder.start();
        notify("Запись началась");
      }).catch(function (error) {
        notify("Микрофон: " + error.message);
      });
    });
    document.getElementById("stopTongueBtn").addEventListener("click", function () {
      if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
        notify("Запись остановлена");
      }
    });
    document.getElementById("tonguePassBtn").addEventListener("click", function () {
      state.tongue.passes += 1;
      document.getElementById("forfeitValue").textContent = state.tongue.passes + ":" + state.tongue.fails;
      saveGameResult(
        "tongue_twister",
        document.getElementById("tongueParticipantSelect").value || state.participants[0],
        "passed: " + document.getElementById("tonguePhrase").textContent,
        {passed: true, phrase: document.getElementById("tonguePhrase").textContent}
      );
      saveState();
    });
    document.getElementById("tongueFailBtn").addEventListener("click", function () {
      state.tongue.fails += 1;
      var forfeit = forfeits[Math.floor(Math.random() * forfeits.length)];
      document.getElementById("forfeitValue").textContent = forfeit;
      var player = document.getElementById("tongueParticipantSelect").value || state.participants[0];
      var phrase = document.getElementById("tonguePhrase").textContent;
      apiFetch("/api/forfeits/random" + (state.companyId ? "?company_id=" + state.companyId : ""))
        .then(function (item) {
          forfeit = item.text;
          document.getElementById("forfeitValue").textContent = forfeit;
          markBackendOnline();
        })
        .catch(function () {})
        .then(function () {
          saveGameResult("tongue_twister", player, "failed: " + phrase + " | forfeit: " + forfeit, {
            passed: false,
            phrase: phrase,
            forfeit: forfeit
          });
        });
      saveState();
    });
  
    loadState();
    renderAll();
    applyTheme();
    newTongue();
    startParticipantsPolling();
    var inviteFromUrl = new URLSearchParams(window.location.search).get("company");
    if (inviteFromUrl && inviteFromUrl !== state.inviteCode) {
      loadBackendCompanyByCode(inviteFromUrl).catch(function () {});
    }
    showScreen("participants");
  })();