# Implementation notes

This repository preserves the original controller logic and pin map, with the
issues found in the 2020 prototype fixed.

## Fixed in this revision

1. **`Retract()` relay call** — `GPIO.output(relay2.GPIO.HIGH)` was replaced by
   `GPIO.output(relay2, GPIO.HIGH)`.
2. **`recordlength()` branches** — the three identical `elif` branches were
   collapsed into one block that updates `L1`–`L4` from the extend/retract
   flags.
3. **`Count_Angle` toggling** — `Count_Angle = ~Count_Angle` now uses
   `Count_Angle ^= 1`, so the two-sample comparison alternates between 0 and 1.
4. **`S1`–`S4` GPIO setup** — these are docking flags, not pins; the invalid
   `GPIO.setup(S1, GPIO.OUT)` calls were removed. Relay setup now happens once
   in `main()`.
5. **Serial handling** — `AngleXY()` uses the single serial object opened in
   `main()`, clears the input buffer, validates the response length, catches
   serial errors and no longer reopens the port on every call.
6. **Entry point and cleanup** — the controller now runs from `main()` under
   `if __name__ == "__main__"`. A `try/finally` block stops the actuators,
   closes the serial port and calls `GPIO.cleanup()`.
7. **Docking loop** — the duplicated angle-reading `try/except` was replaced by
   a single call that skips the iteration when the inclinometer cannot be read,
   and exits if the serial port closes.

## Remaining limitations

- **Angle resolution** — the inclinometer reading is still rounded to whole
  degrees, because the balance/docking logic compares angles to exact zero.
  Finer accuracy would require replacing those comparisons with a tolerance
  and re-validating the eight tilt cases on hardware.
- **No hardware safety layer** — limit switches, emergency-stop wiring,
  watchdog behaviour and electrical interlocks are external to this script.
- **No actuator position feedback** — `L1`–`L4` are estimates updated from
  extend/retract actions and angle changes, not measured positions.
- **Blocking prompt** — the docking phase uses `input("Start Docking?")`, so it
  must run interactively.
- **Sensor protocol** — the inclinometer command and the fixed response
  offsets in `AngleXY()` are specific to the sensor used in the prototype.
