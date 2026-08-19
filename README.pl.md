[English](README.md) | [Deutsch](README.de.md) | [Español](README.es.md) | [Français](README.fr.md) | Polski | [Čeština](README.cs.md) | [Norsk](README.no.md)

# Sterownik macOS do plotera tnącego VEVOR — CH554_CDC / USB 0483:5750

**Ploter tnący VEVOR nie działa na Macu?** Darmowy projekt open source łączący plotery VEVOR / Anhui Anyu z programem [Inkcut](https://github.com/inkcut/inkcut) przez USB — bez abonamentu SignCut, bez maszyny wirtualnej z Windows.

**Szybki test zgodności** — w Terminalu:

```bash
system_profiler SPUSBDataType | grep -B 1 -A 5 "CH554"
```

Jeśli widzisz `CH554_CDC` z `Vendor ID: 0x0483` i `Product ID: 0x5750`, ten projekt dotyczy Twojego urządzenia (ten sam identyfikator mają m.in. VEVOR, Secabo, GoldCut, JinKa, SAGA, US Cutter).

**Typowe objawy na macOS:** brak portu szeregowego (`/dev/cu.*`); głowica rusza raz i zamiera; litery wycinane jedna na drugiej; działa po włączeniu, po chwili bezczynności przestaje reagować.

Pełna dokumentacja (po angielsku): [README.md](README.md) · [Protokół](docs/PROTOCOL.md) · [Rozwiązywanie problemów](docs/TROUBLESHOOTING.md)

> **Wersja wstępna** — nie ma jeszcze gotowego instalatora. Kliknij „Watch", aby dostać powiadomienie.

⭐ Ploter działa? Zostaw gwiazdkę — pomoże to innym użytkownikom Maca znaleźć ten projekt.

*Słowa kluczowe: ploter tnący VEVOR Mac, ploter VEVOR macOS sterownik, VEVOR nie wykryty Mac, darmowa alternatywa SignCut, Inkcut VEVOR.*
