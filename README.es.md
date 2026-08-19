[English](README.md) | [Deutsch](README.de.md) | Español | [Français](README.fr.md) | [Polski](README.pl.md) | [Čeština](README.cs.md) | [Norsk](README.no.md)

# Controlador macOS para cortadora de vinilo VEVOR — CH554_CDC / USB 0483:5750

**¿Tu cortadora (plotter de corte) VEVOR no funciona en Mac?** Proyecto gratuito y de código abierto que conecta las cortadoras VEVOR / Anhui Anyu con [Inkcut](https://github.com/inkcut/inkcut) por USB — sin suscripción a SignCut, sin máquina virtual de Windows.

**Comprobación rápida** — ejecuta en Terminal:

```bash
system_profiler SPUSBDataType | grep -B 1 -A 5 "CH554"
```

Si aparece `CH554_CDC` con `Vendor ID: 0x0483` y `Product ID: 0x5750`, tu máquina es el objetivo de este proyecto (VEVOR, Secabo, GoldCut, JinKa, SAGA, US Cutter y otras marcas comparten este ID).

**Síntomas típicos en macOS:** no aparece ningún puerto serie (`/dev/cu.*`); el carro se mueve una vez y se congela; las letras se cortan superpuestas; funciona tras encender y muere en reposo.

Documentación completa (en inglés): [README.md](README.md) · [Protocolo](docs/PROTOCOL.md) · [Solución de problemas](docs/TROUBLESHOOTING.md)

> **Pre-release** — todavía no hay instalador final. Marca "Watch" en el repositorio para recibir avisos.

⭐ ¿Tu plóter ya funciona? Dale una estrella al repositorio: ayuda a otros usuarios de Mac a encontrarlo.

*Palabras clave: cortadora de vinilo VEVOR Mac, plotter de corte macOS driver, VEVOR no detectada Mac, alternativa SignCut gratis, Inkcut VEVOR.*
