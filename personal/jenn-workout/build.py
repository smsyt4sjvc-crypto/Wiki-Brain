import html, json, os, re
OUT='/home/user/Wiki-Brain/personal/jenn-workout/index.html'
IMG='/home/user/Wiki-Brain/personal/jenn-workout/img'

def fe(name, label=None):   # Free Exercise DB pair
    return {'kind':'fe','files':[f'img/f-{name}-0.jpg',f'img/f-{name}-1.jpg'],'label':label or name.replace('_',' ').replace('-',' ')}
def mc(key, label):          # Body-Solid manual photo
    return {'kind':'g9s','files':[f'img/m-{key}.jpg'],'label':label}

# ---------- the plan, verbatim from Jenn's text ----------
WARMUP=[('Bike, easy (RPE 3-4)','5 min',None,fe('Bicycling_Stationary','Bicycling, Stationary')),
        ('Glute bridges, bodyweight','15',None,fe('Butt_Lift_Bridge','Butt Lift (Bridge)')),
        ('Band lateral walk, light band','10 steps each way',None,None),
        ('Leg swings, front to back','10/leg',None,None)]
COOL=[('Glutes: lying figure-4','ankle over opposite knee, pull legs in',fe('Lying_Glute','Lying Glute')),
      ('Hamstrings','heel on a low surface, leg straight, hinge forward',fe('Standing_Hamstring_and_Calf_Stretch','Standing Hamstring and Calf Stretch')),
      ('Quads','standing, pull heel toward glute',fe('Standing_Elevated_Quad_Stretch','Standing Elevated Quad Stretch')),
      ('Hip flexors','half-kneeling lunge',fe('Kneeling_Hip_Flexor','Kneeling Hip Flexor')),
      ('Inner thighs','seated butterfly, knees toward floor',None),
      ('Lats/upper back','hold frame with both hands, sit hips back',None)]

# exercise rows: (tag, name, sets, cue, image)
DAYS=[
 dict(key='mon',short='Mon',title='Glutes & hamstrings + lats + bike sprints',focus='Glutes & hamstrings + lats + core + bike sprints 10 min',kind='lift',
  blocks=[('Warm-up','7 min','warmup'),
   ('Supersets','1 set of A1, then 1 set of A2, rest 60-90 sec, repeat',[
    ('A1','Leg Press (machine)','3 x 10-12','Feet high and wide on press plate for more glutes; back pad set so knees are at 90 deg; don\'t lock out knees',mc('leg-press','Leg Press')),
    ('A2','Band Pallof Press','3 x 10/side','Anchored at chest height; press straight out, resist the twist',fe('Pallof_Press','Pallof Press')),
    ('B1','Lat Pull Down (machine)','3 x 10-12','Lat Bar on high pulley; pull to upper chest, never toward head or neck',mc('lat-pulldown','Lat Pulldown')),
    ('B2','Band Romanian Deadlift','3 x 12-15','Stand on band hip-width, handles in hands; hinge at hips, soft knees, flat back, squeeze glutes to stand',fe('Romanian_Deadlift','Romanian Deadlift')),
    ('C1','Glute Kickback (machine)','3 x 12-15/leg','Ankle Strap/cuff on low pulley; face machine, hold on, kick straight leg back. Band version: Band Standing Kickback (anchored low, hooked to ankle)',mc('glute-kickback','Glute Kickback')),
    ('C2','Band Glute Bridge','3 x 15','Lying on back, band across hips, handles pressed to floor; 2-sec squeeze at top',fe('Butt_Lift_Bridge','Butt Lift (Bridge)')),
    ('D1','Standing Leg Curl (machine)','2 x 12-15/leg','Heel under bottom leg pad, knee slightly below top roller pad',mc('standing-leg-curl','Standing Leg Curl')),
    ('D2','Band Lateral Walk','2 x 12 steps each way','Band clipped between both ankles (or stand on band, hold handles); stay in a half squat',None)]),
   ('Cardio','Bike sprints 10 min',[('','Bike sprints','10 min','2 min easy, 6 rounds of 20 sec hard (RPE 9) / 40 sec easy, 2 min easy',fe('Bicycling_Stationary','Bicycling, Stationary'))]),
   ('Cool-down stretch','5 min','cool')]),
 dict(key='tue',short='Tue',title='Zone 2 incline walk + band core & back',focus='Treadmill incline walk Zone 2 30 min + band core & back',kind='cardio',
  blocks=[('Treadmill','',[
    ('1','Treadmill warm-up','5 min','easy (RPE 3-4)',fe('Walking_Treadmill','Walking, Treadmill')),
    ('2','Treadmill incline walk Zone 2','30 min','at RPE 5-6',None)]),
   ('Circuit','3 rounds, 60 sec rest between rounds (~15 min)',[
    ('','Resistance Ab Crunch (machine)','12-15','Tricep/Ab Strap on mid pulley; Pec Dec Arms moved out of the way',mc('ab-crunch','Resistance Ab Crunch')),
    ('','Band Standing Row','15','Anchored at chest height; pull handles to ribs, squeeze shoulder blades together',fe('Seated_Cable_Rows','Seated Cable Rows (closest match; do it standing)')),
    ('','Band Face Pull','15','Light band anchored at face height; pull toward forehead, elbows high',fe('Face_Pull','Face Pull')),
    ('','Plank','30-45 sec','Forearms down, body in a straight line',fe('Plank','Plank'))]),
   ('Cool-down stretch','5 min','cool')]),
 dict(key='wed',short='Wed',title='Thighs + mid & lower back + incline walk',focus='Thighs (front, inner, outer) + mid & lower back + treadmill incline walk 10 min',kind='lift',
  blocks=[('Warm-up','7 min','warmup'),
   ('Supersets','1 set of A1, then 1 set of A2, rest 60-90 sec, repeat',[
    ('A1','Leg Extension (machine)','3 x 12-15','Press Arm in Storage position, back pad flat; knees over top roller pads, feet under bottom leg pads',mc('leg-extension','Leg Extension')),
    ('A2','Band Sumo Squat','3 x 15','Stand on band in a wide stance, toes out, handles at shoulders (inner thighs + glutes)',fe('Plie_Dumbbell_Squat','Plie Dumbbell Squat (closest match)')),
    ('B1','Chest Supported Mid Row (machine)','3 x 10-12','Chest flat on pad; pull handles until even with midsection',mc('mid-row','Chest Supported Mid Row')),
    ('B2','Reverse Lunge','3 x 12/leg','Bodyweight; step back, back knee drops toward floor',fe('Dumbbell_Rear_Lunge','Dumbbell Rear Lunge (closest match; no weights)')),
    ('C1','Leg Abduction (machine)','3 x 12-15/leg','Ankle Strap/cuff on low pulley; stand 1-2 ft away, working leg is the one farther from the machine; hold back pad. Band version: Band Hip Abduction (anchored low, hooked to outside ankle, sweep leg out)',mc('leg-abduction','Leg Abduction')),
    ('C2','Band Hip Adduction','3 x 12-15/leg','Anchored low, hooked to the ankle nearest the machine; sweep that leg across in front of the other (inner thigh)',fe('Band_Hip_Adductions','Band Hip Adductions')),
    ('D1','Back Hyperextension (machine)','2 x 12-15','Press Arm in Mid Row position, seat at highest position, facing in; hold mid row handles, arms and back straight, lean back from the hips to 45 deg',None),
    ('D2','Dead Bug','2 x 8/side','Lower back pressed to floor',fe('Dead_Bug','Dead Bug'))]),
   ('Cardio','Treadmill incline walk 10 min',[('','Treadmill incline walk','10 min','steady at RPE 6, roughly 8-12% incline',fe('Walking_Treadmill','Walking, Treadmill'))]),
   ('Cool-down stretch','5 min','cool')]),
 dict(key='thu',short='Thu',title='Bike intervals + core',focus='Bike 4x4 intervals 28 min + core',kind='cardio',
  blocks=[('Bike','',[
    ('1','Bike warm-up','8 min','building from easy to moderate',fe('Bicycling_Stationary','Bicycling, Stationary')),
    ('2','4x4 intervals','28 min','4 min hard (RPE 8) / 3 min easy (RPE 3), x4. Weeks 1-2: 3 rounds.',None)]),
   ('Core circuit','3 rounds, 60 sec rest between rounds (~13 min)',[
    ('','Oblique Crunch (machine)','10/side','Tricep/Ab Strap on mid pulley, Press Arm in Storage position; alternate left and right',mc('ab-crunch','Resistance Ab Crunch station (same setup, twist to each side)')),
    ('','Band Woodchopper','10/side','Anchored high; pull handle diagonally down across your body to the opposite hip, rotate through the torso',fe('Standing_Cable_Wood_Chop','Standing Cable Wood Chop')),
    ('','Reverse Crunch','12-15','Lying on back, curl knees toward chest, lift hips slightly',fe('Reverse_Crunch','Reverse Crunch')),
    ('','Mountain Climbers','30 sec','Hands on floor, drive knees toward chest',fe('Mountain_Climbers','Mountain Climbers'))]),
   ('Cool-down stretch','5 min','cool')]),
 dict(key='fri',short='Fri',title='Glutes & legs + lats + bike tempo',focus='Glutes & legs + lats + core + bike tempo 10 min',kind='lift',
  blocks=[('Warm-up','7 min','warmup'),
   ('Supersets','1 set of A1, then 1 set of A2, rest 60-90 sec, repeat',[
    ('A1','Leg Press (machine)','3 x 10-12','Normal foot position; back pad set so knees are at 90 deg; don\'t lock out knees',mc('leg-press','Leg Press')),
    ('A2','Band Pull-Through','3 x 15','Anchored low, face away, handles between legs; hinge back, drive hips forward, squeeze glutes',fe('Band_Good_Morning_Pull_Through','Band Good Morning (Pull Through)')),
    ('B1','Lat Pull Down (machine)','3 x 12-15','Same setup as Monday',mc('lat-pulldown','Lat Pulldown')),
    ('B2','Band Split Squat','3 x 10/leg','Front foot on band, handles at shoulders; back knee drops toward floor',fe('Split_Squats','Split Squats')),
    ('C1','Glute Kickback (machine)','3 x 15/leg','Same setup as Monday. Band version: Band Standing Kickback',mc('glute-kickback','Glute Kickback')),
    ('C2','Band Single-Leg RDL','3 x 10/leg','Stand on band with working foot, handle in opposite hand; free hand on frame for balance; hinge on one leg',fe('Kettlebell_One-Legged_Deadlift','Kettlebell One-Legged Deadlift (closest match)')),
    ('D1','Resistance Ab Crunch (machine)','2 x 15','Tricep/Ab Strap on mid pulley; Pec Dec Arms moved out of the way',mc('ab-crunch','Resistance Ab Crunch')),
    ('D2','Single-Leg Glute Bridge','2 x 12/leg','Bodyweight; 2-sec squeeze at top',fe('Single_Leg_Glute_Bridge','Single Leg Glute Bridge'))]),
   ('Cardio','Bike tempo 10 min',[('','Bike tempo','10 min','steady at RPE 6-7',fe('Bicycling_Stationary','Bicycling, Stationary'))]),
   ('Cool-down stretch','5 min','cool')]),
 dict(key='sat',short='Sat',title='Long Zone 2 + band glute & thigh circuit',focus='Bike + treadmill Zone 2 40 min + band glute & thigh circuit',kind='cardio',
  blocks=[('Zone 2','40 min',[
    ('1','Bike Zone 2','20 min','at RPE 5-6 (first 3 min easy)',fe('Bicycling_Stationary','Bicycling, Stationary')),
    ('2','Treadmill incline walk Zone 2','20 min','at RPE 5-6',fe('Walking_Treadmill','Walking, Treadmill'))]),
   ('Band circuit','3 rounds, 45 sec rest between rounds (~15 min)',[
    ('','Band Squat','15','Stand on band, handles at shoulders',fe('Bodyweight_Squat','Bodyweight Squat (closest match)')),
    ('','Band Standing Kickback','12/leg','Anchored low, hooked to ankle; face machine, hold on, kick straight leg back',fe('One-Legged_Cable_Kickback','One-Legged Cable Kickback (closest match)')),
    ('','Band Hip Adduction','12/leg','Anchored low, hooked to the ankle nearest the machine; sweep leg across',fe('Band_Hip_Adductions','Band Hip Adductions')),
    ('','Band Lateral Walk','12 steps each way','Band between ankles; stay in a half squat',None)]),
   ('Cool-down stretch','5 min','cool')]),
 dict(key='sun',short='Sun',title='Rest or active recovery',focus='Rest or easy recovery',kind='rest',
  blocks=[('Rest day','',[('','Full rest, or easy bike or walk','20-30 min','RPE 3-4, then 10-15 min full-body stretching with 20-30 sec holds',None)])]),
]

MISSING_NOTE={'Band lateral walk, light band':'No close match in Free Exercise DB',
 'Band Lateral Walk':'No close match in Free Exercise DB','Leg swings, front to back':'No close match in Free Exercise DB',
 'Back Hyperextension (machine)':'Not on the Body-Solid workout pages. Uses the Mid Row station, seat up, facing in.',
 'Treadmill incline walk Zone 2':'','4x4 intervals':'','Inner thighs':'No close match in Free Exercise DB (its “Butterfly” is a chest machine)',
 'Lats/upper back':'No close match in Free Exercise DB','Full rest, or easy bike or walk':''}

def esc(s): return html.escape(s, quote=True)
def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')

def figure(img, name):
    if not img:
        note=MISSING_NOTE.get(name,'')
        if not note: return ''
        return f'<div class="noimg">{esc(note)}</div>'
    src='Body-Solid manual, workout pages' if img['kind']=='g9s' else 'Free Exercise DB'
    pics=''.join(f'<img src="{f}" alt="{esc(img["label"])}{" step "+str(i+1) if len(img["files"])>1 else ""}" loading="lazy" width="420" height="420">' for i,f in enumerate(img['files']))
    return f'<figure class="pics n{len(img["files"])}">{pics}<figcaption>{esc(img["label"])} · {src}</figcaption></figure>'

def ex_card(day, tag, name, sets, cue, img, idx):
    eid=f'{day}-{slug(name)}-{idx}'
    tagh=f'<span class="tag">{esc(tag)}</span>' if tag else ''
    machine='(machine)' in name
    noteph='pin #' if machine else 'band / note'
    return f'''<article class="ex" id="{eid}">
 <label class="done"><input type="checkbox" id="chk-{eid}" data-key="{eid}"><span class="box" aria-hidden="true"></span><span class="sr">Done</span></label>
 <div class="exhead">{tagh}<h4>{esc(name)}</h4><span class="sets">{esc(sets)}</span></div>
 <p class="cue">{esc(cue)}</p>
 {figure(img,name)}
 <div class="note"><input type="text" id="note-{eid}" data-key="note-{eid}" placeholder="{noteph}" inputmode="text" maxlength="40" aria-label="Note for {esc(name)}"></div>
</article>'''

def simple_list(rows, day, prefix):
    out=[]
    for i,r in enumerate(rows):
        if prefix=='warm':
            name,amt,_,img=r; cue=''
        else:
            name,cue,img=r; amt='20-30 sec'
        out.append(ex_card(day,'',name,amt,cue,img,f'{prefix}{i}'))
    return '\n'.join(out)

def day_section(d):
    parts=[]
    for b in d['blocks']:
        title,sub,content=b
        if content=='warmup':
            body=simple_list(WARMUP,d['key'],'warm'); sub='7 min'
        elif content=='cool':
            body=simple_list(COOL,d['key'],'cool'); sub='5 min, hold each 20-30 sec, no bouncing'
        else:
            body='\n'.join(ex_card(d['key'],tag,name,sets,cue,img,i) for i,(tag,name,sets,cue,img) in enumerate(content))
        parts.append(f'<section class="block"><div class="bhead"><h3>{esc(title)}</h3>{("<p>"+esc(sub)+"</p>") if sub else ""}</div>{body}</section>')
    hidden='' if d['key']=='mon' else ' hidden'
    return f'''<div class="day" id="{d['key']}" data-kind="{d['kind']}"{hidden}>
 <header class="dayhead"><p class="eyebrow">{esc(d['short'])} · ~60 min</p><h2>{esc(d['title'])}</h2><p class="focus">{esc(d['focus'])}</p></header>
 {''.join(parts)}
 <p class="resetrow"><button type="button" class="reset" data-day="{d['key']}">Clear today's checks</button></p>
</div>'''

tabs=''.join(f'<button type="button" role="tab" class="tab" data-day="{d["key"]}" aria-selected="{"true" if d["key"]=="mon" else "false"}"><span>{d["short"]}</span><small>{esc({"lift":"Lift","cardio":"Cardio","rest":"Rest"}[d["kind"]])}</small></button>' for d in DAYS)
days=''.join(day_section(d) for d in DAYS)

page=f'''<title>Jenn's Weekly Workout</title>
<meta name="description" content="Weekly glutes, legs, back, core and cardio routine on the Body-Solid G9S home gym, with demo photos for every exercise.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&display=swap">
<style>
/* Layout: one sticky day bar; each day is one scroll of exercise cards with photo pairs. Gym-poster type, calm surfaces. */
:root{{
 --bg:#f6f4f1; --surface:#ffffff; --fg:#1d1a24; --muted:#625c6e; --line:#dcd7d0;
 --accent:#b5214f; --accent-ink:#ffffff; --tag:#eee6ea; --ok:#2a7a4b;
 --display:"Barlow Condensed","Arial Narrow",Impact,sans-serif; --body:"Source Sans 3","Segoe UI",Helvetica,Arial,sans-serif;
}}
@media (prefers-color-scheme: dark){{ :root:not([data-theme="light"]){{ --bg:#15131a; --surface:#1f1c26; --fg:#f1edf2; --muted:#a79fb3; --line:#36313f; --accent:#ec5a86; --accent-ink:#1a0710; --tag:#2b2433; --ok:#6fcf97; color-scheme:dark }} }}
:root[data-theme="dark"]{{ --bg:#15131a; --surface:#1f1c26; --fg:#f1edf2; --muted:#a79fb3; --line:#36313f; --accent:#ec5a86; --accent-ink:#1a0710; --tag:#2b2433; --ok:#6fcf97; color-scheme:dark }}
*{{box-sizing:border-box}}
body{{background:var(--bg);color:var(--fg);font-family:var(--body);font-size:16px;line-height:1.45;margin:0}}
.wrap{{max-width:720px;margin:0 auto;padding-inline:16px;padding-block:0 48px}}
h1,h2,h3,h4{{font-family:var(--display);line-height:1.05;margin:0;text-wrap:balance}}
h1{{font-size:2.6rem;font-weight:700;letter-spacing:.01em}}
.top{{padding-block:20px 10px}}
.top p{{margin:6px 0 0;color:var(--muted);max-width:60ch}}
.eyebrow{{font-family:var(--body);font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);font-weight:600;margin:0}}
.tabs{{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);display:grid;grid-template-columns:repeat(7,1fr);gap:4px;padding-block:8px;border-bottom:1px solid var(--line)}}
.tab{{appearance:none;border:1px solid var(--line);background:var(--surface);color:var(--fg);border-radius:8px;padding:6px 0;font:inherit;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:1px;min-width:0}}
.tab span{{font-family:var(--display);font-weight:700;font-size:1.05rem}}
.tab small{{font-size:.62rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}}
.tab[aria-selected="true"]{{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}}
.tab[aria-selected="true"] small{{color:var(--accent-ink)}}
.tab:focus-visible,.reset:focus-visible,.done input:focus-visible+.box,details summary:focus-visible{{outline:3px solid var(--accent);outline-offset:2px}}
.dayhead{{padding-block:18px 6px}}
.dayhead h2{{font-size:2rem;margin-top:4px}}
.focus{{color:var(--muted);margin:4px 0 0}}
.block{{margin-top:18px}}
.bhead{{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 12px;border-top:2px solid var(--fg);padding-top:8px;margin-bottom:8px}}
.bhead h3{{font-size:1.35rem;text-transform:uppercase;letter-spacing:.03em}}
.bhead p{{margin:0;color:var(--muted);font-size:.9rem}}
.ex{{position:relative;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 12px 10px 48px;margin-bottom:10px}}
.ex.is-done{{opacity:.55}}
.done{{position:absolute;left:12px;top:14px;width:26px;height:26px;cursor:pointer}}
.done input{{position:absolute;opacity:0;width:1px;height:1px}}
.box{{display:block;width:24px;height:24px;border:2px solid var(--muted);border-radius:6px;background:var(--surface)}}
.done input:checked+.box{{background:var(--ok);border-color:var(--ok)}}
.done input:checked+.box::after{{content:"";position:absolute;left:8px;top:3px;width:7px;height:13px;border:solid var(--surface);border-width:0 3px 3px 0;transform:rotate(45deg)}}
.sr{{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}}
.exhead{{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 10px}}
.exhead h4{{font-size:1.25rem;font-weight:600;flex:1 1 auto;min-width:0}}
.tag{{font-family:var(--display);font-weight:700;background:var(--tag);color:var(--fg);border-radius:5px;padding:1px 7px;font-size:.95rem}}
.sets{{font-family:var(--display);font-weight:700;font-size:1.2rem;color:var(--accent);font-variant-numeric:tabular-nums;white-space:nowrap}}
.cue{{margin:4px 0 0;color:var(--muted);font-size:.95rem;max-width:62ch}}
.pics{{margin:10px 0 0;display:grid;grid-template-columns:1fr 1fr;gap:6px}}
.pics.n1{{grid-template-columns:minmax(0,220px)}}
.pics img{{width:100%;height:auto;max-width:100%;border-radius:6px;background:#fff;border:1px solid var(--line)}}
.pics figcaption{{grid-column:1/-1;font-size:.72rem;color:var(--muted);letter-spacing:.02em}}
.noimg{{margin-top:8px;font-size:.78rem;color:var(--muted);font-style:italic}}
.note{{margin-top:8px}}
.note input{{width:100%;max-width:220px;border:1px dashed var(--line);border-radius:6px;background:transparent;color:var(--fg);font:inherit;font-size:.9rem;padding:4px 8px}}
.note input:focus{{outline:2px solid var(--accent);border-style:solid}}
.resetrow{{margin:14px 0 0}}
.reset{{font:inherit;font-size:.85rem;background:transparent;color:var(--muted);border:1px solid var(--line);border-radius:6px;padding:6px 10px;cursor:pointer}}
details{{border-top:1px solid var(--line);padding-block:10px}}
details summary{{font-family:var(--display);font-size:1.3rem;font-weight:700;cursor:pointer;text-transform:uppercase;letter-spacing:.03em}}
details ul{{padding-left:20px;margin:8px 0 0}}
details li{{margin-bottom:6px;max-width:65ch}}
.ref{{margin-top:28px}}
.glance{{display:grid;grid-template-columns:auto 1fr;gap:4px 12px;margin:10px 0 0;font-size:.95rem}}
.glance dt{{font-family:var(--display);font-weight:700;font-size:1.05rem}}
.glance dd{{margin:0;color:var(--muted)}}
.src{{font-size:.8rem;color:var(--muted);margin-top:20px;max-width:65ch}}
@media (prefers-reduced-motion:no-preference){{.ex{{transition:opacity .2s}}}}
</style>
<div class="wrap">
 <header class="top">
  <p class="eyebrow">Body-Solid G9S home gym · bands · treadmill · bike</p>
  <h1>Jenn's Weekly Workout</h1>
  <p>Glutes, legs, back, core and cardio. Every session about 60 minutes. You set all weights and pick the band strength. Tap the box when an exercise is done; the dashed field remembers your pin number or band.</p>
 </header>
 <nav class="tabs" role="tablist" aria-label="Day">{tabs}</nav>
 {days}
 <section class="ref">
  <details open>
   <summary>How to use</summary>
   <ul>
    <li>"3 x 10-12" = 3 sets of 10 to 12 reps. "/leg" or "/side" = each side.</li>
    <li>Supersets (A1/A2): 1 set of A1, then 1 set of A2, rest 60-90 sec, repeat. Each pair uses only one machine station.</li>
    <li>Weight: last 2 reps of each set should be hard with clean form. Go lighter in week 1.</li>
    <li>Breathing: exhale on exertion, inhale on the return.</li>
    <li>Band anchors: "anchored low/chest height/high" = band hooked to the machine frame at that height. "Hooked to ankle" = band clipped to an ankle cuff. "Stand on band" = band under your feet, handles in your hands.</li>
    <li>Cardio effort (RPE 1-10): Easy = 3-4 | Zone 2 = 5-6 (can talk in full sentences) | Hard = 8-9 (only a few words)</li>
    <li>Belly fat: no exercise burns fat from one spot. It comes off with overall fat loss, the cardio and lifting here plus a modest calorie deficit. The core work tightens and strengthens the midsection underneath.</li>
    <li>Glute Kickback and Leg Abduction (machine) need an Ankle Strap on the low pulley. Use the band set's ankle cuff if it clips onto the cable. Otherwise do the band version listed.</li>
   </ul>
  </details>
  <details>
   <summary>Week at a glance</summary>
   <dl class="glance">
    <dt>Mon</dt><dd>Glutes & hamstrings + lats + core + bike sprints 10 min</dd>
    <dt>Tue</dt><dd>Treadmill incline walk Zone 2 30 min + band core & back</dd>
    <dt>Wed</dt><dd>Thighs (front, inner, outer) + mid & lower back + treadmill incline walk 10 min</dd>
    <dt>Thu</dt><dd>Bike 4x4 intervals 28 min + core</dd>
    <dt>Fri</dt><dd>Glutes & legs + lats + core + bike tempo 10 min</dd>
    <dt>Sat</dt><dd>Bike + treadmill Zone 2 40 min + band glute & thigh circuit</dd>
    <dt>Sun</dt><dd>Rest or easy recovery</dd>
   </dl>
  </details>
  <details>
   <summary>Progression</summary>
   <ul>
    <li>Hit the top of the rep range on every set with clean form, then add weight next session.</li>
    <li>Band moves: when one gets easy, move up a band (light to medium to heavy), stand with a wider grip/more stretch, or slow the lowering to 3 sec.</li>
    <li>Track the pin number. Per the chart: Leg Press = 200% of stack, Leg Extension/Leg Curl = 150%, pulleys and press handles = 100%.</li>
    <li>Progress cardio by speed, incline or bike resistance at the same RPE, not by adding time.</li>
    <li>Every 6-8 weeks, take an easy week: same exercises, about half the sets.</li>
   </ul>
  </details>
  <details>
   <summary>Safety (from the chart)</summary>
   <ul>
    <li>Inspect cables before every session; replace any worn cable before using the machine.</li>
    <li>Check that pop pins and adjustment points are in place and tight.</li>
    <li>Check bands and clips for nicks or wear before each use.</li>
   </ul>
  </details>
  <p class="src">Photos: machine exercises are from the workout pages of the Body-Solid G9 owner's manual (the full-size exercise chart that ships with the gym is not published online). Band and bodyweight exercises use the nearest demo from the Free Exercise DB (github.com/yuhonas/free-exercise-db); where the caption says "closest match" the demo uses different equipment, so follow the written cue. Exercises with no close match show no photo.</p>
 </section>
</div>
<script>
(function(){{
 var store={{get:function(k){{try{{return localStorage.getItem(k)}}catch(e){{return null}}}},set:function(k,v){{try{{localStorage.setItem(k,v)}}catch(e){{}}}},del:function(k){{try{{localStorage.removeItem(k)}}catch(e){{}}}}}};
 var tabs=document.querySelectorAll('.tab'), days=document.querySelectorAll('.day');
 function show(key){{
  days.forEach(function(d){{d.hidden=(d.id!==key)}});
  tabs.forEach(function(t){{t.setAttribute('aria-selected',t.dataset.day===key?'true':'false')}});
  store.set('jw-day',key);
 }}
 tabs.forEach(function(t){{t.addEventListener('click',function(){{show(t.dataset.day);window.scrollTo({{top:0}})}})}});
 var start=(location.hash||'').replace('#','');
 if(!document.getElementById(start)||!/^(mon|tue|wed|thu|fri|sat|sun)$/.test(start)){{
  var saved=store.get('jw-day'); var today=['sun','mon','tue','wed','thu','fri','sat'][new Date().getDay()];
  start=saved||today;
 }}
 show(start);
 document.querySelectorAll('.done input').forEach(function(c){{
  var k='jw-'+c.dataset.key, v=store.get(k), ex=c.closest('.ex');
  if(v==='1'){{c.checked=true;ex.classList.add('is-done')}}
  c.addEventListener('change',function(){{ex.classList.toggle('is-done',c.checked); if(c.checked)store.set(k,'1'); else store.del(k)}});
 }});
 document.querySelectorAll('.note input').forEach(function(n){{
  var k='jw-'+n.dataset.key, v=store.get(k); if(v)n.value=v;
  n.addEventListener('input',function(){{ if(n.value)store.set(k,n.value); else store.del(k)}});
 }});
 document.querySelectorAll('.reset').forEach(function(b){{
  b.addEventListener('click',function(){{
   document.querySelectorAll('#'+b.dataset.day+' .done input').forEach(function(c){{c.checked=false;c.closest('.ex').classList.remove('is-done');store.del('jw-'+c.dataset.key)}});
  }});
 }});
}})();
</script>
'''
os.makedirs(os.path.dirname(OUT),exist_ok=True)
open(OUT,'w').write(page)
# verify every referenced image exists
refs=set(re.findall(r'src="(img/[^"]+)"',page))
missing=[r for r in refs if not os.path.exists(os.path.join(os.path.dirname(OUT),r))]
print('bytes',len(page.encode()),'images referenced',len(refs),'missing',missing)
