#!/usr/bin/env python3
"""Generate the billing.thonly.com artboards and canvas.json.

    python3 build-boards.py && python3 build-index.py && python3 build-wall.py

The spec is private; these drawings follow it. The neutrals and the emblem are READ from the vendored brand layer (brand.py,
guarded by scripts/check-brand.mjs); this surface's accent is the one marked block in board.base.css.

The build refuses, in every language it can check: "sign in", the regulated words, a named currency, "running low", and any
internal name. Names here are made up, and every amount is a stand-in.
The Khmer is OURS and UNREVIEWED; every Khmer board says so in its top band.
"""
import hashlib, io, json, os, re
from brand import EMBLEM, tok

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 390, 844
CSS = io.open(os.path.join(HERE, "board.base.css"), encoding="utf-8").read()

BARRED = [r"\bsign[\s-]?in\b", r"\bdeposit", r"\bsavings\b", r"\binterest\b", r"\byield\b", r"\bcredits?\b", r"\baqua\b", r"\bprepaid\b",
          r"running low", r"\bwallet\b", r"b-ads?\b", r"usdmicros", r"\bearn\b", r"\bfree\b", r"\bexpires? (soon|in)\b"]


def brand_css(css):
    for k in ("bg", "surface", "surface-2", "line", "line-strong", "ink", "ink-dim", "ink-faint"):
        for p in ("l", "d"):
            css = css.replace("@%s_%s@" % (p.upper(), k.upper().replace("-", "_")), tok("%s-%s" % (p, k)))
    assert not re.search(r"@[A-Z_0-9]+@", css), "unfilled brand placeholder"
    return css


def mark():
    return ('<span class="wordmark">Heart<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="%s"/>'
            '</svg>ank<sup>®</sup></span>' % EMBLEM)


# ── spot drawings: flat, from the tokens, one per info card ───────────────────────────────────────────────────────
def spot(kind):
    a, l, f, s = "var(--accent)", "var(--line-strong)", "var(--surface-2)", "var(--ink-faint)"
    d = {
        "chip": '<rect x="10" y="4" width="36" height="32" rx="5" fill="%s" stroke="%s"/><rect x="19" y="13" width="18" height="14" rx="3" fill="%s"/>'
                '<path d="M4 14h6M4 26h6M46 14h6M46 26h6" stroke="%s" stroke-width="2.5" stroke-linecap="round"/>' % (f, l, a, l),
        "coin": '<circle cx="24" cy="20" r="15" fill="%s" stroke="%s"/><circle cx="24" cy="20" r="9" fill="none" stroke="%s" stroke-width="2.5"/>'
                '<path d="M42 12h10M42 20h7M42 28h10" stroke="%s" stroke-width="2.5" stroke-linecap="round"/>' % (f, l, a, l),
        "back": '<rect x="6" y="8" width="44" height="26" rx="5" fill="%s" stroke="%s"/><path d="M36 21H18m6-7-7 7 7 7" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>' % (f, l, a),
        "card": '<rect x="6" y="8" width="44" height="28" rx="5" fill="%s" stroke="%s"/><rect x="6" y="14" width="44" height="6" fill="%s"/><path d="M12 29h12" stroke="%s" stroke-width="2.5" stroke-linecap="round"/>' % (f, l, a, s),
        "cal":  '<rect x="10" y="7" width="36" height="30" rx="5" fill="%s" stroke="%s"/><rect x="10" y="7" width="36" height="8" rx="4" fill="%s"/><circle cx="20" cy="24" r="3.5" fill="%s"/><path d="M28 24h10M18 31h20" stroke="%s" stroke-width="2.5" stroke-linecap="round"/>' % (f, l, a, a, l),
        "link": '<rect x="3" y="11" width="20" height="18" rx="5" fill="%s" stroke="%s"/><rect x="33" y="11" width="20" height="18" rx="5" fill="%s" stroke="%s"/><path d="M23 20h10" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % (f, l, f, l, a),
        "fam":  '<circle cx="20" cy="13" r="7" fill="%s"/><path d="M8 36c0-10 6-14 12-14s12 4 12 14z" fill="%s"/><circle cx="39" cy="20" r="5" fill="%s"/><path d="M31 36c0-7 4-10 8-10s8 3 8 10z" fill="%s"/>' % (a, a, s, s),
        "biz":  '<path d="M9 16h38l-3-9H12z" fill="%s"/><rect x="11" y="16" width="34" height="20" fill="%s" stroke="%s"/><rect x="24" y="24" width="8" height="12" fill="%s"/>' % (a, f, l, l),
        "doc":  '<rect x="13" y="3" width="30" height="34" rx="4" fill="%s" stroke="%s"/><path d="M19 12h18M19 19h18M19 26h10" stroke="%s" stroke-width="2.5" stroke-linecap="round"/>' % (f, l, a),
        "hour": '<circle cx="28" cy="20" r="15" fill="%s" stroke="%s"/><path d="M28 12v9l6 4" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>' % (f, l, a),
    }[kind]
    return '<svg class="spot" width="56" height="40" viewBox="0 0 56 40" aria-hidden="true">%s</svg>' % d


def qr(seed=7):
    """A drawn stand-in for a QR code. It scans to nothing."""
    cells, n, u = [], 25, 8
    x = seed
    for r in range(n):
        for c in range(n):
            x = (x * 1103515245 + 12345) & 0x7fffffff
            corner = (r < 7 and c < 7) or (r < 7 and c >= n - 7) or (r >= n - 7 and c < 7)
            if not corner and x % 100 < 46:
                cells.append('<rect x="%d" y="%d" width="%d" height="%d"/>' % (c * u, r * u, u, u))
    for (cx, cy) in ((0, 0), ((n - 7) * u, 0), (0, (n - 7) * u)):
        cells.append('<path fill-rule="evenodd" d="M%d %dh56v56h-56zM%d %dv40h40v-40z"/><rect x="%d" y="%d" width="24" height="24"/>' % (cx, cy, cx + 8, cy + 8, cx + 16, cy + 16))
    return '<svg class="qr" viewBox="-8 -8 216 216" aria-label="A drawn QR code"><rect x="-8" y="-8" width="216" height="216" rx="10" fill="#fff"/><g fill="#14141c">%s</g></svg>' % "".join(cells)


# ── screens ────────────────────────────────────────────────────────────────────────────────────────────────────────
def tabs(t, on):
    names = [("bal", t("Balance", "សមតុល្យ")), ("his", t("History", "ប្រវត្តិ")), ("sch", t("Schedule", "កាលវិភាគ")), ("app", t("Apps", "កម្មវិធី")), ("fam", t("Family", "គ្រួសារ"))]
    return '<div class="tabs">%s</div>' % "".join('<span%s>%s</span>' % (' class="on"' if k == on else "", v) for k, v in names)


def row(t1, s, right):
    return '<div class="row"><div><div class="t">%s</div><div class="s">%s</div></div><div class="amt">%s</div></div>' % (t1, s, right)


def card(sp, h, p):
    return '<div class="card">%s<h2>%s</h2><p>%s</p></div>' % (spot(sp), h, p)


def B13(t):
    return ('<h1>%s</h1><p class="lede">%s</p>' % (t("Your balance for compute and storage", "សមតុល្យរបស់អ្នកសម្រាប់ការគណនា និងការផ្ទុកទិន្នន័យ"),
            t("Some things our apps do cost us money to run. When you pay for them, the money comes from one balance, kept here.", "កិច្ចការខ្លះក្នុងកម្មវិធីរបស់យើងមានថ្លៃដើម។ នៅពេលអ្នកបង់ថ្លៃ ប្រាក់នោះចេញពីសមតុល្យតែមួយ ដែលរក្សាទុកនៅទីនេះ។"))
            + card("chip", t("What you can buy", "អ្វីដែលអ្នកអាចទិញបាន"), t("Compute means the work a computer does for you. Storage means keeping your files. THonly.com sells both.", "ការគណនា គឺជាការងារដែលកុំព្យូទ័រធ្វើឱ្យអ្នក។ ការផ្ទុកទិន្នន័យ គឺការរក្សាឯកសាររបស់អ្នក។ THonly.com លក់ទាំងពីរ។"))
            + card("back", t("It stays yours", "វានៅតែជារបស់អ្នក"), t("Your balance never expires. Ask for the unspent part back at any time.", "សមតុល្យរបស់អ្នកមិនផុតកំណត់ឡើយ។ អ្នកអាចស្នើយកផ្នែកដែលមិនទាន់ចាយមកវិញបានគ្រប់ពេល។"))
            + '<div class="btn">%s</div>' % t("Log in with " + mark(), "ចូលដោយប្រើ " + mark()))


def B18(t):
    return ('<h1>%s</h1><p class="lede">%s</p><div class="field">%s</div><div class="btn">%s</div>'
            % (t("What year were you born?", "តើអ្នកកើតនៅឆ្នាំណា?"), t("Who can hold a balance depends on age. We use this for nothing else.", "អ្នកដែលអាចមានសមតុល្យអាស្រ័យលើអាយុ។ យើងមិនប្រើព័ត៌មាននេះសម្រាប់អ្វីផ្សេងទៀតទេ។"), "2010", t("Continue", "បន្ត"))
            + '<p class="sh">%s</p>' % t("How it works", "របៀបដំណើរការ")
            + card("fam", t("Under 18", "អាយុក្រោម ១៨ ឆ្នាំ"), t("From 13 to 17, you can pay for yourself once a parent agrees and sets a monthly limit. Under 13, a parent can cover you from their own balance.", "ពីអាយុ ១៣ ដល់ ១៧ ឆ្នាំ អ្នកអាចបង់ដោយខ្លួនឯងបាន នៅពេលមាតាបិតាយល់ព្រម និងកំណត់ដែនកំណត់ប្រចាំខែ។ ក្រោមអាយុ ១៣ ឆ្នាំ មាតាបិតាអាចបង់ជំនួសពីសមតុល្យរបស់គាត់។")))


def history_rows(t):
    return (row(t("Added by card", "បញ្ចូលតាមប័ណ្ណ"), t("Nov 1 · Receipt", "១ វិច្ឆិកា · បង្កាន់ដៃ"), "+$20.00")
            + row(t("B-Twin℠ · compute", "B-Twin℠ · ការគណនា"), t("Oct 30 · 41 uses", "៣០ តុលា · ៤១ ដង"), "−$0.16")
            + row(t("B-Origin℠ · records", "B-Origin℠ · កំណត់ត្រា"), t("Oct 30 · 12 records", "៣០ តុលា · ១២ កំណត់ត្រា"), "−$0.12"))


def B1(t):
    return (tabs(t, "bal") + '<p class="sh">%s</p><div class="bal">$42.50</div><p class="lede">%s</p>' % (t("Your balance", "សមតុល្យរបស់អ្នក"), t("For compute and storage from THonly.com.", "សម្រាប់ការគណនា និងការផ្ទុកទិន្នន័យពី THonly.com។"))
            + '<div class="btn">%s</div><p class="sh">%s</p>' % (t("Add money", "បញ្ចូលប្រាក់"), t("Latest", "ថ្មីៗ"))
            + '<div class="card">%s</div>' % history_rows(t)
            + '<span class="more">%s</span>' % t("Get the unspent part back", "យកផ្នែកដែលមិនទាន់ចាយមកវិញ"))


def B1Z(t):
    return (tabs(t, "bal") + '<p class="sh">%s</p><div class="bal">$0.00</div><p class="lede">%s</p>' % (t("Your balance", "សមតុល្យរបស់អ្នក"), t("For compute and storage from THonly.com.", "សម្រាប់ការគណនា និងការផ្ទុកទិន្នន័យពី THonly.com។"))
            + '<div class="btn">%s</div>' % t("Add money", "បញ្ចូលប្រាក់")
            + card("chip", t("Our apps still work", "កម្មវិធីរបស់យើងនៅតែដំណើរការ"), t("Whatever an app gives everyone, and anything someone gave you, doesn't use this balance.", "អ្វីដែលកម្មវិធីផ្តល់ជូនគ្រប់គ្នា និងអ្វីដែលគេបានឱ្យអ្នក មិនប្រើសមតុល្យនេះទេ។")))


def B2(t):
    return ('<h1>%s</h1><div class="chips"><span class="chip">$5</span><span class="chip on">$20</span><span class="chip">$50</span><span class="chip">%s</span></div>' % (t("Add money", "បញ្ចូលប្រាក់"), t("Other", "ផ្សេងទៀត"))
            + '<div class="note" style="margin-top:18px">%s</div>' % t("This balance buys compute and storage from THonly.com. It never expires. Ask for the unspent part back at any time. It can't be sent to anyone.", "សមតុល្យនេះទិញការគណនា និងការផ្ទុកទិន្នន័យពី THonly.com។ វាមិនផុតកំណត់ឡើយ។ អ្នកអាចស្នើយកផ្នែកដែលមិនទាន់ចាយមកវិញបានគ្រប់ពេល។ វាមិនអាចផ្ញើទៅនរណាម្នាក់បានទេ។")
            + '<p class="sh">%s</p>' % t("Pay with", "បង់ដោយ")
            + '<div class="card"><div class="radio on"><i></i>%s</div><div class="radio"><i></i>KHQR</div></div>' % t("Card", "ប័ណ្ណ")
            + '<div class="btn">%s</div><p class="fine">%s</p>' % (t("Continue to pay $20.00", "បន្តទៅបង់ $20.00"), t("Card details go to our payment company, Stripe, on its own page. They never reach us.", "ព័ត៌មានប័ណ្ណទៅកាន់ក្រុមហ៊ុនទូទាត់ Stripe នៅលើទំព័ររបស់គេ។ វាមិនមកដល់យើងទេ។")))


def B3(t):
    return ('<h1>%s</h1><div class="bal">$62.50</div><p class="lede">%s</p>' % (t("$20.00 added", "បានបញ្ចូល $20.00"), t("Your balance now.", "សមតុល្យរបស់អ្នកឥឡូវនេះ។"))
            + card("doc", t("Your receipt", "បង្កាន់ដៃរបស់អ្នក"), t("We emailed it to you, and it's in your history.", "យើងបានផ្ញើវាតាមអ៊ីមែល ហើយវាមាននៅក្នុងប្រវត្តិរបស់អ្នក។"))
            + '<div class="btn ghost">%s</div>' % t("Back to balance", "ត្រឡប់ទៅសមតុល្យ"))


def B3X(t):
    return ('<h1>%s</h1><p class="lede">%s</p>' % (t("The card was declined", "ប័ណ្ណត្រូវបានបដិសេធ"), t("Nothing was charged, and your balance hasn't changed.", "មិនមានការកាត់ប្រាក់ទេ ហើយសមតុល្យរបស់អ្នកមិនបានផ្លាស់ប្តូរទេ។"))
            + '<div class="btn">%s</div><div class="btn ghost">%s</div>' % (t("Try another way", "សាកល្បងវិធីផ្សេង"), t("Back to balance", "ត្រឡប់ទៅសមតុល្យ")))


def B14(t):
    return ('<h1>%s</h1><p class="lede">%s</p>%s' % (t("Pay $20.00 with KHQR", "បង់ $20.00 តាម KHQR"), t("Open your bank's app and scan this.", "បើកកម្មវិធីធនាគាររបស់អ្នក ហើយស្កេននេះ។"), qr())
            + '<dl class="kv"><dt>%s</dt><dd>[ %s ]</dd><dt>%s</dt><dd class="mono">KH-7Q2M</dd></dl>' % (t("Goes to", "ទៅកាន់"), t("account name", "ឈ្មោះគណនី"), t("Reference", "លេខយោង"))
            + '<div class="btn">%s</div><p class="fine">%s</p>' % (t("I've paid", "ខ្ញុំបានបង់ហើយ"), t("We add it after a person checks that it arrived.", "យើងបញ្ចូលវា បន្ទាប់ពីមនុស្សម្នាក់ពិនិត្យថាប្រាក់បានមកដល់។")))


def B15(t):
    return ('<h1>%s</h1><p class="lede">%s</p>' % (t("Thanks. A person will check it.", "សូមអរគុណ។ មនុស្សម្នាក់នឹងពិនិត្យវា។"), t("Your balance changes once it's confirmed. You can close this page.", "សមតុល្យរបស់អ្នកផ្លាស់ប្តូរនៅពេលបានបញ្ជាក់។ អ្នកអាចបិទទំព័រនេះបាន។"))
            + card("hour", t("If it was added", "ប្រសិនបើបានបញ្ចូល"), t("You'll see $20.00 in your history, with a receipt.", "អ្នកនឹងឃើញ $20.00 ក្នុងប្រវត្តិ ជាមួយបង្កាន់ដៃ។"))
            + card("doc", t("If we couldn't find it", "ប្រសិនបើយើងរកមិនឃើញ"), t("We'll say so once, by email, with the reference KH-7Q2M, so your bank can help you trace it.", "យើងនឹងប្រាប់ម្តងតាមអ៊ីមែល ជាមួយលេខយោង KH-7Q2M ដើម្បីឱ្យធនាគាររបស់អ្នកអាចជួយតាមដាន។")))


def B4(t):
    return tabs(t, "his") + '<h1>%s</h1><div class="card">%s%s%s</div><p class="fine">%s</p>' % (t("History", "ប្រវត្តិ"), history_rows(t),
            row(t("Added by KHQR", "បញ្ចូលតាម KHQR"), t("Oct 12 · Receipt", "១២ តុលា · បង្កាន់ដៃ"), "+$10.00"), row(t("Returned to your card", "ត្រឡប់ទៅប័ណ្ណរបស់អ្នក"), t("Sep 29", "២៩ កញ្ញា"), "−$5.00"),
            t("This lists what was used, never what it was used on: no files, no messages, no names.", "បញ្ជីនេះបង្ហាញអ្វីដែលបានប្រើ មិនមែនប្រើលើអ្វីទេ៖ គ្មានឯកសារ គ្មានសារ គ្មានឈ្មោះ។"))


def B5(t):
    return ('<h1>%s</h1><div class="card"><dl class="kv"><dt>%s</dt><dd>[ %s ]</dd><dt>%s</dt><dd>%s</dd><dt>%s</dt><dd>$20.00</dd><dt>%s</dt><dd>$20.00</dd><dt>%s</dt><dd>Visa ···· 4242</dd><dt>%s</dt><dd class="mono">R-20261101-3F</dd></dl></div>'
            % (t("Receipt", "បង្កាន់ដៃ"), t("Sold by", "លក់ដោយ"), t("the seller's legal name", "ឈ្មោះស្របច្បាប់របស់អ្នកលក់"), t("Date", "កាលបរិច្ឆេទ"), t("Nov 1, 2026", "១ វិច្ឆិកា ២០២៦"), t("You paid", "អ្នកបានបង់"), t("Added to balance", "បានបញ្ចូលទៅសមតុល្យ"), t("Paid with", "បង់ដោយ"), t("Number", "លេខ"))
            + '<p class="fine">%s</p>' % t("Your statement shows THONLY.COM.", "របាយការណ៍ប័ណ្ណរបស់អ្នកបង្ហាញ THONLY.COM។"))


def B6(t):
    return (tabs(t, "sch") + '<h1>%s</h1><p class="lede">%s</p><p class="sh">%s</p><div class="chips"><span class="chip">$5</span><span class="chip on">$10</span><span class="chip">$20</span><span class="chip">%s</span></div><p class="sh">%s</p><div class="field">%s</div>'
            % (t("Add money each month", "បញ្ចូលប្រាក់រៀងរាល់ខែ"), t("Only if you want it. This is off until you set it.", "តែបើអ្នកចង់។ វាបិទរហូតដល់អ្នកកំណត់។"), t("Amount", "ចំនួន"), t("Other", "ផ្សេងទៀត"), t("Day of the month", "ថ្ងៃនៃខែ"), t("1st", "ថ្ងៃទី ១"))
            + '<div class="note" style="margin-top:14px">%s</div><div class="btn">%s</div>' % (t("We will charge this card $10.00 on the 1st of each month and add it to your balance, until you stop it. Stop any time on this page, and it stops at once. We email a receipt each time.", "យើងនឹងកាត់ប័ណ្ណនេះ $10.00 នៅថ្ងៃទី ១ រៀងរាល់ខែ ហើយបញ្ចូលទៅសមតុល្យរបស់អ្នក រហូតដល់អ្នកបញ្ឈប់។ អ្នកអាចបញ្ឈប់នៅទំព័រនេះគ្រប់ពេល ហើយវាឈប់ភ្លាមៗ។ យើងផ្ញើបង្កាន់ដៃតាមអ៊ីមែលរាល់ដង។"), t("Save my card and set it", "រក្សាទុកប័ណ្ណ ហើយកំណត់")))


def B7(t):
    return (tabs(t, "sch") + '<h1>%s</h1><div class="card">%s<h2>%s</h2><p>%s</p></div><div class="btn ghost">%s</div>' % (t("Each month", "រៀងរាល់ខែ"), spot("cal"), t("$10.00 on the 1st", "$10.00 នៅថ្ងៃទី ១"), t("Visa ···· 4242. Next on Dec 1.", "Visa ···· 4242។ លើកក្រោយ ១ ធ្នូ។"), t("Stop", "បញ្ឈប់"))
            + '<p class="sh">%s</p>' % t("If a charge fails", "ប្រសិនបើការកាត់ប្រាក់បរាជ័យ")
            + '<div class="note">%s</div><div class="note">%s</div>' % (t("The card was declined on Nov 1. We'll try again on Dec 1.", "ប័ណ្ណត្រូវបានបដិសេធនៅថ្ងៃ ១ វិច្ឆិកា។ យើងនឹងសាកល្បងម្តងទៀតនៅថ្ងៃ ១ ធ្នូ។"), t("Paused after two declines. Set it again whenever you like.", "បានផ្អាកបន្ទាប់ពីត្រូវបដិសេធពីរដង។ អ្នកអាចកំណត់ឡើងវិញនៅពេលណាក៏បាន។")))


def B8(t):
    return (tabs(t, "app") + '<h1>%s</h1><p class="lede">%s</p><div class="card">%s%s</div>' % (t("Apps that can spend this", "កម្មវិធីដែលអាចចាយសមតុល្យនេះ"), t("Each one asked you first. An app only learns whether a payment went through, never your balance.", "កម្មវិធីនីមួយៗបានសួរអ្នកមុន។ កម្មវិធីដឹងតែថាការបង់ប្រាក់បានសម្រេចឬអត់ មិនដែលដឹងសមតុល្យរបស់អ្នកទេ។"),
            '<div class="row"><div><div class="t">B-Twin℠</div><div class="s">%s</div></div><span class="pill">%s</span></div>' % (t("Compute", "ការគណនា"), t("Disconnect", "ផ្តាច់")),
            '<div class="row"><div><div class="t">B-Origin℠</div><div class="s">%s</div></div><span class="pill">%s</span></div>' % (t("Records and lookups", "កំណត់ត្រា និងការស្វែងរក"), t("Disconnect", "ផ្តាច់"))))


def B9(t):
    return ('<h1>%s</h1><p class="lede">%s</p>' % (t("Let this app spend from your balance?", "អនុញ្ញាតឱ្យកម្មវិធីនេះចាយពីសមតុល្យរបស់អ្នកទេ?"), t("Little Lantern Games on B-Origin℠ is asking.", "Little Lantern Games នៅលើ B-Origin℠ កំពុងស្នើសុំ។"))
            + card("link", t("It can pay for", "វាអាចបង់សម្រាប់"), t("Signed records at $0.01 each, and lookups at $0.005 each.", "កំណត់ត្រាដែលបានចុះហត្ថលេខា $0.01 ក្នុងមួយ និងការស្វែងរក $0.005 ក្នុងមួយ។"))
            + card("doc", t("It can't", "វាមិនអាច"), t("See your balance, your card or your history. You can disconnect it at any time.", "មើលសមតុល្យ ប័ណ្ណ ឬប្រវត្តិរបស់អ្នកឡើយ។ អ្នកអាចផ្តាច់វាបានគ្រប់ពេល។"))
            + '<div class="btn">%s</div><div class="btn ghost">%s</div>' % (t("Allow", "អនុញ្ញាត"), t("Not now", "មិនមែនឥឡូវ")))


def B10(t):
    return ('<h1>%s</h1><div class="bal">$42.50</div><p class="lede">%s</p>' % (t("Get the unspent part back", "យកផ្នែកដែលមិនទាន់ចាយមកវិញ"), t("It goes back the way you paid, newest payment first.", "វាត្រឡប់តាមវិធីដែលអ្នកបានបង់ ដោយចាប់ពីការបង់ថ្មីបំផុត។"))
            + '<div class="card">%s%s</div>' % (row("Visa ···· 4242", t("From your last two card payments", "ពីការបង់ប្រាក់តាមប័ណ្ណពីរលើកចុងក្រោយ"), "$32.50"), row("KHQR", t("Sent back to the account that paid", "ផ្ញើត្រឡប់ទៅគណនីដែលបានបង់"), "$10.00"))
            + '<div class="check"><b>✓</b><span>%s</span></div>' % t("Also stop adding money each month.", "បញ្ឈប់ការបញ្ចូលប្រាក់រៀងរាល់ខែផងដែរ។")
            + '<div class="btn">%s</div><p class="fine">%s</p>' % (t("Send back $42.50", "ផ្ញើត្រឡប់ $42.50"), t("Anything bought through Apple or Google is returned by them, not by us.", "អ្វីដែលទិញតាម Apple ឬ Google ត្រូវបានសងវិញដោយពួកគេ មិនមែនដោយយើងទេ។")))


def B11(t):
    return ('<h1>%s</h1><p class="lede">%s</p>' % (t("It's on its way back", "វាកំពុងត្រឡប់មកវិញ"), t("A card usually shows it within 5 to 10 business days.", "ជាធម្មតា ប័ណ្ណបង្ហាញវាក្នុងរយៈពេល ៥ ទៅ ១០ ថ្ងៃធ្វើការ។"))
            + '<div class="card">%s%s</div>' % (row("Visa ···· 4242", t("Sent", "បានផ្ញើ"), "$32.50"), row("KHQR", t("A person is sending it", "មនុស្សម្នាក់កំពុងផ្ញើ"), "$10.00"))
            + '<p class="sh">%s</p><div class="note">%s</div>' % (t("If it can't go back", "ប្រសិនបើវាមិនអាចត្រឡប់បាន"), t("Your card couldn't take it, so $12.50 is back in your balance. We'll write to you to arrange another way.", "ប័ណ្ណរបស់អ្នកមិនអាចទទួលបាន ដូច្នេះ $12.50 បានត្រឡប់មកសមតុល្យវិញ។ យើងនឹងសរសេរមកអ្នក ដើម្បីរៀបចំវិធីផ្សេង។")))


def B12(t):
    return ('<h1>%s</h1><p class="lede">%s</p><div class="card">%s%s</div><div class="btn ghost">%s</div>' % (t("Your accounts", "គណនីរបស់អ្នក"), t("One login can hold a personal balance and a balance for each business.", "ការចូលមួយអាចមានសមតុល្យផ្ទាល់ខ្លួន និងសមតុល្យសម្រាប់អាជីវកម្មនីមួយៗ។"),
            row(t("Mey (you)", "ម៉ី (អ្នក)"), t("Personal", "ផ្ទាល់ខ្លួន"), "$42.50"), row("Little Lantern Games", t("Business · Billing email: hello@example.com", "អាជីវកម្ម · អ៊ីមែល៖ hello@example.com"), "$118.00"), t("Add a business", "បន្ថែមអាជីវកម្ម"))
            + card("biz", t("A business's use", "ការប្រើរបស់អាជីវកម្ម"), t("One line a day for each app. You can recount signed records yourself from the public log.", "មួយជួរក្នុងមួយថ្ងៃសម្រាប់កម្មវិធីនីមួយៗ។ អ្នកអាចរាប់កំណត់ត្រាដែលបានចុះហត្ថលេខាឡើងវិញដោយខ្លួនឯង ពីកំណត់ហេតុសាធារណៈ។")))


def B16(t):
    return ('<h1>%s</h1><p class="lede">%s</p>%s' % (t("Ask a parent", "សួរមាតាបិតា"), t("You can pay for yourself once a parent agrees. Show them this, on their phone.", "អ្នកអាចបង់ដោយខ្លួនឯង នៅពេលមាតាបិតាយល់ព្រម។ បង្ហាញនេះដល់គាត់ លើទូរសព្ទរបស់គាត់។"), qr(11))
            + '<p class="sh">%s</p>' % t("What the parent sees", "អ្វីដែលមាតាបិតាឃើញ")
            + '<div class="card"><h2>%s</h2><p>%s</p><div class="chips"><span class="chip">$5</span><span class="chip on">$10</span><span class="chip">$20</span></div><div class="btn">%s</div></div>' % (t("Dara asks to pay for compute and storage", "ដារ៉ាស្នើសុំបង់ថ្លៃការគណនា និងការផ្ទុកទិន្នន័យ"), t("You set the most Dara can add in a month. You can take this back at any time. You won't see what Dara does in the apps.", "អ្នកកំណត់ចំនួនច្រើនបំផុតដែលដារ៉ាអាចបញ្ចូលក្នុងមួយខែ។ អ្នកអាចដកការយល់ព្រមនេះបានគ្រប់ពេល។ អ្នកនឹងមិនឃើញអ្វីដែលដារ៉ាធ្វើក្នុងកម្មវិធីទេ។"), t("I'm the parent, and I agree", "ខ្ញុំជាមាតាបិតា ហើយខ្ញុំយល់ព្រម")))


def B17(t):
    return (tabs(t, "fam") + '<h1>%s</h1><div class="card">%s<h2>Dara</h2><p>%s</p><div class="chips"><span class="chip">%s</span><span class="chip">%s</span></div></div><div class="card">%s<h2>Nita</h2><p>%s</p><div class="chips"><span class="chip">%s</span><span class="chip">%s</span></div></div><p class="fine">%s</p>'
            % (t("Family", "គ្រួសារ"), spot("fam"), t("Pays for themselves. Up to $10.00 added a month.", "បង់ដោយខ្លួនឯង។ បញ្ចូលបានរហូតដល់ $10.00 ក្នុងមួយខែ។"), t("Change limit", "ប្តូរដែនកំណត់"), t("Take back", "ដកវិញ"),
               spot("link"), t("B-Twin℠ pays from your balance. Up to $5.00 a month.", "B-Twin℠ បង់ពីសមតុល្យរបស់អ្នក។ រហូតដល់ $5.00 ក្នុងមួយខែ។"), t("Change limit", "ប្តូរដែនកំណត់"), t("Disconnect", "ផ្តាច់"),
               t("You see limits and totals by app, never what a child made or said.", "អ្នកឃើញដែនកំណត់ និងចំនួនសរុបតាមកម្មវិធី មិនដែលឃើញអ្វីដែលកូនបានបង្កើត ឬនិយាយទេ។")))


def A1(t):
    item = '<div class="card"><div class="hr" style="justify-content:space-between"><span class="amt"><b>%s</b></span><span class="mono">%s</span></div><p>%s</p><div class="sheetrow"><div class="btn">%s</div><div class="btn ghost">%s</div></div></div>'
    return ('<h1>%s</h1><p class="lede">%s</p>' % (t("KHQR to check", "KHQR ដែលត្រូវពិនិត្យ"), t("Find each one in the receiving account, then say what you saw. A balance moves only on Received.", "រកមើលនីមួយៗក្នុងគណនីទទួល រួចប្រាប់អ្វីដែលអ្នកបានឃើញ។ សមតុល្យផ្លាស់ប្តូរតែនៅពេលចុច បានទទួល។"))
            + item % ("$20.00", "KH-7Q2M", t("Mey · 12 minutes ago", "ម៉ី · ១២ នាទីមុន"), t("Received", "បានទទួល"), t("Not found", "រកមិនឃើញ"))
            + item % ("៛40,000", "KH-3D9A", t("Sokha · 2 hours ago", "សុខា · ២ ម៉ោងមុន"), t("Received", "បានទទួល"), t("Not found", "រកមិនឃើញ"))
            + '<p class="sh">%s</p>' % t("To send back", "ដើម្បីផ្ញើត្រឡប់")
            + '<div class="card"><div class="hr" style="justify-content:space-between"><span class="amt"><b>$10.00</b></span><span class="mono">KH-1P8C</span></div><p>%s</p><div class="sheetrow"><div class="btn">%s</div><div class="btn ghost">%s</div></div></div>' % (t("Mey · to the account that paid", "ម៉ី · ទៅគណនីដែលបានបង់"), t("Sent", "បានផ្ញើ"), t("Couldn't send", "មិនអាចផ្ញើ")))


def S1(t):
    return ('<h1>Little Lantern Games</h1><p class="lede">%s</p><div class="card">%s<h2>%s</h2><p>%s</p></div><div class="btn">%s</div>'
            % (t("Your B-Origin℠ business", "អាជីវកម្ម B-Origin℠ របស់អ្នក"), spot("link"), t("Paying for use", "ការបង់ថ្លៃការប្រើ"), t("Signed records and lookups are paid from a balance at billing.thonly.com. B-Origin℠ holds no money.", "កំណត់ត្រាដែលបានចុះហត្ថលេខា និងការស្វែងរក ត្រូវបង់ពីសមតុល្យនៅ billing.thonly.com។ B-Origin℠ មិនកាន់ប្រាក់ទេ។"), t("Connect a balance", "ភ្ជាប់សមតុល្យ"))
            + '<p class="sh">%s</p><div class="field">%s</div><p class="fine">%s</p>' % (t("Your own monthly cap", "ដែនកំណត់ប្រចាំខែរបស់អ្នក"), "$100.00", t("At your cap, or at zero, paid API calls stop with a clear error. A person's own Sign is never touched.", "នៅដែនកំណត់ ឬនៅសូន្យ ការហៅ API ដែលត្រូវបង់នឹងឈប់ជាមួយកំហុសច្បាស់លាស់។ Sign ផ្ទាល់ខ្លួនរបស់មនុស្សម្នាក់មិនត្រូវបានប៉ះពាល់ទេ។")))


def sheet(t, body):
    return '<div class="app" style="padding:0"><div class="scrim"></div><div class="sheet" style="top:auto;bottom:0"><div class="grab"></div>%s</div></div>' % body


def S2(t):
    return ('<h1>%s</h1><p class="lede">%s</p>' % (t("This render costs $0.004.", "ការបង្ហាញនេះមានតម្លៃ $0.004។"), t("Drawn in the app, when the day's share and any gift are used.", "គូរក្នុងកម្មវិធី នៅពេលចំណែកប្រចាំថ្ងៃ និងអំណោយត្រូវបានប្រើអស់។"))
            + '<div class="card"><div class="sheetrow"><div class="btn">%s</div><div class="btn">%s</div></div></div>' % (t("Pay $0.004", "បង់ $0.004"), t("Watch one ad", "មើលការផ្សាយមួយ"))
            + '<p class="plain">%s</p>' % t("Not now", "មិនមែនឥឡូវ")
            + '<p class="sh">%s</p>' % t("Where there is no ad", "កន្លែងដែលគ្មានការផ្សាយ")
            + '<div class="card"><div class="btn">%s</div><span class="plain">%s</span></div>' % (t("Pay $0.004", "បង់ $0.004"), t("Not now", "មិនមែនឥឡូវ")))


def S3(t):
    return ('<h1>%s</h1><p class="lede">%s</p>' % (t("Add to your balance", "បញ្ចូលទៅសមតុល្យរបស់អ្នក"), t("Through Apple, in the app, outside the United States.", "តាម Apple ក្នុងកម្មវិធី នៅក្រៅសហរដ្ឋអាមេរិក។"))
            + '<div class="card">%s%s</div>' % (row("$4.99", t("Adds $4.24", "បញ្ចូល $4.24"), '<span class="pill">%s</span>' % t("Buy", "ទិញ")), row("$9.99", t("Adds $8.49", "បញ្ចូល $8.49"), '<span class="pill">%s</span>' % t("Buy", "ទិញ")))
            + '<p class="fine">%s</p>' % t("[ Placeholder figures. ] It never expires. Apple handles any refund on these.", "[ តួលេខគំរូ។ ] វាមិនផុតកំណត់ឡើយ។ Apple ដោះស្រាយការសងប្រាក់វិញសម្រាប់ការទិញទាំងនេះ។"))


SCREENS = [
    ("B13", "billing", "Before you log in", B13), ("B18", "billing", "Your age", B18), ("B1", "billing", "Balance", B1), ("B1Z", "billing", "Balance at zero", B1Z),
    ("B2", "billing", "Add money", B2), ("B3", "billing", "Added", B3), ("B3X", "billing", "Declined", B3X), ("B14", "billing", "Pay with KHQR", B14), ("B15", "billing", "KHQR, waiting", B15),
    ("B4", "billing", "History", B4), ("B5", "billing", "Receipt", B5), ("B6", "billing", "Set a monthly top-up", B6), ("B7", "billing", "Monthly top-up on", B7),
    ("B8", "billing", "Apps", B8), ("B9", "billing", "An app asks", B9), ("B10", "billing", "Get it back", B10), ("B11", "billing", "Sent back", B11), ("B12", "billing", "Accounts", B12),
    ("B16", "family", "A teen asks a parent", B16), ("B17", "family", "A parent's page", B17),
    ("A1", "admin", "KHQR to check", A1),
    ("S1", "apps", "B-Origin: connect a balance", S1), ("S2", "apps", "B-Twin: the price at the moment", S2), ("S3", "apps", "B-Twin: in-app purchase", S3),
]
PUBLIC = {"B13"}
SHARE = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 15V3m0 0L7 8m5-5 5 5"/><path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7"/></svg>'


def page(sid, render, lang, dark=False):
    km = lang == "km"
    t = (lambda e, k: k) if km else (lambda e, k: e)
    body = render(t).replace("℠", '<span class="sm">℠</span>')
    plain = re.sub(r"<[^>]+>", " ", body)
    for pat in BARRED + ([r"ឥតគិតថ្លៃ"] if km else []):
        assert not re.search(pat, plain, re.I), "%s/%s: barred word %r" % (sid, lang, pat)
    if km:
        for m in re.finditer(r"ធនាគារ", plain):
            assert "របស់អ្នក" in plain[m.start():m.start() + 24], "%s: Khmer bank word used of anything but the reader's own bank" % sid
    band = "នេះជាសេចក្តីព្រាងភាសាខ្មែររបស់យើង រហូតដល់អ្នកអានជនជាតិខ្មែរអនុម័ត។" if km else ""
    foot = t("Drawings. They charge nobody.", "គំនូរទាំងនេះមិនកាត់ប្រាក់នរណាទេ។") + (t(" Visits are counted without cookies.", " ការចូលមើលត្រូវបានរាប់ដោយគ្មានខូគី។") if sid in PUBLIC else "")
    themes = "".join('<span%s>%s</span>' % (' class="on"' if i == (2 if dark else 0) else "", x) for i, x in enumerate(t(("System", "Light", "Dark"), ("ប្រព័ន្ធ", "ភ្លឺ", "ងងឹត"))))
    langs = "".join('<span%s>%s</span>' % (' class="on"' if (i == 0) == (not km) else "", x) for i, x in enumerate(("EN", "ខ្មែរ")))
    head = ('<span class="wm">THonly<sup>™</sup><em>%s</em></span>' % t("Billing", "វិក្កយបត្រ")) if sid[0] != "S" else '<span class="wm">%s</span>' % ("B-Origin℠" if sid == "S1" else "B-Twin℠")
    if sid[0] == "S": head = head.replace("℠", '<span class="sm">℠</span>')
    return """<!doctype html>
<html lang="%s" class="%s%s">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=%d">
<meta name="googlebot" content="noindex,nofollow"><meta name="bingbot" content="noindex,nofollow">
<meta name="slurp" content="noindex,nofollow"><meta name="yandex" content="noindex,nofollow">
<title>billing.thonly.com drawings · %s</title>
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<style>[hidden]{display:none!important}</style>
<link rel="stylesheet" href="board.css?v=@CSSV@">
</head>
<body>
%s<div class="app">
<header><span class="hl">%s</span><span class="hr"><span class="seg">%s</span>%s</span></header>
%s
<div class="grow"></div>
<footer><span>%s</span><span class="seg">%s</span></footer>
</div>
</body>
</html>
""" % (lang, lang, " dark" if dark else "", W, sid, '<div class="band">%s</div>' % band if band else "", head, langs,
       ('<span class="sharebtn" aria-label="%s">%s</span>' % (t("Share", "ចែករំលែក"), SHARE)) if sid in PUBLIC else "", body, foot, themes)


def main():
    css = brand_css(CSS)
    io.open(os.path.join(HERE, "board.css"), "w", encoding="utf-8").write(css)
    cssv = hashlib.sha256(css.encode()).hexdigest()[:8]
    hpath = os.path.join(HERE, "heights.json")
    hts = json.load(io.open(hpath)) if os.path.exists(hpath) else {}
    hh = lambda f: max(H, int(hts.get(f, H)))
    tall_en = max([H] + [int(v) for k, v in hts.items() if not k.endswith("Km.html")])
    tall_km = max([H] + [int(v) for k, v in hts.items() if k.endswith("Km.html")])
    pages = [{"id": "billing", "name": "billing.thonly.com"}, {"id": "family", "name": "Family"}, {"id": "admin", "name": "The KHQR queue"}, {"id": "apps", "name": "Inside the apps"}]
    boards, col = [], {p["id"]: 0 for p in pages}
    rowy = {"en": 0, "km": tall_en + 160}
    for sid, pg, title, render in SCREENS:
        for lang in ("en", "km"):
            f = "%s%s.html" % (sid, "" if lang == "en" else "Km")
            io.open(os.path.join(HERE, f), "w", encoding="utf-8").write(page(sid, render, lang).replace("@CSSV@", cssv))
            boards.append({"file": f, "page": pg, "title": "%s · %s, %s" % (sid, title, "English" if lang == "en" else "Khmer"), "w": W, "h": hh(f), "x": col[pg] * (W + 80), "y": rowy[lang]})
        col[pg] += 1
    f = "B1Dark.html"  # one dark pass (Default 6)
    io.open(os.path.join(HERE, f), "w", encoding="utf-8").write(page("B1", B1, "en", dark=True).replace("@CSSV@", cssv))
    boards.append({"file": f, "page": "billing", "title": "B1 · dark pass, English", "w": W, "h": hh(f), "x": 0, "y": rowy["km"] + tall_km + 160})
    canvas = {"pages": pages, "artboards": boards, "annotations": [], "launch": {"page": "billing", "view": "canvas"}}
    io.open(os.path.join(HERE, "canvas.json"), "w", encoding="utf-8").write(json.dumps(canvas, ensure_ascii=False, indent=1))
    print("%d artboards written · board.css v=%s" % (len(boards), cssv))


if __name__ == "__main__":
    main()
