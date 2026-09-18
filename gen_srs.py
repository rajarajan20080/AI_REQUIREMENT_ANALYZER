import csv, json, random, itertools

random.seed(20260917)

# ---------------- domains ----------------
# each: actors, entities, attributes (searchable fields), a few domain-specific extras
DOMAINS = {
"Online Bookstore": dict(
    primary="customer", admin="administrator",
    entities=["book","author profile","catalogue category","shopping cart item","order","book review","wishlist entry","promotional coupon","gift card","delivery address"],
    fields=["title","author","ISBN"], unit="order", money=True),
"Food Delivery": dict(
    primary="customer", admin="administrator",
    entities=["restaurant","menu item","food order","cart item","delivery agent record","order review","favourite restaurant","discount offer","saved address","payment method"],
    fields=["restaurant name","cuisine","location"], unit="order", money=True),
"Hospital Management": dict(
    primary="patient", admin="hospital administrator",
    entities=["doctor profile","appointment","prescription","lab report","medical record","ward bed","billing record","insurance claim","vaccination record","discharge summary"],
    fields=["doctor name","specialisation","department"], unit="appointment", money=True),
"E-Learning Platform": dict(
    primary="student", admin="administrator",
    entities=["course","lecture video","assignment","quiz","certificate","discussion thread","enrolment record","course review","study note","learning path"],
    fields=["course title","instructor","subject"], unit="enrolment", money=True),
"Banking System": dict(
    primary="account holder", admin="bank administrator",
    entities=["savings account","fund transfer","beneficiary","cheque request","loan application","standing instruction","transaction record","debit card","account statement","service request"],
    fields=["account number","beneficiary name","transaction reference"], unit="transaction", money=True),
"Hotel Booking": dict(
    primary="guest", admin="hotel manager",
    entities=["hotel listing","room","reservation","guest review","room service request","loyalty point record","cancellation request","invoice","saved hotel","special request"],
    fields=["hotel name","city","room type"], unit="reservation", money=True),
"Airline Reservation": dict(
    primary="passenger", admin="airline administrator",
    entities=["flight","seat","booking","baggage entry","boarding pass","fare rule","cancellation record","frequent flyer record","meal preference","travel document"],
    fields=["flight number","source and destination","travel date"], unit="booking", money=True),
"Library Management": dict(
    primary="member", admin="librarian",
    entities=["book copy","borrowing record","reservation request","fine record","membership profile","journal issue","return record","reading list","digital resource","overdue notice"],
    fields=["title","author","accession number"], unit="loan", money=False),
"Inventory Management": dict(
    primary="store operator", admin="warehouse administrator",
    entities=["stock item","purchase order","supplier record","goods receipt note","stock transfer","damaged goods entry","reorder rule","batch record","stock audit entry","barcode label"],
    fields=["item code","supplier name","category"], unit="purchase order", money=True),
"Payroll System": dict(
    primary="employee", admin="payroll administrator",
    entities=["salary slip","attendance record","leave application","reimbursement claim","tax declaration","bonus entry","deduction rule","bank detail record","overtime entry","appraisal record"],
    fields=["employee ID","department","month"], unit="payroll run", money=True),
"Ride Hailing": dict(
    primary="rider", admin="operations administrator",
    entities=["ride request","driver profile","trip record","fare estimate","saved location","trip rating","cancellation record","vehicle document","promo code","lost item report"],
    fields=["pickup location","drop location","vehicle type"], unit="trip", money=True),
"Social Networking": dict(
    primary="user", admin="moderator",
    entities=["post","comment","friend request","group","direct message","story","reported content item","profile photo","notification setting","blocked user entry"],
    fields=["username","hashtag","location"], unit="post", money=False),
"Hospital Pharmacy": dict(
    primary="pharmacist", admin="pharmacy administrator",
    entities=["medicine stock item","dispensing record","expiry alert","supplier invoice","prescription order","substitute drug entry","cold storage log","narcotic register entry","return-to-supplier record","reorder request"],
    fields=["drug name","batch number","manufacturer"], unit="dispensing record", money=True),
"Vehicle Rental": dict(
    primary="renter", admin="fleet administrator",
    entities=["vehicle listing","rental booking","damage report","insurance record","pickup schedule","return inspection","security deposit record","driver licence record","extension request","maintenance log"],
    fields=["vehicle model","pickup city","rental date"], unit="rental booking", money=True),
"Event Management": dict(
    primary="attendee", admin="event organiser",
    entities=["event listing","ticket","seat allocation","speaker profile","session schedule","attendee feedback","refund request","venue record","sponsor entry","check-in record"],
    fields=["event name","date","venue"], unit="ticket", money=True),
"Real Estate Portal": dict(
    primary="buyer", admin="portal administrator",
    entities=["property listing","site visit request","agent profile","shortlisted property","price alert","document upload","loan enquiry","locality report","listing photo set","ownership record"],
    fields=["locality","property type","budget range"], unit="listing", money=True),
"Crop Advisory": dict(
    primary="farmer", admin="agriculture officer",
    entities=["crop record","soil test report","irrigation schedule","pest alert","fertiliser recommendation","market price entry","subsidy application","weather advisory","harvest log","equipment rental request"],
    fields=["crop name","district","season"], unit="crop record", money=False),
"Telemedicine": dict(
    primary="patient", admin="clinic administrator",
    entities=["video consultation","symptom questionnaire","e-prescription","follow-up reminder","specialist referral","consultation note","health vital entry","medical certificate","consent record","chat transcript"],
    fields=["doctor name","specialisation","consultation date"], unit="consultation", money=True),
"Fitness Tracking": dict(
    primary="user", admin="administrator",
    entities=["workout session","calorie entry","step count record","fitness goal","body measurement","water intake log","training plan","progress photo","sleep record","achievement badge"],
    fields=["activity type","date","trainer name"], unit="workout session", money=False),
"Ticket Support Desk": dict(
    primary="requester", admin="support administrator",
    entities=["support ticket","ticket comment","attachment","escalation record","knowledge base article","service level agreement rule","assignment record","satisfaction survey","ticket tag","canned response"],
    fields=["ticket ID","status","priority"], unit="ticket", money=False),
"Examination System": dict(
    primary="candidate", admin="examination controller",
    entities=["exam registration","hall ticket","answer script","result record","revaluation request","question paper","seating allocation","malpractice report","mark sheet","exam timetable entry"],
    fields=["registration number","exam name","subject code"], unit="exam registration", money=True),
"Smart Home Control": dict(
    primary="resident", admin="system administrator",
    entities=["connected device","automation rule","energy usage record","security camera feed","door lock event","scene preset","sensor alert","guest access token","device group","firmware update record"],
    fields=["device name","room","device type"], unit="automation rule", money=False),
"Job Portal": dict(
    primary="job seeker", admin="portal administrator",
    entities=["job posting","application","resume","interview schedule","saved job","employer profile","skill tag","offer letter record","application status update","recruiter message"],
    fields=["job title","company","location"], unit="application", money=False),
"Parking Management": dict(
    primary="driver", admin="parking administrator",
    entities=["parking slot","slot booking","entry record","exit record","parking fee entry","vehicle registration record","violation notice","monthly pass","slot availability record","gate access log"],
    fields=["parking area","vehicle number","slot type"], unit="slot booking", money=True),
"Insurance Claims": dict(
    primary="policyholder", admin="claims administrator",
    entities=["policy record","claim request","supporting document","premium payment","claim status update","nominee detail","policy renewal request","surveyor report","settlement record","grievance entry"],
    fields=["policy number","claim type","claim date"], unit="claim", money=True),
"Municipal Grievance": dict(
    primary="citizen", admin="municipal officer",
    entities=["complaint","complaint photo","ward record","resolution update","property tax record","water connection request","trade licence application","birth certificate request","street light fault entry","garbage collection schedule"],
    fields=["complaint ID","ward number","complaint category"], unit="complaint", money=True),
"Video Streaming": dict(
    primary="subscriber", admin="content administrator",
    entities=["video title","watchlist entry","viewing history record","subscription plan","user profile","download entry","content rating","playback setting","recommendation entry","parental control rule"],
    fields=["title","genre","release year"], unit="subscription", money=True),
"Restaurant POS": dict(
    primary="cashier", admin="restaurant manager",
    entities=["table order","bill","menu item","kitchen ticket","split payment record","tip entry","shift record","daily sales entry","void transaction record","table reservation"],
    fields=["table number","order number","item name"], unit="bill", money=True),
"Courier Tracking": dict(
    primary="sender", admin="logistics administrator",
    entities=["shipment","pickup request","tracking event","delivery attempt record","proof of delivery","return shipment","route assignment","shipping label","weight discrepancy record","delivery exception"],
    fields=["tracking number","destination pin code","shipment date"], unit="shipment", money=True),
"Blood Bank": dict(
    primary="donor", admin="blood bank administrator",
    entities=["donation record","blood unit","donor eligibility record","blood request","camp registration","cross-match record","expiry disposal entry","donor health screening","issue record","stock level entry"],
    fields=["blood group","component type","collection date"], unit="blood request", money=False),
}

# ---------------- functional templates ----------------
CRUD = [
 ("The system shall allow {actor}s to create a new {e}.", "create"),
 ("The system shall allow {actor}s to view the details of a selected {e}.", "read"),
 ("The system shall allow {actor}s to update an existing {e}.", "update"),
 ("The system shall allow {actor}s to delete a {e} that is no longer required.", "delete"),
 ("The system shall allow {actor}s to search for a {e} by {f}.", "search"),
 ("The system shall allow {actor}s to filter the list of {e}s by status.", "search"),
 ("The system shall allow {actor}s to sort the list of {e}s by date of creation.", "search"),
 ("The system shall display a paginated list of {e}s with twenty entries per page.", "read"),
 ("The system shall allow {actor}s to export the list of {e}s as a CSV file.", "export"),
 ("The system shall allow {actor}s to download a {e} as a PDF document.", "export"),
 ("The system shall send an email notification to the {actor} when a {e} is created.", "notify"),
 ("The system shall send an SMS alert to the {actor} when the status of a {e} changes.", "notify"),
 ("The system shall record the date and time at which each {e} is modified.", "audit"),
 ("The system shall maintain an audit log of every change made to a {e}.", "audit"),
 ("The system shall allow {admin}s to approve a {e} submitted by a {actor}.", "workflow"),
 ("The system shall allow {admin}s to reject a {e} with a mandatory reason.", "workflow"),
 ("The system shall allow {admin}s to generate a monthly report of all {e}s.", "report"),
 ("The system shall allow {admin}s to view a dashboard summarising {e} counts by status.", "report"),
 ("The system shall prevent a {actor} from submitting a duplicate {e}.", "validation"),
 ("The system shall validate all mandatory fields of a {e} before saving it.", "validation"),
 ("The system shall allow {actor}s to attach a supporting document to a {e}.", "attachment"),
 ("The system shall restrict access to a {e} to the {actor} who created it.", "authorization"),
 ("The system shall allow {admin}s to archive a {e} older than one year.", "archival"),
 ("The system shall allow {actor}s to add a comment to a {e}.", "collaboration"),
 ("The system shall display the current status of each {e} on the {actor} dashboard.", "read"),
]

ACCOUNT = [
 ("The system shall allow users to register using an email address and a password.", "authentication"),
 ("The system shall allow users to register using a mobile number verified through a one-time password.", "authentication"),
 ("The system shall allow users to log in using valid credentials.", "authentication"),
 ("The system shall lock a user account after five consecutive failed login attempts.", "authentication"),
 ("The system shall allow users to reset a forgotten password through a secure email link.", "authentication"),
 ("The system shall allow users to enable two-factor authentication for their account.", "authentication"),
 ("The system shall allow users to update their profile information.", "profile"),
 ("The system shall allow users to upload a profile photograph of up to 2 MB.", "profile"),
 ("The system shall allow users to deactivate their own account.", "profile"),
 ("The system shall allow users to view their activity history for the last ninety days.", "profile"),
 ("The system shall allow {admin}s to assign roles and permissions to a user account.", "authorization"),
 ("The system shall log the user out automatically after fifteen minutes of inactivity.", "authentication"),
]

MONEY = [
 ("The system shall allow {actor}s to pay for a {unit} using a credit or debit card.", "payment"),
 ("The system shall allow {actor}s to pay for a {unit} using a UPI transaction.", "payment"),
 ("The system shall generate a printable invoice for every completed {unit}.", "payment"),
 ("The system shall allow {actor}s to request a refund for a cancelled {unit}.", "payment"),
 ("The system shall allow {admin}s to apply a discount to a {unit} before payment.", "payment"),
 ("The system shall display the total payable amount including taxes before payment is confirmed.", "payment"),
 ("The system shall allow {actor}s to view the payment history of all past {unit}s.", "payment"),
 ("The system shall mark a {unit} as failed if the payment gateway returns an error.", "payment"),
]

# vague / defective functional statements
VAGUE_F = [
 ("The system shall handle {e}s appropriately.", "ambiguous", ["appropriately"]),
 ("The system shall manage {e}s in an efficient manner.", "ambiguous", ["efficient manner"]),
 ("The system shall process a {e} as quickly as possible.", "ambiguous", ["as quickly as possible"]),
 ("The system should support various operations on {e}s as needed.", "ambiguous", ["various","as needed"]),
 ("The system shall provide adequate options for managing {e}s.", "ambiguous", ["adequate"]),
 ("The system shall display suitable information about each {e}.", "ambiguous", ["suitable"]),
 ("The system shall deal with invalid {e} data properly.", "ambiguous", ["properly"]),
 ("The system shall support most of the common actions on a {e}.", "ambiguous", ["most","common"]),
 ("The system shall provide appropriate error messages when something goes wrong with a {e}.", "ambiguous", ["appropriate","something goes wrong"]),
 ("The system shall be able to work with a reasonable number of {e}s.", "ambiguous", ["reasonable"]),
 ("The system shall allow {actor}s to do the usual things with their {e}s.", "ambiguous", ["usual things"]),
 ("The system shall handle {e} errors and other similar issues.", "ambiguous", ["other similar issues"]),
]

# near-duplicate pairs (same intent, different wording)
DUP_PAIRS = [
 ("The system shall allow {actor}s to save a {e} for later use.",
  "The system shall allow {actor}s to bookmark a {e} for future reference."),
 ("The system shall allow {actor}s to cancel a {e} before it is processed.",
  "The system shall allow {actor}s to withdraw a {e} prior to processing."),
 ("The system shall allow {actor}s to search for a {e} by {f}.",
  "The system shall provide a search facility that locates a {e} using {f}."),
 ("The system shall send a confirmation message once a {e} is submitted.",
  "The system shall notify the {actor} after a {e} has been submitted successfully."),
 ("The system shall allow {admin}s to remove a {e} from the system.",
  "The system shall allow {admin}s to delete an existing {e} record."),
 ("The system shall allow {actor}s to rate a completed {unit} from one to five stars.",
  "The system shall allow {actor}s to give a star rating between one and five for a finished {unit}."),
]

# ---------------- non-functional ----------------
NFR_CLEAR = [
 ("The system shall display any {e} search result within 2 seconds for 95 percent of requests.", "Performance"),
 ("The system shall support 5,000 concurrent users without response times exceeding 3 seconds.", "Scalability"),
 ("The system shall process at least 200 {unit} submissions per minute at peak load.", "Performance"),
 ("The system shall be available 99.9 percent of the time measured monthly, excluding scheduled maintenance.", "Availability"),
 ("The system shall store all user passwords using the bcrypt hashing algorithm with a work factor of at least 12.", "Security"),
 ("The system shall transmit all data over TLS 1.3 or higher.", "Security"),
 ("The system shall log every administrative action with user ID and timestamp and retain the log for 12 months.", "Security"),
 ("The system shall restore service within 30 minutes of a database failure using the latest hourly backup.", "Reliability"),
 ("The system shall take an automated backup of the {e} database every 6 hours.", "Reliability"),
 ("The system shall allow a new {actor} to complete a {unit} within 3 minutes without external assistance.", "Usability"),
 ("The system shall conform to WCAG 2.1 Level AA accessibility guidelines.", "Usability"),
 ("The system shall support the Chrome, Firefox, Edge, and Safari browsers in their two most recent major versions.", "Portability"),
 ("The system shall run on Android 10 and above and iOS 15 and above.", "Portability"),
 ("The system shall provide the user interface in English, Hindi, and Tamil.", "Usability"),
 ("The source code shall maintain a unit test coverage of at least 80 percent.", "Maintainability"),
 ("The system shall expose all {e} operations through a documented REST API.", "Interoperability"),
 ("The system shall retain {e} records for 7 years before permanent deletion.", "Compliance"),
 ("The system shall allow a {actor} to download all personal data held about them within 48 hours of request.", "Compliance"),
 ("The system shall mask all but the last four digits of any stored card number.", "Security"),
 ("The system shall recover and resume an interrupted {unit} submission within 10 seconds of reconnection.", "Reliability"),
]

NFR_VAGUE = [
 ("The system should be user-friendly and easy to use for all {actor}s.", "Usability", ["user-friendly","easy to use"]),
 ("The system shall be fast and responsive under normal conditions.", "Performance", ["fast","responsive","normal conditions"]),
 ("The system shall handle a reasonably large number of users efficiently.", "Scalability", ["reasonably large","efficiently"]),
 ("The system shall support a flexible and scalable architecture as needed.", "Scalability", ["flexible","as needed"]),
 ("The system shall be secure and protect {actor} data appropriately.", "Security", ["secure","appropriately"]),
 ("The system shall be highly reliable at all times.", "Reliability", ["highly reliable","all times"]),
 ("The system shall be maintainable and easy to modify in the future.", "Maintainability", ["maintainable","easy to modify"]),
 ("The system shall have a modern and attractive user interface.", "Usability", ["modern","attractive"]),
 ("The system shall minimise downtime as far as possible.", "Availability", ["as far as possible"]),
 ("The system shall use industry standard security practices.", "Security", ["industry standard"]),
 ("The system shall work well on most devices.", "Portability", ["work well","most devices"]),
 ("The system shall load {e} pages quickly.", "Performance", ["quickly"]),
 ("The system shall be sufficiently robust for real world usage.", "Reliability", ["sufficiently robust","real world usage"]),
 ("The system shall scale up easily when the user base grows.", "Scalability", ["easily"]),
 ("The system shall provide good performance during peak hours.", "Performance", ["good performance"]),
]

VAGUE_WORDS = ["appropriate","appropriately","efficient","efficiently","quickly","fast","user-friendly",
 "easy","reasonable","reasonably","adequate","suitable","properly","as needed","flexible","various",
 "most","common","usual","modern","attractive","good","robust","highly","industry standard","normal conditions",
 "as far as possible","as quickly as possible","something goes wrong","other similar issues","all times","easily","work well"]

rows = []
rid = 0

def add(domain, text, rtype, cat, quality, dup_group="", notes=""):
    global rid
    if text in seen: return False
    seen.add(text)
    rid += 1
    amb = [w for w in VAGUE_WORDS if w in text.lower()]
    rows.append(dict(
        req_id=f"REQ-{rid:05d}",
        domain=domain,
        requirement_text=text,
        requirement_type=rtype,                 # Functional / Non-Functional
        category=cat,                           # sub-category
        quality_label=quality,                  # well-formed / ambiguous / duplicate
        is_ambiguous=int(quality == "ambiguous"),
        is_duplicate=int(quality == "duplicate"),
        duplicate_group=dup_group,
        is_testable=int(quality == "well-formed"),
        ambiguous_terms="|".join(sorted(set(amb))),
        word_count=len(text.split()),
        notes=notes))
    return True

seen = set()
TARGET_PER_DOMAIN = 100

for dname, d in DOMAINS.items():
    actor, admin, ents, fields = d["primary"], d["admin"], d["entities"], d["fields"]
    unit = d["unit"]
    def fill(t, e="", f=""):
        return t.format(actor=actor, admin=admin, e=e, f=f, unit=unit)
    count = 0

    # 1. account / auth requirements (well-formed)
    for t, c in ACCOUNT:
        if count >= 12: break
        if add(dname, fill(t), "Functional", c, "well-formed"): count += 1

    # 2. payment/money requirements
    if d["money"]:
        for t, c in MONEY:
            if count >= 20: break
            if add(dname, fill(t), "Functional", c, "well-formed"): count += 1

    # 3. CRUD-style functional requirements across entities
    combos = [(t, e) for e in ents for t in CRUD]
    random.shuffle(combos)
    for (t, c), e in combos:
        if count >= 60: break
        f = random.choice(fields)
        if add(dname, fill(t[0] if isinstance(t, tuple) else t, e, f), "Functional", c, "well-formed"):
            count += 1
    # (guard: CRUD items are tuples)
    for tpl in CRUD:
        if count >= 62: break
        t, c = tpl
        e = random.choice(ents); f = random.choice(fields)
        if add(dname, fill(t, e, f), "Functional", c, "well-formed"): count += 1

    # 4. duplicate pairs
    dup_idx = 0
    for a, b in DUP_PAIRS:
        if count >= 74: break
        e = random.choice(ents); f = random.choice(fields)
        ta, tb = fill(a, e, f), fill(b, e, f)
        if ta in seen or tb in seen: continue
        dup_idx += 1
        g = f"{dname[:3].upper()}-DUP-{dup_idx}"
        add(dname, ta, "Functional", "duplicate-pair", "well-formed", g, "original of a near-duplicate pair"); count += 1
        add(dname, tb, "Functional", "duplicate-pair", "duplicate", g, "restates the requirement above"); count += 1

    # 5. vague functional
    for t, q, terms in VAGUE_F:
        if count >= 84: break
        e = random.choice(ents)
        if add(dname, fill(t, e), "Functional", "under-specified", "ambiguous"): count += 1

    # 6. clear NFRs
    random.shuffle(NFR_CLEAR)
    for t, c in NFR_CLEAR:
        if count >= 94: break
        e = random.choice(ents)
        if add(dname, fill(t, e), "Non-Functional", c, "well-formed"): count += 1

    # 7. vague NFRs
    for t, c, terms in NFR_VAGUE:
        if count >= TARGET_PER_DOMAIN: break
        e = random.choice(ents)
        if add(dname, fill(t, e), "Non-Functional", c, "ambiguous"): count += 1

    # top-up with more CRUD combos if short
    while count < TARGET_PER_DOMAIN:
        t, c = random.choice(CRUD)
        e = random.choice(ents); f = random.choice(fields)
        if add(dname, fill(t, e, f), "Functional", c, "well-formed"): count += 1

print("total rows:", len(rows))

# ---------------- write outputs ----------------
cols = list(rows[0].keys())
with open("/mnt/user-data/outputs/srs_requirements_3000.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)

with open("/mnt/user-data/outputs/srs_requirements_3000.jsonl", "w", encoding="utf-8") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")

# stats
from collections import Counter
print("domains:", len(Counter(r["domain"] for r in rows)))
print(Counter(r["requirement_type"] for r in rows))
print(Counter(r["quality_label"] for r in rows))
print(Counter(r["category"] for r in rows).most_common(10))
