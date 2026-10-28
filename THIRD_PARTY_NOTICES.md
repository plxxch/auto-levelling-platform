# Third-party notices

This repository contains only original code by Pengyu Li. The following
runtime dependencies are **not** bundled; install them separately (for example
with `pip3 install -r requirements.txt`). They remain under their own
licenses:

| Dependency | Purpose | License |
|---|---|---|
| `RPi.GPIO` | Raspberry Pi GPIO access | MIT |
| `pyserial` | Serial communication with the inclinometer | BSD 3-Clause |
| `NumPy` | Actuator-length sorting (`argsort`) | BSD 3-Clause |

The Python standard library is used under the PSF license.
