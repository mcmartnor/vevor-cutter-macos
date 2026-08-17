[English](README.md) | [Deutsch](README.de.md) | [Español](README.es.md) | [Français](README.fr.md) | [Polski](README.pl.md) | [Čeština](README.cs.md) | Norsk

# macOS-driver for VEVOR vinylkutter — CH554_CDC / USB 0483:5750

**Virker ikke VEVOR-vinylkutteren (skjæreplotteren) din på Mac?** Gratis, åpen kildekode som kobler VEVOR-/Anhui Anyu-kuttere til [Inkcut](https://github.com/inkcut/inkcut) via USB — uten SignCut-abonnement, uten Windows-VM.

**Rask kompatibilitetssjekk** — kjør i Terminal:

```bash
system_profiler SPUSBDataType | grep -B 1 -A 5 "CH554"
```

Ser du `CH554_CDC` med `Vendor ID: 0x0483` og `Product ID: 0x5750`, er dette prosjektet for din maskin (samme ID brukes av VEVOR, Secabo, GoldCut, JinKa, SAGA, US Cutter m.fl.).

**Typiske symptomer på macOS:** ingen serieport (`/dev/cu.*`) dukker opp; hodet beveger seg én gang og fryser; bokstaver kuttes oppå hverandre; virker etter oppstart, dør etter tomgang.

Full dokumentasjon (engelsk): [README.md](README.md) · [Protokoll](docs/PROTOCOL.md) · [Feilsøking](docs/TROUBLESHOOTING.md)

> **Tidlig versjon** — ferdig installasjonsveiledning kommer. Trykk «Watch» på repoet for varsel.

*Søkeord: vinylkutter VEVOR Mac, skjæreplotter macOS, VEVOR ikke funnet Mac, gratis SignCut-alternativ, Inkcut VEVOR, folieskjærer Mac.*
