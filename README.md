# molbox_tester

Ein Python-Tool, das periodisch Befehle über Telnet an einen Host sendet und die Antworten logged.

## Features

- Sendet alle 2 Sekunden (konfigurierbar) einen Befehl über Telnet
- Logged alle Antworten mit Zeitstempel
- Automatisches Timeout-Handling (10 Sekunden)
- Automatisches Reconnect bei Timeout oder Verbindungsabbruch
- Konfigurierbar über ~/.molbox_tester

## Anforderungen

- Python 3.8 oder höher
- telnetlib3 (wird automatisch bei der Installation installiert)

## Installation

```bash
pip install .
```

Oder für Entwicklung:

```bash
pip install -e .
```

## Konfiguration

Erstelle eine Datei `~/.molbox_tester` mit folgendem Inhalt:

```ini
[molbox]
host = localhost
port = 23
interval = 2.0
command = ALLR
timeout = 10
```

Alle Parameter sind optional. Defaults:
- host: localhost
- port: 23
- interval: 2.0 (Sekunden)
- command: ALLR
- timeout: 10 (Sekunden)

## Verwendung

Nach der Installation:

```bash
molbox
```

Das Tool läuft kontinuierlich und sendet alle `interval` Sekunden den konfigurierten Befehl.

Zum Beenden: Ctrl+C

## Beispiel

```bash
$ molbox
2025-12-10 10:00:00,000 - INFO - Loading configuration from /home/user/.molbox_tester
2025-12-10 10:00:00,001 - INFO - Starting molbox_tester...
2025-12-10 10:00:00,001 - INFO - Configuration: host=192.168.1.100, port=23, interval=2.0s, command=ALLR, timeout=10s
2025-12-10 10:00:00,002 - INFO - Connecting to 192.168.1.100:23...
2025-12-10 10:00:00,150 - INFO - Connected successfully
2025-12-10 10:00:00,151 - INFO - Sent: ALLR
2025-12-10 10:00:00,250 - INFO - Received: OK
2025-12-10 10:00:02,251 - INFO - Sent: ALLR
2025-12-10 10:00:02,350 - INFO - Received: OK
```

## Erstellen von Binärdateien

Um eine eigenständige ausführbare Datei (.exe für Windows oder Binary für Linux) zu erstellen:

```bash
python build.py
```

Das Build-Script:
- Installiert automatisch PyInstaller
- Installiert alle erforderlichen Abhängigkeiten
- Erstellt eine eigenständige ausführbare Datei im `dist/` Verzeichnis

### Plattformen

- **Windows**: Erzeugt `dist/molbox.exe`
- **Linux**: Erzeugt `dist/molbox`

Die erstellte Datei kann ohne Python-Installation ausgeführt werden und enthält alle notwendigen Abhängigkeiten.

### Hinweise

- Das Build-Script muss auf der Zielplattform ausgeführt werden (Windows-Binary auf Windows, Linux-Binary auf Linux)
- Die erstellten Binaries sind groß (~10-20 MB), da sie Python und alle Abhängigkeiten enthalten
- Nach dem Build können Sie die Datei aus dem `dist/` Verzeichnis kopieren und verwenden
