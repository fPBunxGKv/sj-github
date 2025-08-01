## Doku
[Anmelde Prozess](docs/drawio/SJ_Anmeldung_Ablauf-Anmeldung.drawio.svg)  
[Mail Versand](docs/drawio/SJ_Anmeldung_Ablauf-Mailversand.drawio.svg)  
...  

## Entwicklung
### Datenbank
- [ ] SQLite - oder andere?
- [ ] Schema i.o.?
...  
### Printing
[python-escpos](https://python-escpos.readthedocs.io/en/latest/index.html)

## Installation
- sj_event anlegen falls noch keines vorhanden ist
- Fake/Testdaten erstellen (manuel anstossen) - falls für das aktive event keine daten vorhanden sind
...

## Anmeldung
- [x] Daten prüfen
- [x] Doppelte Anmeldungen erkennen (Name,Vorname,Jahrgang,...)
- [x] Life suche über alle User -> Laufzettel drucken
...  

## Event
- [x] Drucken der Laufzettel / Zettel für Wäscheleine
    - [ ] Drucker Typ: Epson TM-T88II
    - [ ] Drucker Typ: EPSON TM-T20II  

- [ ] Nur X Vorläufe zulassen (schon bei der Einteilung am Start)
- [x] 2x gleiche Startnummer pro Lauf nicht zulassen (doppel scan)
- [ ] bisherige Zeiten beim Zeiterfassen anzeigen
- [ ] 

- [ ] Nach den Vorläufen die Finalläufe generieren
    - [ ] Vorläufe sperren
    - [x] Für die besten vier pro Kategorie ein "Resultat" mit status SFR

## Auswertung
- [x] Ranglisten für das aktive Event generieren
- [ ] Ranglisten pro Event und nicht nur für aktuelles
...  

## Admin Seite
- [ ] Benutzer / Gruppen Verwaltung
- [ ] TeilnehmerIn anmelden -> Bestätigungs-Mail auslösen
- [ ] Event Verwaltung
- Ranglisten
    - [ ] evtl. an alle TeilnehmerInnen mailen
    - [ ] Email Adressen aller TeilnehmerInnen ausgeben für Abschlussmail (oder direkt aus der Webpage personalisiert)
...  

# Version 2
- [ ] Stoppen mit dem Mobile (Browser im fullscreen)
    - regisrtieren via unique QR Code pro Bahn
- [ ] Helfer Management
    - DB Schema?
    - Anfragen per Mail, mit Bestätigungslink Ja/Nein
    - Einsatzplan generieren
    - Bestätigen per Mail

# Version 2.1
- [ ] Mandantenfähig