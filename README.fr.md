[English](README.md) | [Deutsch](README.de.md) | [Español](README.es.md) | Français | [Polski](README.pl.md) | [Čeština](README.cs.md) | [Norsk](README.no.md)

# Pilote macOS pour traceur de découpe VEVOR — CH554_CDC / USB 0483:5750

**Votre traceur de découpe (plotter vinyle) VEVOR n'est pas détecté sur Mac ?** Projet gratuit et open source qui connecte les découpeuses VEVOR / Anhui Anyu à [Inkcut](https://github.com/inkcut/inkcut) en USB — sans abonnement SignCut, sans machine virtuelle Windows.

**Vérification rapide** — dans le Terminal :

```bash
system_profiler SPUSBDataType | grep -B 1 -A 5 "CH554"
```

Si `CH554_CDC` apparaît avec `Vendor ID: 0x0483` et `Product ID: 0x5750`, votre machine est concernée (VEVOR, Secabo, GoldCut, JinKa, SAGA, US Cutter et d'autres marques partagent cet identifiant).

**Symptômes typiques sous macOS :** aucun port série (`/dev/cu.*`) n'apparaît ; le chariot bouge une fois puis se fige ; les lettres se découpent les unes sur les autres ; fonctionne après allumage puis meurt au repos.

Documentation complète (en anglais) : [README.md](README.md) · [Protocole](docs/PROTOCOL.md) · [Dépannage](docs/TROUBLESHOOTING.md)

> **Pré-version** — pas encore d'installateur finalisé. Cliquez sur « Watch » pour être averti.

⭐ Votre découpeur fonctionne ? Une étoile sur GitHub aide d'autres utilisateurs Mac à trouver ce projet.

*Mots-clés : traceur de découpe VEVOR Mac, plotter de découpe vinyle macOS, VEVOR non détecté Mac, alternative SignCut gratuite, Inkcut VEVOR.*
