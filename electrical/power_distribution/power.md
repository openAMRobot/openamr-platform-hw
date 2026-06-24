# Power & electrical safety

*Last updated: 2026-06-20.*

## 🔋 État de charge batterie — SEUILS (24 V plomb) — LIRE AVANT TOUT TEST NAV
Système 24 V = 2× plomb 12 V en série. Tension **au repos** (sans charge) :

| Tension repos | État | Pour la navigation |
|---|---|---|
| **~25,5–26 V** | pleine charge | ✅ OK pour tester |
| **~24,5 V** | ~70 % | ✅ acceptable |
| **~24 V** | ~50 % | ⚠️ limite |
| **≤ 23,5 V** | déchargé (~30 %) | ❌ **NE PAS tester la nav** |

⚠️ C'est la tension **au repos** : **sous charge (moteurs), elle chute encore** (souvent −1 à −2 V en pointe,
cf le pack qui sague). En dessous de ~22 V sous charge → drivers en sous-tension → **couple mou + roue
gauche (faux-contact) décroche → le robot ne suit pas le plan → percute des obstacles pourtant évités par
la nav.** **RÈGLE : viser ≥ 25 V au repos avant tout test de navigation/évitement.** Sinon on debugge Nav2
pour rien (déjà arrivé : le vrai problème était le 24 V, pas la nav).

**Relevé 2026-06-20 (fin de session)** : batterie à **23,4 V au repos → trop bas**. Tout test d'évitement
de cette session est non concluant tant que la batterie n'est pas rechargée (~25,5 V). À reprendre après
charge.

## Power architecture — VERIFIED 2026-06-19
```
Battery 24V ──┐
              ├──(parallel)──► V+ / V−  of BOTH drivers   (marron = V+, bleu = V−)
Mains 24V  ───┘
              └──(parallel)──► DC-DC 24V→5V ──► Raspberry Pi ──USB──► Teensy ──► IMU + encoders (5V)
```
| Element | Supply |
|---|---|
| Motors / drivers | **24 V DC** on `V+ / V−` of each driver. Wire colors: **marron = V+, bleu = V−** (confirmed) |
| 24 V source | **battery pack** (lead-acid) **or** an **AC/DC converter** (230 V mains) — wired **in parallel** to the same 24 V bus |
| Raspberry Pi | **DC-DC 24 V→5 V** buck from the 24 V bus |
| Teensy | powered over **USB** from the Pi (5 V) |
| **IMU + encoders** | **5 V from the Teensy** (VUSB pin) → see ⚠️ encoder overvoltage in [encoders.md](../sensors/encoders.md) |
| LiDAR | powered over its USB (CP2102 adapter) from the Pi |

## 🔴 Safety gaps found (2026-06-19) — to fix
1. **No fuse on the battery.** A lead-acid pack can deliver **hundreds of amps** into a short → fire /
   burns / melted wires if a 24 V conductor touches ground. **Add a fuse (or breaker) on the battery `+`**,
   as close to the terminal as possible. Size it to the motor stall current (TBD — note the value once chosen).
2. **No battery-side disconnect** (only the mains has a switch). No fast hardware cut-off for the 24 V
   battery. **Add a switch/disconnect — ideally an E-stop mushroom** — on the battery `+`.
3. **Battery AND mains in parallel** on the same bus: if both are ever connected **at once**, the stiffer
   source back-feeds the other (risk to the AC/DC, or uncontrolled battery charge). **Only one source at a
   time** — a source selector switch would make this safe.

## Battery pack
- **4 × 12 V lead-acid** batteries (the big black ones).
- Wired **2 in series → 24 V** (one "pair"). With 2 pairs you can make **24 V** (pairs in parallel, more
  capacity) **or 48 V** (pairs in series) — this matches the OpenAMR platform's "24/48 V" spec.
- **In practice we usually run a single pair = 24 V.**
- ⚠️ Lead-acid basics: respect polarity, don't short the terminals (very high current), charge with a
  suitable lead-acid charger, and don't fully deep-discharge them (shortens life).

The Teensy sends only **low-current logic signals** to the drivers; the **24 V power** goes through the
drivers to the motor phases. Logic ground (Teensy GND) and driver `COM` must be **common**.

## ⚠️ Electrical safety — 230 V AC (read this)
The 24 V side is low-risk, but the **AC/DC converter is fed by 230 V AC, which is potentially lethal.**

- Touching exposed 230 V can cause cardiac fibrillation, "can't-let-go" muscle tetany, burns. ~30 mA
  through the body is already dangerous.
- If the converter's mains terminals are exposed/unprotected, **treat it as dangerous** and let nobody
  touch it while powered.

**Minimum protections (in priority order):**
1. **30 mA RCD / residual-current device** upstream — the single most important life-saver (cuts power in
   milliseconds on a ground/body leak).
2. **Enclose all 230 V wiring** in a closed box — no bare mains conductor reachable by a finger.
3. **Earth** the converter's metal chassis (protective conductor).
4. **Fuse / breaker** on the mains input (short-circuit / overload).
5. **Strain relief** on the mains cable; prefer an IEC inlet over flying leads.
6. **Golden rule**: cut/unplug the mains **before** touching anything on the power side. Never work live.

## Battery vs mains — measured 2026-06-18 (battery sags under load)
Same motor step (0.25 m/s ≈ 24 rpm), comparing the PWM the PID needs to reach that speed:

| Supply | PWM needed for ~23 rpm |
|---|---|
| AC/DC mains (24 V stiff) | ~180–220 |
| Battery pack | **~290–349** (~60 % more) |

The battery read **24.4 V at rest** but needs **~60 % more PWM** under load → it **sags under load**
(weak/discharged pack or high internal/contact resistance). Not blocking now (PID compensates, PWM ≈ 34 %
of the 1023 max), but at higher speeds it will **plateau**, and a sagging 24 V rail is what made the
**left wheel drop out** when its cable also had a loose contact (see history/diagnostics.md (see `openamr-platform-sw`: docs/troubleshooting/diagnostics.md)).

**Practical rule:** keep the pack **charged**; if motors feel weak / one wheel drops, **check battery
voltage under load** (multimeter on the terminals while commanding) and the 24 V connectors before
suspecting the firmware/PID. Bench-test on mains for repeatable results.

## Stopping the robot quickly (test safety)
- Software: stop publishing `/cmd_vel` → firmware zeroes motors after 200 ms (watchdog). `Ctrl-C` on the
  publisher works too.
- Hardware backstop: keep a hand on the **24 V cut-off** during powered tests. Wheels off the ground.

## TODO / to document
- Exact battery capacity (Ah) & charger, AC/DC converter model, fuse rating, and whether a physical
  **E-stop** exists (a ROS-independent emergency stop is recommended).
- A **battery voltage monitor** would be useful (lead-acid sags under load; low voltage → erratic motors).
