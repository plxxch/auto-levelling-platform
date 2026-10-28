# Known issues in the original prototype

This file records issues found in the archived 2020 prototype code. They are
left in place because the repository preserves the original implementation;
fix them before using the controller on hardware.

1. **`Retract()` relay call** — the line
   `GPIO.output(relay2.GPIO.HIGH)` is invalid Python; it should be
   `GPIO.output(relay2, GPIO.HIGH)`.

2. **`recordlength()` branches** — the three `elif` branches test the same
   condition (`(abs(px2-px1)!=0) or (abs(py2-py1)!=0)`), so the intended
   "loaded up / loaded down / unloaded" distinction is not effective.

3. **`Count_Angle = ~Count_Angle`** — bitwise inversion turns the flag into
   `-1` / `-2` instead of toggling between `0` and `1`; the subsequent
   `== 0` / `== 1` checks break after the first iteration.

4. **`S1`–`S4` used as both flags and GPIO pins** — `GPIO.setup(S1, GPIO.OUT)`
   is called while `S1 = False`, which configures BCM 0 rather than four
   separate sensor/actuator pins. The four flags are otherwise used as
   docking-state booleans.

5. **Serial port handling** — `AngleXY()` opens a new `serial.Serial` object on
   every call and never closes it; the port is hard-coded to `/dev/ttyUSB0`.

6. **No entry-point guard** — the script executes immediately on import; it has
   no `if __name__ == "__main__":` guard.

7. **No cleanup path** — there is no `try/finally` or `GPIO.cleanup()`; if the
   script exits unexpectedly, the relay outputs keep their last state.

8. **Angle resolution** — the inclinometer response is rounded to whole
   degrees, which limits the achievable leveling accuracy.
