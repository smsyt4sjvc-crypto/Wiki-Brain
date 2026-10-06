# Jenn's Weekly Workout — phone page

**Open on the phone:** https://claude.ai/artifact/6pf9LvHW1wMnMP96pexMer
(private Artifact — share it from the page's Share menu before Jenn can open it)

- `index.html` — the page (tabs per day; tap-to-check per exercise; a note field per exercise for pin # / band; both remembered on that phone only).
- `plan.md` — Jenn's routine, verbatim, as pasted 2026-10-05.
- `build.py` — generates `index.html` from the plan data (edit the plan there, run it, republish to the SAME URL).
- `img/` — the 58 photos the page uses. `m-*.jpg` = machine photos cropped from the Body-Solid G9 owner's manual workout pages (the shipped exercise chart is not online); `f-*.jpg` = Free Exercise DB demo pairs (github.com/yuhonas/free-exercise-db).

Image rules followed from the plan's app note: machine moves → manual photo; band/bodyweight → closest Free Exercise DB match (caption says "closest match" when the demo uses different equipment); no close match → no photo (Band Lateral Walk, Leg swings, Band Hip Abduction, Back Hyperextension, seated butterfly, lat stretch).

To republish after a change: `python3 personal/jenn-workout/build.py`, then publish `personal/jenn-workout/index.html` with `url` = the link above (files in `img/` are already uploaded; pass only changed ones).
