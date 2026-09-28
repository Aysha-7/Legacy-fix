# What I checked, and what the agent got wrong

## What the agent got wrong

The first thing I caught was the miles conversion. Bob fixed the `wear_percent` bug and the
missing-reading bug quickly and correctly, but when it swept the helper files it described
`MILES_PER_KM = 1.609` as "possibly the wrong direction" rather than just saying outright that
it was wrong. I had to push it: "is 1.609 miles per km or km per mile?" Once I asked directly
it confirmed the constant was inverted — the correct value is 0.621371 — and fixed it. If I had
just accepted the first sweep summary I would have missed a bug that was making every UK partner
report print 2.6× the real fleet distance.

The second thing I noticed was in the analysis step. Bob's first instinct when I asked about
breakdown predictors was to reach for total odometer and age, which are the obvious-sounding
columns. I told it not to assume and to show me the correlation numbers first. When it did, both
columns came back at r ≈ 0.00 — essentially zero relationship with breakdowns. The real signal
was in km_since_service (r = 0.40), how hard the car is driven daily (r = 0.25), and load
factor (r = 0.22). Bob only stopped assuming "older and higher-mileage = riskier" after I made
it show me the data first.

## What I checked before I accepted its work

**Wear math:** I verified by hand before accepting the fix. A car at 14,900 km of a 15,000 km
interval should be at (14900 / 15000) × 100 = 99.33 %. The old code used `//` (integer floor
division), which gives 14900 // 15000 = 0, so 0 %. I checked that the new code uses `/`, not
`//`, and that `wear_percent(14900, 15000)` returns 99.33, not 0. I ran `python verify.py` and
read the line that says "a car at 14,900 of 15,000 km reports 99.3%" to confirm it myself.

**80% threshold untouched:** I opened `km_wachter.py` after the fix and checked that
`SERVICE_INTERVAL_KM = 15000` and `WARN_AT_PERCENT = 80` were still exactly those values. I
also checked `settings.cfg` directly — `service_interval_km = 15000` and `warn_at_percent = 80`
are still there unchanged. `verify.py` has a dedicated check for both and both show PASS.

**Missing-reading fix:** I read the new `needs_service` code and confirmed it uses
`if "last_service_km" not in car: return False` rather than defaulting to 0. I then ran the
test manually: `needs_service({"id": "VOS-7788", "odometer": 92000})` returns False. Before the
fix it returned True because 92000 − 0 = 92000 km of fake wear.

**Report crash fix:** I looked at `car_wear` in `fleet_report.py` and confirmed the bare
`car["last_service_km"]` was replaced with a guard that returns 0.0 for cars with no reading.
The new test `test_summary_does_not_crash_on_missing_reading` passes, and `verify.py` confirms
"the nightly report ran without crashing".

**Full run:** I ran `python -m pytest -v` and saw all 4 tests green, then ran `python verify.py`
and read every PASS line myself before deciding the code was done.

## What the data actually said

The obvious assumption going in was that high-mileage, older cars break down more. The data does
not say that. `odometer_km` has a correlation of r = 0.002 with `broke_down` — effectively zero.
`age_years` is r = −0.001 — also zero. The mean odometer for cars that broke down (53,448 km)
is almost identical to the mean for cars that did not (53,302 km). Same story for age: both
groups average 5.9 years.

What actually separates the two groups:

- **km_since_service** (r = 0.40): cars that broke down had driven an average of 11,678 km since
  their last service; cars that survived averaged 7,261 km. The median gap is even starker:
  13,064 km vs 6,308 km. This is the single strongest predictor.
- **avg_daily_km** (r = 0.25): cars that broke down are driven about 28 km/day harder on average
  (160 vs 131 km/day). Hard daily use matters independently of how long since the last service.
- **load_factor** (r = 0.22): cars that broke down carry heavier loads on average (0.60 vs 0.51).
  Weaker signal than the other two, but consistent.

The risk score built from these three columns (min-max normalised, averaged, scaled 0-100) gives
broken cars an average score of 59.2 and surviving cars 40.8 — a meaningful separation without
any machine learning. The most actionable finding is cars like VOS-1217 and VOS-1448: both score
above 68 and are flagged as high-risk, but neither would be caught by the 80% KM rule today
because one has only driven 1,700 km since its last service. The score finds them; the rule
never would.
