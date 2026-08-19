[English](README.md) | Deutsch | [Español](README.es.md) | [Français](README.fr.md) | [Polski](README.pl.md) | [Čeština](README.cs.md) | [Norsk](README.no.md)

# VEVOR-Schneideplotter-Treiber für macOS — CH554_CDC / USB 0483:5750

**VEVOR Schneideplotter wird am Mac nicht erkannt oder schneidet nicht?** Dieses kostenlose Open-Source-Projekt verbindet VEVOR- und Anhui-Anyu-Schneideplotter über USB direkt mit [Inkcut](https://github.com/inkcut/inkcut) — ohne SignCut-Abo, ohne Windows-VM. Reiner User-Space-Treiber (libusb/pyusb), keine Kernel-Erweiterung.

## 10-Sekunden-Kompatibilitätscheck

Im Terminal ausführen:

```bash
system_profiler SPUSBDataType | grep -B 1 -A 5 "CH554"
```

Wenn `CH554_CDC`, `Vendor ID: 0x0483` und `Product ID: 0x5750` erscheinen, ist Ihr Plotter das richtige Gerät für dieses Projekt. Dieselbe USB-Kennung nutzen viele Marken: VEVOR (KH/KI/KW/SK-Serien), Secabo, GoldCut, HELITIN, JinKa, SAGA, US Cutter u. a. Bestätigt getestet ist bislang der VEVOR KH-870 — weitere Geräteberichte sind willkommen (GitHub Issues).

## Typische Probleme unter macOS

- Plotter erscheint im USB-Baum, aber **kein serieller Port** (`/dev/cu.*`) — normal bei dieser Hardware, macOS legt für Printer-Class-Geräte keinen an
- Schlittenwagen **fährt einmal an und bleibt stehen**
- Motive werden **übereinander geschnitten** (doppelte Schnitte)
- Gerät funktioniert nach dem Einschalten, **stirbt im Leerlauf** bis zum nächsten Aus-/Einschalten

## Was dahintersteckt (Kurzfassung)

Die Firmware ist eine CDC-Schnittstelle im Printer-Class-Gewand: Sie schneidet erst, wenn `SET_LINE_CODING` (9600 8N1) gesendet und **DTR/RTS** gesetzt sind. Der CH554-USB-Stack stürzt beim Ruhezustand des Ports ab (Abhilfe: Keep-alive alle 15 s). Die native Sprache ist **DMPL** (0,025 mm/Schritt), nicht HPGL. Der interne Puffer ist winzig — Daten müssen im Schneidetempo gesendet werden.

Vollständige technische Dokumentation und Status: [englische Hauptseite](README.md) · [Protokoll-Details](docs/PROTOCOL.md) · [Fehlersuche](docs/TROUBLESHOOTING.md)

> **Hinweis:** Pre-Release — noch kein fertiger Installer. Repo beobachten („Watch") für die erste getestete Anleitung.

⭐ Läuft dein Plotter jetzt? Ein Stern auf GitHub hilft anderen Mac-Nutzern, dieses Projekt zu finden.

*Suchbegriffe: VEVOR Schneideplotter Mac, Schneideplotter macOS Treiber, VEVOR Plotter Software kostenlos, CH554_CDC, SignCut Alternative, Inkcut Anleitung deutsch, Secabo GoldCut JinKa Mac.*
