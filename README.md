# Automatic Leveling System for a Mobile Scissor-Lift Platform

Python control software for a mobile scissor-lift platform that levels itself
automatically using a Raspberry Pi, a serial inclinometer, and four linear
actuators. After balancing, the controller runs a docking sequence that seats
all four actuator legs.

This repository is the control-software part of a project that included:

- defining the control architecture around a Raspberry Pi, inclinometer and
  linear actuators;
- developing the autonomous balancing and docking software;
- evaluating and upgrading the leveling sensor for improved accuracy;
- actuator load characterization;
- prototype refinement and experimental validation with undergraduate
  students.

## System architecture

```
            serial (9600 8N1)
inclinometer ───────────────► Raspberry Pi ───► 8-channel relay board
                               (Python)              │
                                                     ├─► linear actuator 1
                                                     ├─► linear actuator 2
                                                     ├─► linear actuator 3
                                                     └─► linear actuator 4
```

- The **inclinometer** is connected to `/dev/ttyUSB0` at **9600 baud**. The
  controller sends `77 04 00 04 08` and parses the X/Y tilt angles from the
  response.
- Each **linear actuator** has a separate extend and retract relay, so four
  actuators use all eight relay channels.
- The controller reads the tilt, chooses the leg(s) to extend based on the
  sign of the X/Y angles, and repeats until the platform is level.
- When level, it runs `Docking()`, using the recorded actuator stroke
  estimates (`recordlength`, `Sort_Length`, `Legselection`) to bring each leg
  down in sequence.

## Relay / GPIO pin map (BCM numbering)

| Leg | Extend relay | Retract relay |
|---|---|---|
| Front left | GPIO17 | GPIO27 |
| Front right | GPIO18 | GPIO5 |
| Back right | GPIO6 | GPIO13 |
| Back left | GPIO19 | GPIO26 |

The relay board is wired **active-low** in the code: `GPIO.LOW` energises the
relay. All relays are initialised to `GPIO.HIGH` (off) at start-up.

## Files

```
auto_levelling_platform.py   # controller
requirements.txt              # RPi.GPIO, pyserial, numpy
KNOWN_ISSUES.md               # notes on the original prototype
```

## Requirements

- Raspberry Pi with GPIO access
- Python 3
- Serial inclinometer supported by the command/response format above
- 8-channel relay board and four linear actuators

Install the Python dependencies:

```bash
pip3 install -r requirements.txt
```

## Running

```bash
python3 auto_levelling_platform.py
```

The script opens `/dev/ttyUSB0` directly. If your inclinometer uses a different
port, change it in the serial setup and in `AngleXY()`.

When the platform first reaches a level position, the controller retracts the
legs for the docking phase and then asks:

```
Start Docking?
```

Press Enter to continue.

## Prototype status

This is the original research-prototype code, archived for reference. It is
**not** a production controller: hardware limit switches, emergency-stop
handling, watchdog behaviour and electrical safety interlocks are outside this
script. Review [KNOWN_ISSUES.md](KNOWN_ISSUES.md) before running it on
hardware.

## License

MIT License, Copyright (c) 2020 Pengyu Li. See [LICENSE](LICENSE).
Runtime dependencies (RPi.GPIO, pyserial, NumPy) are not included and remain
under their own licenses.
