# Projekt-Tagebuch – Individual Web Crawler

---

## Anmerkungen

Da es sich um eine Einzelarbeit im Rahmen der Wiederholungsprüfung handelt, gibt es kein Team im klassischen Sinne. Alle Entscheidungen, die Architektur, die Implementierung und das Testing wurden von mir alleine durchgeführt. Statt regulärer Sprint-Meetings habe ich am Ende jeder Phase eine kurze Selbstreflexion gemacht und den aktuellen Stand dokumentiert. Die Kommunikation mit der Betreuerin erfolgte bei Bedarf per E-Mail oder in der Sprechstunde.

Das Projekt wurde von Anfang an so aufgebaut, dass es vollständig containerisiert läuft. Das heißt, man braucht nur Docker installiert zu haben und kann mit einem einzigen Befehl die gesamte Anwendung starten. Das war mir wichtig, weil es die Reproduzierbarkeit sicherstellt und es für die Betreuerin einfacher macht, das Projekt zu testen.

---

## 2. Projekt-Kurzbeschreibung

### Worum geht es?

Das Ziel dieses Projekts ist die Entwicklung eines individuellen Web Crawlers als Full-Stack-Webanwendung. Die Anwendung soll es einem registrierten Benutzer ermöglichen, eine beliebige URL einzugeben und die dahinterliegende Webseite automatisch zu durchsuchen. Dabei wird die Seite bis zu einer wählbaren Tiefe von maximal drei Ebenen gecrawlt. Auf den gefundenen Seiten wird nach PDF-Dokumenten gesucht, diese werden automatisch heruntergeladen und im System gespeichert. Aus jedem PDF werden die zehn häufigsten Wörter extrahiert und dauerhaft gespeichert. Der Benutzer kann anschließend über eine Suchfunktion herausfinden, in welchen seiner PDFs ein bestimmtes Wort vorkommt. Außerdem können aus den gesammelten PDFs Word-Clouds generiert werden – entweder aus einem einzelnen PDF, aus mehreren ausgewählten PDFs oder aus allen PDFs eines bestimmten Zeitraums.

### Deliverables

Am Ende des Projekts sollen folgende Ergebnisse vorliegen:

- Ein funktionsfähiges Backend (REST-API) mit allen elf Features
- Ein React-Frontend mit dreizehn Seiten, das alle Backend-Funktionen über eine Benutzeroberfläche zugänglich macht
- Eine Docker-Compose-Konfiguration, die alle Dienste (Datenbank, Redis, Backend, Worker, Frontend, Mailserver, Demo-Seiten) mit einem Befehl startet
- Automatisierte Tests (74 Tests in 9 Testdateien)
- Diese Projektdokumentation

### Wo liegen die größten Herausforderungen?

Die größte Herausforderung war das asynchrone Crawling. Wenn ein Benutzer einen Crawl-Job startet, darf die API nicht blockieren, sondern muss den Job im Hintergrund verarbeiten. Dafür wird Celery mit Redis als Message-Broker eingesetzt. Die Schwierigkeit liegt darin, dass der Crawler Links verfolgen, Duplikate erkennen und dabei die Tiefenregeln einhalten muss – und das alles zuverlässig im Hintergrund.

Eine weitere Herausforderung war die Textextraktion aus PDFs. Nicht jedes PDF enthält maschinenlesbaren Text, und die Bibliothek PyMuPDF verhält sich bei verschiedenen PDF-Formaten unterschiedlich. Die Top-10-Wortstatistiken mussten außerdem Stoppwörter filtern und korrekt sortiert werden.

### Wo liegt der größte Mehrwert?

Der größte Mehrwert für die Anwenderin liegt darin, dass man PDFs nicht mehr manuell suchen und herunterladen muss. Man gibt einfach eine URL ein, und das System findet automatisch alle PDFs auf der Seite und den verlinkten Unterseiten. Die Wortstatistiken und die Suchfunktion machen es dann möglich, schnell die relevanten Dokumente zu finden, ohne jedes PDF einzeln öffnen zu müssen.

### Scope und Nicht-Ziele

**Im Scope:**
- Benutzerregistrierung und Login mit JWT-Authentifizierung
- Passwort-Reset per E-Mail (mit 60-Sekunden-Token)
- Profilverwaltung (Nickname und E-Mail ändern)
- Web-Crawling mit Tiefe 1–3
- PDF-Erkennung, Download und Speicherung
- Textextraktion und Top-10-Wortstatistiken
- Suchfunktion über Wortstatistiken
- Word-Cloud-Generierung (Single, Multi, Intervall)
- React-Frontend mit allen Funktionen
- Docker-Compose-Setup für alle Dienste

**Nicht-Ziele (explizit ausgeschlossen):**
- Volltextsuche innerhalb der PDFs (es wird nur in den Top-10-Statistiken gesucht)
- Crawling von JavaScript-gerenderten Seiten (SPA)
- Benutzerrollen oder Admin-Bereich
- Mehrsprachigkeit der Benutzeroberfläche
- Mobile App
- Deployment auf einem Cloud-Server (die Anwendung läuft lokal via Docker)

### Umsetzungsansatz

Das Backend wird mit Python 3.11 und FastAPI umgesetzt. Die Datenbank ist PostgreSQL 16, die Hintergrundverarbeitung läuft über Celery mit Redis. Das Frontend wird mit React 18, Vite als Build-Tool und TailwindCSS für das Styling entwickelt. Im Docker-Compose-Setup wird Nginx als Reverse-Proxy eingesetzt, der das Frontend ausliefert und API-Anfragen an das Backend weiterleitet. Für die Passwort-Reset-Funktion wird im Entwicklungsbetrieb MailHog als lokaler Mailserver verwendet. Zum Testen des Crawlers gibt es zwei statische Demo-Webseiten (demo_site und external_site), die als eigene Nginx-Container laufen.

---

## 3. Spezifikation der Lösung

### 3.1 Systemumfeld

Die Anwendung besteht aus folgenden Komponenten, die alle als Docker-Container laufen:

```
┌─────────────────────────────────────────────────────┐
│                    Docker Compose                    │
│                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐       │
│  │ Frontend │───▶│ Backend  │───▶│PostgreSQL│       │
│  │ (Nginx)  │    │ (FastAPI)│    │   (DB)   │       │
│  │ :3000    │    │ :8000    │    │          │       │
│  └──────────┘    └────┬─────┘    └──────────┘       │
│                       │                              │
│                  ┌────▼─────┐    ┌──────────┐       │
│                  │  Worker  │───▶│  Redis   │       │
│                  │ (Celery) │    │ (Broker) │       │
│                  └──────────┘    └──────────┘       │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ MailHog  │  │demo_site │  │ext_site  │          │
│  │ :8025    │  │ :8088    │  │ :8089    │          │
│  └──────────┘  └──────────┘  └──────────┘          │
└─────────────────────────────────────────────────────┘
```

**Systemgrenzen:** Die Anwendung läuft vollständig lokal. Es gibt keine Anbindung an externe Dienste oder Cloud-Infrastruktur. Der Crawler greift auf beliebige im Netzwerk erreichbare Webseiten zu. Für Tests werden die mitgelieferten Demo-Seiten verwendet.

### 3.2 Features (Funktionale Anforderungen)

Die elf Features sind als User Stories formuliert:

**F01 – Registrierung und Login**
*Als Benutzer möchte ich mich mit Nickname, E-Mail und Passwort registrieren und anschließend einloggen können, damit ich meine Crawl-Daten persönlich und geschützt verwalten kann.*
- Validierung: eindeutiger Nickname, eindeutige E-Mail, Passwort mind. 8 Zeichen
- Login mit E-Mail oder Nickname möglich
- JWT-Token wird bei erfolgreichem Login zurückgegeben

**F02 – Profilverwaltung**
*Als Benutzer möchte ich meinen Nickname und meine E-Mail-Adresse einsehen und ändern können.*
- Duplikat-Prüfung bei Änderungen
- Fehlermeldungen bei bereits verwendetem Nickname oder E-Mail

**F03 – Passwort-Reset**
*Als Benutzer möchte ich mein Passwort zurücksetzen können, falls ich es vergessen habe.*
- E-Mail mit Reset-Link wird gesendet (über MailHog im Dev-Modus)
- Token läuft nach 60 Sekunden ab
- Abgelaufene, ungültige und bereits verwendete Tokens werden abgefangen

**F04 – Web-Crawling**
*Als Benutzer möchte ich eine URL und eine Crawl-Tiefe (1–3) angeben und den Crawl-Vorgang starten können.*
- Tiefe 1: Nur die eingegebene URL
- Tiefe 2: Eingegebene URL + Links auf derselben Domain
- Tiefe 3: Wie Tiefe 2 + externe Links (werden aber nicht weiter verfolgt)
- Maximal 200 Seiten pro Job, URL-Deduplizierung

**F05 – Job-Historie**
*Als Benutzer möchte ich alle meine bisherigen Crawl-Jobs mit Status sehen können.*
- Status: queued, running, done, failed
- Sortiert nach Erstellungsdatum (neueste zuerst)
- Bleibt auch nach Seitenwechsel oder Neuanmeldung erhalten

**F06 – PDF-Download und -Speicherung**
*Als Benutzer möchte ich, dass PDFs auf gecrawlten Seiten automatisch gefunden und heruntergeladen werden.*
- PDFs werden unter `/data/pdfs/<user_id>/<job_id>/` gespeichert
- SHA-256-Hash zur Deduplizierung
- Download-Funktion im Frontend

**F07 – PDF-Textextraktion und Top-10-Wörter**
*Als Benutzer möchte ich die zehn häufigsten Wörter jedes PDFs sehen können.*
- Textextraktion mit PyMuPDF
- Stoppwörter werden gefiltert
- Ergebnis wird dauerhaft in der Datenbank gespeichert (nicht bei jedem Aufruf neu berechnet)

**F08 – Suche über Wortstatistiken**
*Als Benutzer möchte ich nach einem Wort suchen und alle PDFs finden, die dieses Wort in ihren Top-10-Statistiken haben.*
- Keine Volltextsuche, sondern Suche in den gespeicherten Top-10-Listen
- Ergebnis zeigt PDF-Quelle, Download-Datum und Links zu Stats/Download

**F09 – Word-Cloud (einzelnes PDF)**
*Als Benutzer möchte ich aus einem einzelnen PDF eine Word-Cloud generieren können.*

**F10 – Word-Cloud (mehrere PDFs)**
*Als Benutzer möchte ich mehrere PDFs auswählen und daraus eine gemeinsame Word-Cloud generieren können.*
- Mindestens 2 PDFs müssen ausgewählt werden

**F11 – Word-Cloud (Zeitintervall)**
*Als Benutzer möchte ich einen Zeitraum angeben und aus allen in diesem Zeitraum heruntergeladenen PDFs eine Word-Cloud generieren können.*
- Datum-/Zeitauswahl mit Sekundengenauigkeit
- Filtert nach `downloaded_at` des PDFs

### 3.3 Schnittstellen (REST-API)

Alle Endpunkte verwenden JSON. Authentifizierte Endpunkte erwarten einen `Authorization: Bearer <token>` Header.

| Methode | Endpunkt | Auth | Beschreibung |
|---------|----------|------|--------------|
| POST | /auth/register | Nein | Benutzer registrieren |
| POST | /auth/login | Nein | Einloggen, JWT erhalten |
| POST | /auth/forgot-password | Nein | Reset-E-Mail senden |
| POST | /auth/reset-password | Nein | Passwort zurücksetzen |
| GET | /me | Ja | Eigenes Profil abrufen |
| PUT | /me | Ja | Profil bearbeiten |
| POST | /crawl/jobs | Ja | Neuen Crawl-Job starten |
| GET | /crawl/jobs | Ja | Alle eigenen Jobs auflisten |
| GET | /crawl/jobs/{id} | Ja | Job-Details abrufen |
| GET | /crawl/jobs/{id}/pages | Ja | Gecrawlte Seiten eines Jobs |
| GET | /crawl/jobs/{id}/pdfs | Ja | Gefundene PDFs eines Jobs |
| GET | /pdfs/ | Ja | Alle eigenen PDFs auflisten |
| GET | /pdfs/{id} | Ja | PDF-Details |
| GET | /pdfs/{id}/download | Ja | PDF herunterladen |
| GET | /pdfs/{id}/stats/top-words | Ja | Top-10-Wörter abrufen |
| GET | /search/top-words?word=X | Ja | Wort in Statistiken suchen |
| POST | /wordclouds/single | Ja | Word-Cloud aus 1 PDF |
| POST | /wordclouds/multi | Ja | Word-Cloud aus mehreren PDFs |
| POST | /wordclouds/interval | Ja | Word-Cloud aus Zeitraum |
| GET | /wordclouds/{id}/image | Ja | Word-Cloud-Bild abrufen |

**Fehlerformat:**
```json
{
  "detail": {
    "error": {
      "code": "invalid_credentials",
      "message": "Wrong email/nickname or password",
      "http_status": 401
    }
  }
}
```

### 3.4 Datenmodell

Die Datenbank besteht aus sieben Tabellen:

```
┌──────────┐       ┌───────────────────┐
│  users   │──1:N──│password_reset_    │
│          │       │tokens             │
└────┬─────┘       └───────────────────┘
     │
     ├──1:N──┌──────────────┐
     │       │  crawl_jobs  │──1:N──┌──────────────┐
     │       │              │       │crawled_pages │
     │       └──────┬───────┘       └──────────────┘
     │              │
     │              │──1:N──┌───────────────┐──1:1──┌──────────────────┐
     │              │       │pdf_documents  │       │pdf_top_words_    │
     ├──1:N─────────┘       │               │       │stats             │
     │                      └───────┬───────┘       └──────────────────┘
     │                              │
     │                              │ N:M
     │       ┌──────────────────┐   │
     ├──1:N──│wordcloud_        │───┘
             │artifacts         │
             └──────────────────┘
```

### 3.5 Qualitätseigenschaften (Nicht-Funktionale Anforderungen)

- **Performance:** Crawl-Jobs laufen asynchron im Hintergrund. Die API bleibt immer reaktionsfähig. Im Frontend wird der Job-Status alle 2 Sekunden automatisch aktualisiert.
- **Sicherheit:** Passwörter werden mit bcrypt gehasht. JWT-Tokens laufen nach 24 Stunden ab. Jeder Benutzer sieht nur seine eigenen Daten (Ownership-Prüfung auf jedem Endpunkt). Reset-Tokens sind einmalig verwendbar und laufen nach 60 Sekunden ab.
- **Zuverlässigkeit:** Maximale Seitenzahl pro Job (200) verhindert endlose Crawls. URL-Deduplizierung vermeidet Schleifen. Wortstatistiken werden einmalig berechnet und dauerhaft gespeichert.
- **Benutzbarkeit:** Übersichtliches, modernes UI mit TailwindCSS. Klare Fehlermeldungen bei Validierungsfehlern. Status-Badges mit Farbkodierung (grau=wartend, gelb=läuft, grün=fertig, rot=fehlgeschlagen).
- **Portabilität:** Die gesamte Anwendung läuft in Docker-Containern. Keine manuelle Installation von Abhängigkeiten nötig.

---

## 4. Aufwandschätzung

Da es sich um eine Einzelarbeit handelt, wurde der Aufwand mithilfe einer analogen Schätzung ermittelt: Für jedes Feature habe ich den Aufwand auf Basis der erwarteten Komplexität und meiner Erfahrung mit ähnlichen Aufgaben aus früheren Projekten geschätzt. Eine formale Delphi-Schätzung mit mehreren unabhängigen Experten ist bei einem Ein-Personen-Projekt methodisch nicht durchführbar. Stattdessen habe ich die initiale Schätzung in einem zweiten Durchgang kritisch überprüft und Puffer für technische Risiken (z.B. Kompatibilitätsprobleme bei Bibliotheken, asynchrone Verarbeitung) eingeplant.

| Phase | Features | Geschätzter Aufwand | Tatsächlicher Aufwand |
|-------|----------|--------------------|-----------------------|
| Phase 1: Fundament | Docker-Setup, DB-Modell, Auth (F01), Profil (F02), Passwort-Reset (F03) | 30 Std. | ~28 Std. |
| Phase 2: Kern-Features | Crawling (F04), Job-Historie (F05), PDF-Download (F06), Celery-Tasks | 35 Std. | ~38 Std. |
| Phase 3: Analyse & Suche | Textextraktion (F07), Suche (F08), Word-Clouds (F09, F10, F11) | 30 Std. | ~27 Std. |
| Phase 4: Frontend & Abschluss | React-Frontend (13 Seiten), E2E-Tests, Dokumentation | 25 Std. | ~30 Std. |
| **Gesamt** | | **120 Std.** | **~123 Std.** |

Die Schätzung hat sich als ziemlich genau herausgestellt. Die größte Abweichung gab es bei Phase 2 (Crawling), weil die Tiefenregeln und die Deduplizierung komplexer waren als anfangs gedacht. Dafür ging Phase 3 etwas schneller, weil die Datenbankstruktur aus Phase 2 bereits gut vorbereitet war. Phase 4 hat etwas länger gedauert als geplant, weil das Zusammenspiel zwischen Frontend und Backend (CORS, Proxy-Konfiguration, Trailing-Slash-Redirects) einige unerwartete Probleme verursacht hat.

---

## 5. Auslieferung

### 5.1 Lieferumfang

- **Source-Code:** Vollständiger Quellcode für Backend und Frontend im Git-Repository
- **Docker-Konfiguration:** `docker-compose.yml` mit allen acht Diensten
- **Dokumentation:** Diese Projektdokumentation, Feature-Spezifikationen, API-Vertrag, Datenmodell, Architektur-Dokument
- **Tests:** 74 automatisierte Tests in 9 Testdateien
- **Demo-Seiten:** Statische Webseiten zum Testen des Crawlers

### 5.2 Repository-Struktur

```
web_crawler/
├── Backend/
│   ├── app/
│   │   ├── api/routers/     # 7 Router-Dateien
│   │   ├── core/            # Config, Security, Celery
│   │   ├── db/              # Datenbankverbindung
│   │   ├── models/          # 5 ORM-Modelle
│   │   ├── schemas/         # Pydantic-Schemas
│   │   ├── services/        # 7 Service-Dateien
│   │   ├── tasks/           # 3 Celery-Task-Dateien
│   │   └── storage/         # Dateipfad-Verwaltung
│   ├── tests/               # 9 Testdateien
│   ├── Dockerfile
│   └── requirements.txt
├── Frontend/
│   ├── src/
│   │   ├── api/             # 7 API-Module
│   │   ├── components/      # UI- und Layout-Komponenten
│   │   ├── context/         # AuthContext
│   │   ├── hooks/           # useAuth, usePolling
│   │   └── pages/           # 13 Seiten
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── demo_site/               # Test-Webseite für Crawling
├── external_site/           # Externe Links-Simulation
├── docs/                    # Projektdokumentation
└── docker-compose.yml
```

### 5.3 Verwendete Bibliotheken und Lizenzen

| Bibliothek | Lizenz | Verwendungszweck |
|------------|--------|------------------|
| FastAPI | MIT | Web-Framework (Backend) |
| SQLAlchemy | MIT | ORM (Datenbankzugriff) |
| Celery | BSD | Hintergrundverarbeitung |
| PyMuPDF | AGPL-3.0 | PDF-Textextraktion |
| WordCloud | MIT | Word-Cloud-Generierung |
| React | MIT | Frontend-Framework |
| TailwindCSS | MIT | CSS-Framework |
| Vite | MIT | Frontend-Build-Tool |
| PostgreSQL | PostgreSQL License | Datenbank |
| Redis | BSD | Message-Broker |
| Nginx | BSD-2-Clause | Reverse-Proxy |

**Hinweis:** PyMuPDF steht unter der AGPL-3.0-Lizenz. Für ein akademisches Projekt ist das unproblematisch, bei kommerzieller Nutzung müsste man entweder eine kommerzielle Lizenz erwerben oder eine alternative Bibliothek verwenden.

### 5.4 Hardware-Anforderungen

- Docker Desktop (Windows, macOS oder Linux)
- Mindestens 4 GB RAM (für alle Container gleichzeitig)
- Ca. 2 GB Festplattenspeicher für Docker-Images

### 5.5 Installationsanleitung

```bash
# 1. Repository klonen
git clone https://github.com/direncanS/Invidual-Web-Crawler.git
cd Invidual-Web-Crawler

# 2. Alle Dienste starten
docker compose up -d --build

# 3. Warten bis alles bereit ist (ca. 30-60 Sekunden)
# Dann im Browser öffnen:
#   Frontend:  http://localhost:3000
#   API-Docs:  http://localhost:8000/docs
#   MailHog:   http://localhost:8025
```

Zum Stoppen:
```bash
docker compose down        # Container stoppen
docker compose down -v     # Container stoppen + Daten löschen
```

---

## 6. Unser Projekt-Tagebuch

### Phase 1: Fundament (06.03. – 14.03.2026)

**06.03. – Projektstart und Setup**

Heute habe ich mit dem Projekt angefangen. Zuerst habe ich die Aufgabenstellung genau durchgelesen und mir Notizen gemacht, welche Features gefordert sind. Dann habe ich das Docker-Compose-Setup aufgebaut: PostgreSQL, Redis, MailHog und das Backend als FastAPI-Anwendung. Das Datenbankmodell habe ich direkt mit SQLAlchemy definiert – sieben Tabellen mit den richtigen Beziehungen.

Ein Problem gab es gleich am Anfang: Die `entrypoint.sh` hatte Windows-Zeilenumbrüche (CRLF), und der Linux-Container konnte sie nicht ausführen. Die Lösung war ein `sed -i 's/\r$//'` im Dockerfile. Das hat mich eine halbe Stunde gekostet, bis ich drauf gekommen bin.

**08.03. – Authentifizierung**

Register und Login funktionieren jetzt. Bei der Passwort-Hashierung gab es ein Kompatibilitätsproblem: `passlib` funktioniert nicht mit `bcrypt >= 4.1`. Ich musste `bcrypt==4.0.1` pinnen. Das war frustrierend, weil die Fehlermeldung nicht besonders aussagekräftig war – ich habe bestimmt eine Stunde gesucht, bis ich den GitHub-Issue dazu gefunden habe.

**10.03. – Passwort-Reset und Profil**

Die Passwort-Reset-Funktion mit 60-Sekunden-Token läuft. MailHog fängt die E-Mails ab, sodass man den Reset-Link dort sehen kann. Beim Testen ist mir aufgefallen, dass der `email-validator` Domains wie `.local` ablehnt. In den Tests verwende ich jetzt immer `@example.com`.

Das Profil (GET/PUT /me) war relativ unkompliziert. Die Duplikat-Prüfung für Nickname und E-Mail funktioniert, mit klaren Fehlermeldungen.

**12.03. – Tests für Phase 1**

Ich habe die Tests für Auth, Passwort-Reset und Profil geschrieben. Dabei habe ich SAVEPOINT-Isolation verwendet, damit jeder Test eine saubere Datenbank hat. Am Ende von Phase 1 stehen 28 Tests, alle grün.

---

### Phase 2: Kern-Features (17.03. – 21.03.2026)

**17.03. – Crawling-Grundstruktur**

Heute habe ich den Celery-Worker aufgesetzt und die erste Version des Crawlers geschrieben. Der Worker nimmt Jobs aus der Redis-Queue und verarbeitet sie im Hintergrund. Das Grundprinzip funktioniert: URL eingeben, Job wird erstellt, Worker crawlt die Seite.

Ein Problem: `celery.autodiscover_tasks(["app.tasks"])` hat die Task-Dateien nicht gefunden, weil sie nicht `tasks.py` heißen sondern `crawl_tasks.py` usw. Die Lösung war, die Module explizit in `celery.conf.include` aufzulisten.

**18.03. – Tiefenregeln**

Die Tiefenregeln waren komplizierter als gedacht. Tiefe 1 ist einfach (nur die Start-URL), aber bei Tiefe 2 und 3 muss man zwischen Same-Domain und External-Domain Links unterscheiden. Externe Links werden bei Tiefe 3 zwar besucht, aber nicht weiter verfolgt. Dazu kommt die URL-Deduplizierung, damit man nicht in Schleifen gerät. Ich habe ein Set für bereits besuchte URLs verwendet.

**19.03. – Demo-Seiten**

Um den Crawler deterministisch testen zu können, habe ich zwei statische Webseiten als Nginx-Container aufgesetzt: `demo_site` (mit internen Links und einem PDF) und `external_site` (für externe Link-Tests). Die `demo_site` hat eine klare Struktur: `index.html` verlinkt auf `level2_a.html` und `level2_b.html`, und dort gibt es einen Link zu `sample.pdf`.

Das `sample.pdf` muss ein echtes PDF sein – PyMuPDF braucht ein gültiges PDF-Format für die Textextraktion. Ein leeres Dummy-File reicht nicht.

**20.03. – PDF-Download und Job-Historie**

PDFs werden jetzt automatisch erkannt und heruntergeladen. Die Speicherung erfolgt unter `/data/pdfs/<user_id>/<job_id>/`. Die Job-Historie zeigt alle bisherigen Jobs mit Status-Badges. Die API unterstützt Polling, damit der Job-Status in Echtzeit abgefragt werden kann.

**21.03. – Tests für Phase 2**

Tests für Crawling, Historie und PDF-Download geschrieben. Insgesamt jetzt 52 Tests. Ein Stolperstein: Celery-Tasks müssen in Tests gepatcht werden. Der Patch-Pfad ist `app.tasks.crawl_tasks.crawl_website.delay`, nicht der importierte Name.

---

### Phase 3: Analyse & Suche (24.03. – 27.03.2026)

**24.03. – Textextraktion und Top-10-Wörter**

Die Textextraktion mit PyMuPDF funktioniert gut. Stoppwörter (englische und deutsche) werden gefiltert. Die Ergebnisse werden als JSON in der `pdf_top_words_stats`-Tabelle gespeichert. Wenn ein Benutzer die Statistiken abruft und sie noch nicht berechnet wurden, gibt die API einen 409-Status zurück.

**25.03. – Suchfunktion**

Die Suche über `GET /search/top-words?word=X` durchsucht die gespeicherten Top-10-Listen aller PDFs des Benutzers. Das ist keine Volltextsuche, sondern eine gezielte Suche in den vorberechneten Statistiken. Das Ergebnis zeigt PDF-Quelle, Download-Datum und Links zu Stats/Download.

**26.03. – Word-Cloud-Generierung**

Drei Modi implementiert: Single (1 PDF), Multi (2+ PDFs), Interval (Zeitraum). Die Word-Cloud-Bilder werden als PNG gespeichert. Die Generierung läuft asynchron über Celery.

Beim Interval-Modus muss man aufpassen: Der Filter geht nach `downloaded_at` des PDFs, nicht nach `created_at` des Jobs. Die Zeitauswahl soll sekundengenau sein, damit man den gewünschten Zeitraum präzise eingrenzen kann.

**27.03. – Tests für Phase 3**

Tests für PDF-Stats, Suche und Word-Clouds geschrieben. 74 Tests insgesamt, alle grün.

---

### Phase 4: Frontend & Abschluss (28.03. – 01.04.2026)

**28.03. – React-Projekt und Grundstruktur**

Vite-Projekt erstellt, TailwindCSS konfiguriert, React Router eingerichtet. Der AuthContext verwaltet den JWT-Token und den Benutzer-Status. Der Axios-Client hat einen Interceptor, der automatisch den Token an jede Anfrage hängt.

13 Seiten erstellt: Landing, Register, Login, ForgotPassword, ResetPassword, Dashboard, Profile, NewCrawl, JobDetail, PdfStats, Search, Wordclouds, NotFound.

**29.03. – Nginx-Proxy und CORS**

Das war schwieriger als erwartet. Im Docker-Setup leitet Nginx `/api/`-Anfragen an das Backend weiter. Das funktioniert grundsätzlich, aber FastAPI macht bei manchen Endpunkten automatische Redirects (z.B. `/pdfs` -> `/pdfs/`), und die Redirect-URL geht dann an die falsche Adresse. Die Lösung war, in den API-Aufrufen konsistent Trailing-Slashes zu verwenden.

Außerdem musste ich CORS-Middleware im Backend hinzufügen, damit der Vite-Dev-Server (der auf einem anderen Port läuft) auf die API zugreifen kann.

**30.03. – End-to-End Smoke Test**

Ich habe ein Python-Skript geschrieben, das den kompletten Flow testet: Register -> Login -> Crawl starten -> Job-Polling -> PDF-Stats -> Suche -> Word-Cloud -> Profil-Update -> History-Persistenz -> Auth-Schutz. Alle 24 Tests bestanden.

**31.03. – Dokumentation und letzte Korrekturen**

Projektdokumentation geschrieben. Kleinere UI-Verbesserungen (bessere Fehlermeldungen, Loading-States). Repository aufgeräumt und auf GitHub gepusht.

**01.04. – Abgabe**

Letzter Check: `docker compose down -v && docker compose up -d --build`, alle Funktionen durchgetestet, Dokumentation finalisiert, abgegeben.

---

### Rückblick

Was gut lief:
- Docker-Setup von Anfang an hat viel Zeit gespart
- Die klare Trennung von Routers, Services und Models hat den Code übersichtlich gehalten
- Die Demo-Seiten machen das Testen reproduzierbar

Was ich nächstes Mal anders machen würde:
- Früher mit dem Frontend anfangen, nicht erst in der letzten Phase
- Nginx-Proxy-Konfiguration vorher testen, bevor alle Seiten fertig sind
- Mehr Zeit für die Dokumentation einplanen
