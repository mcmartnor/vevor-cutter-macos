[English](README.md) | [Deutsch](README.de.md) | [Español](README.es.md) | [Français](README.fr.md) | [Polski](README.pl.md) | Čeština | [Norsk](README.no.md)

# Ovladač macOS pro řezací plotr VEVOR — CH554_CDC / USB 0483:5750

**Řezací plotr VEVOR na Macu nefunguje?** Bezplatný open source projekt propojující plotry VEVOR / Anhui Anyu s programem [Inkcut](https://github.com/inkcut/inkcut) přes USB — bez předplatného SignCut, bez virtuálního Windows.

**Rychlá kontrola kompatibility** — v Terminálu:

```bash
system_profiler SPUSBDataType | grep -B 1 -A 5 "CH554"
```

Pokud vidíte `CH554_CDC` s `Vendor ID: 0x0483` a `Product ID: 0x5750`, je tento projekt určen pro vaše zařízení (stejné ID sdílejí VEVOR, Secabo, GoldCut, JinKa, SAGA, US Cutter a další).

**Typické příznaky na macOS:** nikdy se neobjeví sériový port (`/dev/cu.*`); vozík se jednou pohne a zamrzne; písmena se řežou přes sebe; po zapnutí funguje, v nečinnosti přestane reagovat.

Kompletní dokumentace (anglicky): [README.md](README.md) · [Protokol](docs/PROTOCOL.md) · [Řešení potíží](docs/TROUBLESHOOTING.md)

> **Předběžná verze** — instalátor zatím není hotový. Sledujte repozitář („Watch") pro upozornění.

*Klíčová slova: řezací plotr VEVOR Mac, plotr VEVOR macOS ovladač, VEVOR nedetekován Mac, zdarma alternativa SignCut, Inkcut VEVOR.*
