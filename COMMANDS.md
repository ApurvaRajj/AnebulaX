# AnebulaX — Complete Command Reference Manual

AnebulaX supports voice and text commands matched via intelligent word-set scoring with natural phrasing. Commands can also be chained using `and` or `then` (e.g. `open youtube and volume 50`).

---

## 1. Antigravity AI & Nova Integration

Prefix any command with `nova` to query Google Antigravity AI.

| Action | Example Trigger Phrasings | Description |
|---|---|---|
| **Query Antigravity AI** | `nova what is quantum entanglement`, `ask nova explain rust traits`, `hey nova write a python script` | Queries Antigravity AI (via `agy ask` or API fallback) |
| **Cheapest AI Model** | `use cheapest model`, `switch to cheapest model`, `set model cheapest`, `use flash lite`, `fastest model` | Switches active model to `flash_lite` (fast, lightweight) |
| **Better AI Model** | `use better model`, `switch to better model`, `set model better`, `use flash model`, `balanced model` | Switches active model to `flash` (balanced standard) |
| **Best AI Model** | `use best model`, `switch to best model`, `set model best`, `use pro model`, `smartest model` | Switches active model to `pro` (deep reasoning) |
| **Show Current Model** | `show ai model`, `current model`, `which model are you using`, `what ai model` | Displays currently active Antigravity model |

---

## 2. Voice & Audio Configuration

| Action | Example Trigger Phrasings | Description |
|---|---|---|
| **Voice Mode** | `voice`, `listen`, `start voice`, `stop listening`, `exit voice` | Starts or stops the hands-free voice loop |
| **Microphone Diagnostic** | `test mic`, `mic test`, `check mic`, `microphone test` | Runs 5-step diagnostic (deps, PyAudio, devices, energy, STT) |
| **List Microphones** | `list mics`, `show microphones`, `list audio devices` | Enumerates available microphone indices |
| **Select Microphone** | `set mic 0`, `select mic 1`, `set mic default` | Sets active microphone input device |
| **Energy Threshold** | `set energy 300`, `energy threshold 150`, `voice sensitivity 200` | Adjusts mic threshold (50–3000; lower = more sensitive) |
| **Dynamic Energy Toggle** | `set dynamic on`, `set dynamic off`, `toggle dynamic` | Automatically adjusts energy threshold to room noise |
| **STT Engine** | `set stt google`, `set stt vosk`, `switch stt` | Switches between online (Google) and offline (Vosk) |
| **STT Status** | `stt status`, `speech status`, `stt info` | Displays current speech recognition configuration |
| **Mute / Unmute Voice** | `toggle tts`, `mute voice`, `unmute voice`, `silence` | Enables or disables spoken audio responses |

---

## 3. System & Hardware Control

| Action | Example Trigger Phrasings | Description |
|---|---|---|
| **Volume Up / Down** | `volume up`, `louder`, `increase volume`, `volume down`, `quieter` | Steps system volume up or down |
| **Set Exact Volume** | `set volume to 50`, `volume 75`, `volume max`, `max volume` | Sets volume to a specific percentage |
| **Mute / Unmute** | `mute`, `unmute`, `silence volume`, `restore sound` | Toggles audio mute |
| **Brightness Up / Down** | `increase brightness`, `raise brightness`, `dim screen`, `lower brightness` | Adjusts display brightness |
| **Set Brightness** | `set brightness to 80`, `brightness 50` | Sets exact screen brightness level |
| **Screenshot** | `screenshot`, `take screenshot`, `capture screen`, `snip` | Captures screen to Pictures directory |
| **Lock Screen** | `lock screen`, `lock computer`, `lock workstation` | Secures and locks the active session |
| **Power Operations** | `shutdown`, `restart computer`, `sleep`, `log out` | Performs power actions with voice/text confirmation |
| **System Info & Battery** | `system info`, `battery status`, `uptime`, `hostname`, `cpu usage` | Reports system health and hardware diagnostics |
| **Task Manager** | `task manager`, `open task manager`, `processes` | Launches system task manager / process monitor |

---

## 4. Web Browsing & Navigation

| Action | Example Trigger Phrasings | Description |
|---|---|---|
| **Direct Site Opening** | `open youtube`, `go to reddit`, `open canva`, `netflix`, `open github` | Opens popular sites directly in configured browser |
| **Web Search** | `search google for recipes`, `search python tutorials`, `search duckduckgo for news` | Performs search using configured or stated engine |
| **Site-Specific Searches** | `in youtube search lofi beats`, `in claude search async python`, `in gemini search android` | Performs targeted search within specific platforms |
| **Browser Tab Control** | `new tab`, `close tab`, `refresh tab`, `reopen tab`, `next tab`, `previous tab` | Sends cross-platform hotkeys to active browser window |
| **Smart URL Parsing** | `open example.com`, `go to messages.google.com/web` | Resolves and opens arbitrary domain names |

---

## 5. Bookmarks & Custom Software Registry

All stored in user home directory (`~/.anebulax_bookmarks.json`, `~/.anebulax_software.txt`).

| Action | Example Trigger Phrasings | Description |
|---|---|---|
| **List Bookmarks** | `list bookmarks`, `show bookmarks` | Displays all custom saved URLs |
| **Add Bookmark** | `add bookmark wiki https://wikipedia.org`, `save bookmark docs https://docs.python.org` | Adds custom quick-launch bookmark |
| **Delete Bookmark** | `delete bookmark wiki`, `remove bookmark docs` | Deletes bookmark from registry |
| **List Custom Apps** | `list software`, `show custom software` | Displays hot-reloaded software paths |
| **Launch App** | `open chrome`, `open vscode`, `open spotify`, `open terminal` | Launches registered application binary |

---

## 6. Productivity, Notes & Reminders

| Action | Example Trigger Phrasings | Description |
|---|---|---|
| **Set Reminder** | `remind me in 10 minutes to stretch`, `remind me in 1 hour to check email` | Saves reminder to disk and fires background alarm |
| **List Reminders** | `show reminders`, `list reminders` | Displays upcoming and past reminders |
| **Quick & Structured Notes**| `note meeting at 4pm`, `read notes`, `clear notes` | Writes and retrieves persisted notes |
| **Todo Lists** | `todo add finish report`, `show todos`, `clear todos` | Manages persistent task lists |
| **Timers & Alarms** | `set timer 5 minutes`, `timer 30 seconds`, `pomodoro` | Starts countdown timer with notification |
| **World Clock & Date** | `what time is it`, `current date`, `days until christmas`, `week number` | Instant date, time, and timezone utilities |

---

## 7. Developer & Terminal Utilities

| Action | Example Trigger Phrasings | Description |
|---|---|---|
| **Git Commands** | `git status`, `git diff`, `git log`, `git branch`, `git commit` | Runs local repository queries |
| **Docker Operations** | `docker ps`, `docker images`, `docker build` | Inspects container status |
| **Python & Package Tools** | `pip list`, `python version`, `format python file` | Python developer helpers |
| **Network Diagnostics** | `my ip`, `local ip`, `public ip`, `ping google.com`, `check wifi` | Analyzes network connectivity |

---

## 8. Math, Solvers & Conversions

| Action | Example Trigger Phrasings | Description |
|---|---|---|
| **Direct Arithmetic** | `50 + 20`, `(12 * 4) / 3`, `2^8`, `sqrt(144)` | Fast expression solver |
| **Algebra & Calculus** | `solve 2*x + 5 = 15`, `derivative of x^3`, `integral of sin(x)` | SymPy symbolic solver |
| **Number Theory** | `is 17 prime`, `fibonacci 10`, `prime factors 60`, `gcd of 24 and 36` | Primes, factors, sequences |
| **Unit & Currency Math** | `convert 5 miles to km`, `100 usd to eur`, `split bill 120 4` | Conversion and financial calculations |

---

## 9. Text Manipulation & Tools

| Action | Example Trigger Phrasings | Description |
|---|---|---|
| **Case & Format** | `uppercase hello`, `lowercase TEST`, `slugify title text`, `snake case hello world` | String casing transformations |
| **Encoders & Hashes** | `base64 encode secret`, `base64 decode c2VjcmV0`, `hash text mypass` | Crypto and encoding utilities |
| **Text Metrics** | `word count in hello world`, `character count in text`, `spelling check receive` | Text analysis tools |

---

## 10. Fun, Facts & Entertainment

| Action | Example Trigger Phrasings | Description |
|---|---|---|
| **Jokes & Facts** | `tell me a joke`, `tell me a fact`, `quote of the day`, `give me an affirmation` | Entertainment and trivia |
| **Games & Chance** | `flip a coin`, `roll a dice`, `magic 8 ball will it rain`, `tell me a riddle` | Decision makers and games |

---

*AnebulaX — Engineered for high-speed voice and offline system control.*
