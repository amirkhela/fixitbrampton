#!/usr/bin/env python3
"""
fixitbrampton.ca content generator.
Produces /services/<service>-<area>.html for all 10 services x 10 areas = 100 pages.

Existing hand-written pages in /services/ are NOT overwritten.
Sitemap is regenerated from the final URL list.
State is tracked in scripts/content_state.json for the /loop.
"""

import json
import os
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent.parent
SERVICES_DIR = ROOT / "services"
STATE_FILE = Path(__file__).resolve().parent / "content_state.json"
SITEMAP = ROOT / "sitemap.xml"

# Hand-crafted existing pages — don't touch
PROTECTED = {
    "tv-mounting-brampton",
    "furniture-assembly-brampton",
    "drywall-painting-brampton",
    "deck-fence-repair-brampton",
}

SERVICES = {
    "tv-mounting": {
        "name": "TV Mounting",
        "pa": "ਟੀਵੀ ਮਾਊਂਟਿੰਗ",
        "short_verb": "mount a TV",
        "hero_adjective": "levelled to the millimetre",
        "price_from": 130, "price_to": 220, "price_hint": "bracket included",
        "intro": "Any TV size on any wall — drywall, brick, concrete, or tile backsplash. Stud-anchored or masonry-anchored, cables tucked into the wall, angle set for your couch height, and the room vacuumed before we leave.",
        "included": [
            "Stud-finder scan + marking; anchored into structural studs or masonry (never drywall only)",
            "Universal fixed, tilting, or full-motion bracket included if you need one",
            "Cable management: in-wall fishing with a Code-compliant power kit, or paintable raceway",
            "Soundbar mounted below the TV (if supplied), HDMI/ARC tested",
            "Levelled with a digital level, angle tuned for seating height",
            "Old mount removed and drywall holes patched flush if it's a replacement",
            "Cardboard, plastic, and drywall dust cleaned up and taken away",
            "7-day call-back guarantee — if anything loosens, we come back free",
        ],
        "faqs": [
            ("How much does it cost to mount a TV?", "Standard wall mounting is $130 for TVs up to 55 inches, $160 for 56–75 inch, and $200–220 for 76 inches and up. Cable hiding inside the wall adds $40–60 depending on drywall conditions. Bracket included."),
            ("Can you mount on brick or concrete?", "Yes — we bring masonry drill bits and anchors rated well above your TV's weight. Brick and concrete actually hold heavier TVs more securely than drywall."),
            ("Can you hide the cables in the wall?", "On standard drywall, yes — we install a Code-compliant in-wall power kit and fish the HDMI through. On exterior walls with horizontal blocking we use a paintable surface raceway."),
        ],
        "related": ["furniture-assembly", "drywall-painting", "shelving-closets"],
    },
    "furniture-assembly": {
        "name": "Furniture Assembly",
        "pa": "ਫਰਨੀਚਰ ਅਸੈਂਬਲੀ",
        "short_verb": "assemble furniture",
        "hero_adjective": "every screw in its place",
        "price_from": 75, "price_to": 280, "price_hint": "per-piece flat; anti-tip free",
        "intro": "IKEA with 28 wordless steps. Wayfair boxes with mystery hardware. Amazon dressers with half the screws. We do this every day — built, wall-anchored, and boxes to the curb in less time than it'd take you to figure out which way is up.",
        "included": [
            "Full build per manufacturer instructions — every dowel, cam lock, and connector seated right",
            "Drawers aligned so they don't catch; doors hung so they don't sag",
            "Anti-tip strap anchored into a stud for dressers, bookcases, wardrobes — free",
            "Missing/damaged parts flagged with photo docs you can send the retailer",
            "Boxes flattened, plastic bagged, curbside-ready — or hauled away for a small fee",
            "Furniture moved to final position in the room",
            "Drop cloths on the floor; any scratches we cause are on us",
            "7-day call-back — if a panel squeaks or a drawer misaligns, we come back free",
        ],
        "faqs": [
            ("How much does furniture assembly cost?", "Small pieces (nightstands, small desks, a PAX wardrobe with 2 doors) start at $75. Dressers, queen beds, and bookcases run $120–160. Full bedroom sets or large PAX closets come in at $180–280."),
            ("Will you anchor furniture to the wall?", "Yes — free, always. Tall dressers and bookcases get an anti-tip strap drilled into a stud. IKEA ships the strap for a reason, and we put it in."),
            ("Can you take the cardboard away?", "Flattened to your curb, yes — included if recycling day is within 3 days. If not, we haul for $25–40."),
        ],
        "related": ["tv-mounting", "shelving-closets", "drywall-painting"],
    },
    "drywall-painting": {
        "name": "Drywall Repair & Painting",
        "pa": "ਡਰਾਈਵਾਲ ਅਤੇ ਪੇਂਟਿੰਗ",
        "short_verb": "patch drywall or paint",
        "hero_adjective": "patches that actually disappear",
        "price_from": 85, "price_to": 800, "price_hint": "patch bundle; room repaint from $450",
        "intro": "The doorknob hole in the guest room. The stress cracks above the window. The ghost of a patch your last painter left. We sand flush, float the compound properly, feather the edges, colour-match the paint, and leave the room cleaner than we found it.",
        "included": [
            "Nail holes, screw holes, anchor holes — filled, sanded, primed, painted",
            "Doorknob holes repaired with a proper patch (not just mud — that cracks in a year)",
            "Fist-to-furniture-sized holes: mesh or California patch, three-coat mudding, feathered sanding",
            "Hairline settling cracks reinforced with paper tape, compound, primer, paint",
            "Popcorn ceiling patches matched with texture spray",
            "Paint colour-matched from your can or scan-matched at the store",
            "Full interior rooms rolled with premium Benjamin Moore or Sherwin-Williams",
            "Vacuum-assisted sanding, drop cloths, shop-vac cleanup — zero dust tracked through the house",
        ],
        "faqs": [
            ("How much does drywall repair cost?", "Small patches (nail/picture holes) bundled start at $85 for up to five. A fist-size hole with paint runs $120–160. Larger patches $180–280. Full room repaint from $450."),
            ("Can you match my existing paint?", "If you have the can, we use it. If not, we scan-match a chip at the paint store. On modern latex, the match is indistinguishable once dry."),
            ("Do you control the dust?", "Yes — drop cloths, plastic sheeting over furniture, vacuum-assisted sander on big patches, shop-vac before leaving."),
        ],
        "related": ["general-repairs", "tv-mounting", "caulking-weatherproofing"],
    },
    "deck-fence-repair": {
        "name": "Deck & Fence Repair",
        "pa": "ਡੈੱਕ ਅਤੇ ਵਾੜ ਮੁਰੰਮਤ",
        "short_verb": "repair a deck or fence",
        "hero_adjective": "before winter does worse",
        "price_from": 120, "price_to": 1200, "price_hint": "per-board; full re-stain from $450",
        "intro": "The soft spot by the BBQ. The fence panel the wind pushed sideways. The gate that drags. The deck that needs stain before another winter turns it silver. We repair, reset, sand, seal — pressure-treated lumber, proper concrete, two coats of quality stain.",
        "included": [
            "Loose or soft deck boards pulled, joists inspected, replaced with matching pressure-treated",
            "Railings tightened, wobbly posts sistered, loose balusters re-anchored",
            "Stair tread replacement — matched width, proper rise, screwed not nailed",
            "Fence post resets with fresh concrete, plumbed and braced 24 hours",
            "Individual fence panel and picket replacement with pressure-treated cedar or spruce",
            "Gate re-hanging: hinges straightened, droppers added, latch re-aligned",
            "Deck sanding, power-washing, two-coat staining with Olympic Maximum or Behr Premium",
            "All waste hauled — no rotten wood or concrete chunks left on the lawn",
        ],
        "faqs": [
            ("How much does deck repair cost?", "Single loose board $120–180. Stair tread $160 each. Railing re-secure $150. Soft-spot repair (3–5 boards) $280–450. Full re-stain from $450."),
            ("Can you reset a leaning fence post?", "Yes — rotten posts get sistered or replaced; wind-shifted posts get re-plumbed, braced, and concrete-set. Flat $240 per post including lumber and concrete."),
            ("When is the best time to stain a deck?", "Late spring through early fall — above 10°C, no rain 48 hours either side. In the GTA that's May through October."),
        ],
        "related": ["general-repairs", "caulking-weatherproofing", "door-window-repair"],
    },
    "plumbing-minor": {
        "name": "Minor Plumbing",
        "pa": "ਛੋਟੀ ਪਲੰਬਿੰਗ",
        "short_verb": "fix a leak or faucet",
        "hero_adjective": "no more drip, drip, drip",
        "price_from": 95, "price_to": 350, "price_hint": "parts often extra at cost",
        "intro": "Dripping taps that wake you up. Toilets that run all night and double the water bill. Shower heads from the 90s. Drain snaking when the kitchen sink won't clear. If it's bigger than a seal or cartridge we'll say so up front — but most household plumbing is smaller than you'd expect.",
        "included": [
            "Dripping faucets rebuilt with new cartridge, O-rings, or washers",
            "Running toilets fixed — flapper, fill valve, flush valve replacements",
            "Shower head and hose replacement, including hidden shut-off valves",
            "P-trap replacement, sink clogs snaked, garburator reset or replacement",
            "Angle-stop (shut-off valve) replacement under sinks and toilets",
            "Washing machine hose swap to braided stainless — cheap insurance against flooding",
            "Outdoor hose bib winter prep and spring re-connection",
            "Photo-documented before/after; we leave under-sink cabinets cleaner than we found them",
        ],
        "faqs": [
            ("Are you a licensed plumber?", "For the basics we handle — faucets, cartridges, flappers, traps — a license isn't required in Ontario. For anything that needs behind-the-wall work, we refer you to a licensed plumber. We won't guess."),
            ("How much does a faucet fix cost?", "A standard cartridge rebuild is $95–140 including the cartridge. Full faucet swap $160–220 plus the new faucet. Running toilet rebuild $120–160."),
            ("Can you clear a drain?", "Kitchen sinks and bathroom traps — yes, we snake and clean. Main line/sewer backups need a dedicated drain company with a 100-foot cable."),
        ],
        "related": ["general-repairs", "caulking-weatherproofing", "drywall-painting"],
    },
    "electrical-minor": {
        "name": "Minor Electrical",
        "pa": "ਛੋਟੀ ਬਿਜਲੀ",
        "short_verb": "install a fixture or switch",
        "hero_adjective": "ESA-friendly minor electrical",
        "price_from": 95, "price_to": 280, "price_hint": "fixture extra",
        "intro": "Light fixtures that never got installed after the drywall went up. Ceiling fans that wobble. Dimmers that hum. Smart switches that half your neighbours already have. We handle the fixture-swap and device-level work that doesn't touch the panel — and tell you honestly when a licensed electrician is the right call.",
        "included": [
            "Light fixture replacement — flush mount, pendant, chandelier, vanity, exterior",
            "Ceiling fan installation or replacement, with proper fan-rated boxes where required",
            "Dimmer switch installation (LED-compatible) and 3-way/4-way configurations",
            "Smart switch and smart bulb setup — Kasa, Lutron, Philips Hue, Nest",
            "Outlet cover plates replaced, loose outlets secured",
            "Under-cabinet lighting install with tidy cable routing",
            "Doorbell replacement — wired or smart (Ring, Nest)",
            "We stay within the ESA homeowner-permissible scope; anything beyond goes to a licensed electrician",
        ],
        "faqs": [
            ("Can you replace a breaker or work in the panel?", "No — panel work, new circuits, and service upgrades need a licensed electrician and an ESA permit. We stick to device-level work that's permissible without a license."),
            ("How much does it cost to install a light fixture?", "A standard flush mount or pendant swap is $95–140. Chandeliers and fixtures requiring a two-person lift run $160–220. Ceiling fans $180–280 including box replacement if needed."),
            ("Will you install a smart switch?", "Yes — we install and set up the device with your phone. A neutral wire is needed for most smart switches; we check first and tell you if your box has one."),
        ],
        "related": ["general-repairs", "shelving-closets", "tv-mounting"],
    },
    "door-window-repair": {
        "name": "Door & Window Repair",
        "pa": "ਦਰਵਾਜ਼ੇ ਅਤੇ ਖਿੜਕੀ ਮੁਰੰਮਤ",
        "short_verb": "fix a door or window",
        "hero_adjective": "doors that latch, windows that seal",
        "price_from": 95, "price_to": 400, "price_hint": "hardware extra at cost",
        "intro": "Doors that don't latch anymore, handles that turn loose in your hand, screens with a hockey-puck-sized hole, windows whistling in the winter. All of these are handyman-level fixes — no need for a window company if the glass is fine.",
        "included": [
            "Sticking interior doors planed and re-hinged to latch cleanly",
            "Door handles, deadbolts, and hinges replaced; smart locks installed (Schlage, Yale, August)",
            "Weather stripping replacement on entry doors and patio doors",
            "Sliding door rollers adjusted or replaced; tracks cleaned",
            "Screen re-meshing on window and patio door screens",
            "Window sash balance replacement; sash locks re-secured",
            "Garage entry door thresholds re-seated to stop drafts",
            "Closer arms installed or tuned so screen doors don't slam",
        ],
        "faqs": [
            ("Can you install a new entry door?", "Full exterior door replacement with a new frame is a 2-person, half-day job — we do it, but quote on-site. Swapping an existing door into existing hinges/hardware is a same-visit job."),
            ("How much does it cost to fix a sticking door?", "Plane, rehang, and adjust a single interior door runs $95–140. If the jamb has shifted and needs shimming, $160–220."),
            ("Do you re-mesh screens?", "Yes — window and patio door screens, including pet-resistant mesh. Per-screen price $45–85 depending on size."),
        ],
        "related": ["caulking-weatherproofing", "general-repairs", "drywall-painting"],
    },
    "shelving-closets": {
        "name": "Shelving & Closets",
        "pa": "ਸ਼ੈਲਵਿੰਗ ਅਤੇ ਅਲਮਾਰੀਆਂ",
        "short_verb": "install shelving or closets",
        "hero_adjective": "level, square, anchored to studs",
        "price_from": 95, "price_to": 480, "price_hint": "materials extra at cost",
        "intro": "Floating shelves that actually hold what you put on them. Pantry systems that don't sag after a month. Closet organizers built to the wall, not resting on the carpet. Garage wall storage that turns chaos into a grid. All anchored into studs, all levelled, all square.",
        "included": [
            "Floating shelves — concealed bracket, stud-anchored, load-rated",
            "ClosetMaid, ClosetMate, Rubbermaid Elfa and IKEA PAX interior systems",
            "Custom cleat shelving in garages and mudrooms",
            "Pantry wire and melamine systems installed plumb and level",
            "Kids' room organizers with toddler-safe anchoring",
            "Pegboard walls for garages and workshops",
            "Under-stair storage custom-built where possible",
            "Every hole measured twice, every anchor rated to load, every shelf bubble-level checked",
        ],
        "faqs": [
            ("Can you do a full PAX closet?", "Yes — from flat-pack through install and anchoring. Pricing depends on the number of frames and doors; 2-frame basic $240, 4-frame with doors $380–480."),
            ("Will the shelves actually hold weight?", "Yes — we anchor into studs, not drywall anchors, for anything over 10 lbs. A 36-inch floating shelf anchored properly holds 80+ lbs evenly loaded."),
            ("Can you build custom shelving?", "Simple cleat and plywood built-ins, yes. Full-cabinetry style built-ins (with face frames and doors) is carpenter work — we refer out."),
        ],
        "related": ["furniture-assembly", "general-repairs", "tv-mounting"],
    },
    "caulking-weatherproofing": {
        "name": "Caulking & Weatherproofing",
        "pa": "ਕੌਲਕਿੰਗ ਅਤੇ ਮੌਸਮ-ਰੋਧ",
        "short_verb": "re-caulk or weatherproof",
        "hero_adjective": "your furnace isn't heating the street",
        "price_from": 120, "price_to": 340, "price_hint": "materials included",
        "intro": "That yellowing caulk around the tub that's peeling at the edges. The draft whistling under the front door every January. The window sash that leaks when it rains sideways. These are the unglamorous fixes that quietly save you hundreds in heat and water damage — which is why they're easy to put off, and why we do them.",
        "included": [
            "Old caulk cut out and cleaned; surface primed; new silicone or latex bead pulled smooth",
            "Bathtub and shower surround re-caulked — mildew-resistant sanitary silicone",
            "Kitchen sink, backsplash, and countertop re-seal",
            "Exterior window frames sealed at the trim-to-brick line",
            "Door thresholds, sweeps, and weather stripping replaced",
            "Attic hatch weather stripping — a huge silent heat leak most people miss",
            "Baseboard to floor caulk touch-up where the gaps show",
            "All surfaces left painter-ready or finish-ready; no grey smears on the tile",
        ],
        "faqs": [
            ("How much does re-caulking cost?", "Single bathtub/shower surround $140–180. Kitchen sink and backsplash $95–130. Window and door weatherproofing $120–200 per door/window pair."),
            ("Why does caulk fail so fast?", "Usually wrong product. Bathroom needs 100% silicone, not latex. Exterior uses urethane or polyurethane, not silicone. We use the right product for the job."),
            ("Can you do exterior caulking too?", "Yes — window frames, door trim, dryer vents. Done in dry weather above 5°C so it cures properly."),
        ],
        "related": ["door-window-repair", "drywall-painting", "general-repairs"],
    },
    "general-repairs": {
        "name": "General Home Repairs",
        "pa": "ਆਮ ਘਰ ਮੁਰੰਮਤ",
        "short_verb": "handle the small stuff",
        "hero_adjective": "the list you keep meaning to get to",
        "price_from": 85, "price_to": 280, "price_hint": "per-visit, multi-job discount",
        "intro": "The hinge that squeaks at 2am. The railing that wobbles every time you go up the stairs. The curtain rod that pulled out of the wall. The cabinet door that won't close flush. All of these get flagged by your brain every day — this is the visit where you clear the list.",
        "included": [
            "Door hinges squeaking or loose — adjusted, lubed, or replaced",
            "Wobbly railings and stair balusters re-secured into studs",
            "Curtain rod re-anchoring with toggle bolts or stud screws",
            "Cabinet hinges re-shimmed; doors aligned; soft-close dampers added if supplied",
            "Squeaky stair treads screwed from underneath when accessible",
            "Towel bar and toilet paper holder remounting when the drywall anchor pulled out",
            "Childproofing — cabinet latches, corner guards, outlet covers",
            "The best per-visit pricing when you batch 3+ small jobs — way cheaper than per-trip visits",
        ],
        "faqs": [
            ("Can I batch a bunch of small jobs?", "Yes — this is the most efficient way to use us. A 2-hour visit at $180 can knock out 8–10 small items that would've cost $400+ as separate service calls elsewhere."),
            ("How small is too small to call?", "Not a thing. If it's been bothering you for months and will take 15 minutes to fix, that's a perfect include on a batched visit."),
            ("Do you charge a minimum?", "$85 minimum for a visit — so we only come for a single 20-minute job if you're fine with that. Most people save it for 3-4 items."),
        ],
        "related": ["door-window-repair", "drywall-painting", "shelving-closets"],
    },
}

AREAS = {
    "brampton": {
        "display": "Brampton",
        "pa": "ਬਰੈਂਪਟਨ",
        "type": "city",
        "parent": None,
        "postal_codes": ["L6P", "L6R", "L6S", "L6T", "L6V", "L6W", "L6X", "L6Y", "L6Z", "L7A"],
        "housing": "a mix of 1970s bungalows, 1990s two-storey detached, and newer townhouse blocks",
        "landmarks": "Bramalea City Centre, Gage Park, the downtown arts block on Main Street",
        "drive_notes": "we live and work out of Brampton — every job is local",
        "hook": "from the Bramalea bungalows we grew up in to the new Springdale detached blocks",
    },
    "springdale": {
        "display": "Springdale",
        "pa": "ਸਪ੍ਰਿੰਗਡੇਲ",
        "type": "neighbourhood",
        "parent": "Brampton",
        "postal_codes": ["L6R", "L6P"],
        "housing": "detached and linked-detached homes built between the late 1990s and mid-2010s; lots of freehold townhouse blocks",
        "landmarks": "Trinity Common Mall, Sandalwood Parkway, Bramalea Road North",
        "drive_notes": "10–15 minutes from central Brampton — we pass through it most weeks",
        "hook": "the freehold townhouse blocks off Sandalwood and the detached homes south of Mayfield",
    },
    "castlemore": {
        "display": "Castlemore",
        "pa": "ਕੈਸਲਮੋਰ",
        "type": "neighbourhood",
        "parent": "Brampton",
        "postal_codes": ["L6P"],
        "housing": "larger detached homes and executive estates — many 3,000+ sq ft with finished basements and extensive decks",
        "landmarks": "The Gore Road corridor, Castlemore Road, Claireville Conservation Area",
        "drive_notes": "15–20 minutes from the centre of Brampton; we service this area several times a month",
        "hook": "the executive homes along The Gore Road and Castlemore Road",
    },
    "mount-pleasant": {
        "display": "Mount Pleasant",
        "pa": "ਮਾਊਂਟ ਪਲੈਜ਼ੈਂਟ",
        "type": "neighbourhood",
        "parent": "Brampton",
        "postal_codes": ["L7A", "L6X"],
        "housing": "newer detached and townhouse subdivisions built from 2005 onward around the GO station and village core",
        "landmarks": "Mount Pleasant GO Station, the village square, Creditview Road",
        "drive_notes": "20 minutes from east Brampton; we're there weekly for TV mounts and IKEA furniture in the newer homes",
        "hook": "the GO-station village blocks and the newer Creditview Road townhouses",
    },
    "heart-lake": {
        "display": "Heart Lake",
        "pa": "ਹਾਰਟ ਲੇਕ",
        "type": "neighbourhood",
        "parent": "Brampton",
        "postal_codes": ["L6Z"],
        "housing": "established 1980s and 1990s detached homes and bungalows, many with mature trees and original decks",
        "landmarks": "Heart Lake Conservation Area, Sandalwood and Kennedy, Heart Lake Town Centre",
        "drive_notes": "10 minutes from central Brampton — Heart Lake is one of our most-called areas for deck repair",
        "hook": "the 80s–90s detached homes around Sandalwood and Kennedy",
    },
    "bramalea": {
        "display": "Bramalea",
        "pa": "ਬ੍ਰਾਮਾਲੀਆ",
        "type": "neighbourhood",
        "parent": "Brampton",
        "postal_codes": ["L6S", "L6T"],
        "housing": "the original planned subdivision of Brampton — 1960s–80s bungalows and side-splits that still make up the bones of east Brampton",
        "landmarks": "Bramalea City Centre, Chinguacousy Park, Bramalea Road",
        "drive_notes": "5–10 minutes from our home base — we're in Bramalea almost daily",
        "hook": "the original 60s–80s bungalows and side-splits of Canada's first master-planned community",
    },
    "fletchers-meadow": {
        "display": "Fletcher's Meadow",
        "pa": "ਫਲੈਚਰਜ਼ ਮੈਡੋ",
        "type": "neighbourhood",
        "parent": "Brampton",
        "postal_codes": ["L7A"],
        "housing": "newer detached and semi-detached homes, mostly built in the 2000s, with modern electrical and still-young decks",
        "landmarks": "Chinguacousy Road, Fletcher's Creek, Cassie Campbell Community Centre",
        "drive_notes": "15–20 minutes from east Brampton — we come west for Fletcher's Meadow regularly",
        "hook": "the 2000s-era detached and semi blocks around Chinguacousy and Wanless",
    },
    "mississauga": {
        "display": "Mississauga",
        "pa": "ਮਿਸੀਸਾਗਾ",
        "type": "city",
        "parent": None,
        "postal_codes": ["L4W", "L4X", "L4Y", "L4Z", "L5A", "L5B", "L5C", "L5E", "L5M", "L5N", "L5R", "L5V", "L5W"],
        "housing": "everything from Streetsville's historic main street homes to the highrise condos near Square One to the detached blocks in Meadowvale and Erin Mills",
        "landmarks": "Square One, Streetsville, Port Credit, Meadowvale",
        "drive_notes": "20–30 minutes from Brampton depending on where — we're in Mississauga two or three times a week",
        "hook": "detached blocks in Meadowvale, Erin Mills and Streetsville",
    },
    "caledon": {
        "display": "Caledon",
        "pa": "ਕੈਲੇਡਨ",
        "type": "city",
        "parent": None,
        "postal_codes": ["L7C", "L7E", "L7K"],
        "housing": "rural-edge larger lots, estate homes, and small-town pockets — bigger decks, long driveways, and the odd century home that needs careful hands",
        "landmarks": "Caledon Village, Belfountain, the Forks of the Credit",
        "drive_notes": "30–40 minutes from Brampton — we budget for the drive and quote accordingly",
        "hook": "the estate homes off Mayfield and the small-town pockets of Caledon Village",
    },
    "bolton-georgetown": {
        "display": "Bolton / Georgetown",
        "pa": "ਬੋਲਟਨ / ਜਾਰਜਟਾਊਨ",
        "type": "region",
        "parent": None,
        "postal_codes": ["L7E", "L7G"],
        "housing": "small-town Ontario feel — older downtowns with Victorian and century homes on one end, newer suburban blocks on the other",
        "landmarks": "downtown Bolton, historic main street Georgetown, Highway 10 corridor",
        "drive_notes": "35–45 minutes from Brampton — we combine jobs in this area for efficiency",
        "hook": "the century homes of downtown Georgetown and the Bolton subdivisions off King",
    },
}


HEADER = '''  <div class="prestrip" role="note" aria-label="Punjabi service available">
    <span class="gurmukhi">ਸਤ ਸ੍ਰੀ ਅਕਾਲ</span>
    <span class="sep">·</span>
    Punjabi &amp; English Spoken
    <span class="sep">·</span>
    <span class="gurmukhi">ਪੰਜਾਬੀ ਵਿੱਚ ਸੇਵਾ ਉਪਲਬਧ</span>
  </div>

  <header class="header">
    <div class="container header-inner">
      <a href="/" class="brand" aria-label="Fix It Brampton home">
        <svg class="brand-mark" viewBox="0 0 64 64" aria-hidden="true">
          <rect width="64" height="64" rx="14" fill="#C97B2E"/>
          <path d="M18 44 L32 30 L30 28 Q27 25 28 22 Q29 18 33 17 Q37 16 40 19 Q44 23 41 28 Q39 31 35 31 L33 33 L46 46" stroke="#FDFAF4" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
          <circle cx="50" cy="14" r="4" fill="#7A1F2D"/>
        </svg>
        <span class="brand-name">
          <span class="en">Fix It Brampton</span>
          <span class="pa">ਬਰੈਂਪਟਨ ਦਾ ਭਰੋਸੇਯੋਗ ਹੈਂਡੀਮੈਨ</span>
        </span>
      </a>
      <nav class="header-nav" aria-label="Primary">
        <a href="sms:2892753973" class="header-phone">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
          (289) 275-3973
        </a>
        <a href="https://wa.me/12892753973" class="wa-icon-link" aria-label="Chat on WhatsApp" target="_blank" rel="noopener">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.71.306 1.263.489 1.695.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
        </a>
      </nav>
    </div>
  </header>'''

FOOTER = '''  <footer class="footer">
    <div class="container">
      <div class="footer-inner">
        <div class="footer-brand">
          <span class="brand-name"><span class="en">Fix It Brampton</span></span>
          <p>Brampton's honest, Punjabi-speaking handyman. Small and medium jobs, flat-rate quotes, done right the first time.</p>
        </div>
        <div>
          <h4>Top Services</h4>
          <ul>
            <li><a href="/services/furniture-assembly-brampton">Furniture Assembly</a></li>
            <li><a href="/services/tv-mounting-brampton">TV Mounting</a></li>
            <li><a href="/services/drywall-painting-brampton">Drywall &amp; Painting</a></li>
            <li><a href="/services/deck-fence-repair-brampton">Deck &amp; Fence Repair</a></li>
          </ul>
        </div>
        <div>
          <h4>Service Area</h4>
          <ul>
            <li><a href="/#area">Brampton</a></li>
            <li><a href="/#area">Mississauga</a></li>
            <li><a href="/#area">Caledon</a></li>
            <li><a href="/#area">Bolton / Georgetown</a></li>
          </ul>
        </div>
        <div>
          <h4>Contact</h4>
          <ul>
            <li><a href="sms:2892753973">(289) 275-3973</a></li>
            <li>Mon–Sun · 8am–6pm</li>
            <li><a href="/#faq">FAQ</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; <span id="footerYear">2026</span> Fix It Brampton · Brampton, Ontario, Canada</p>
        <p class="pa">ਬਰੈਂਪਟਨ ਦਾ ਆਪਣਾ ਹੈਂਡੀਮੈਨ</p>
      </div>
    </div>
  </footer>

  <div class="floating-cta" aria-hidden="false">
    <a href="sms:2892753973" class="fc-text" aria-label="Text us">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
      Text Now
    </a>
    <a href="https://wa.me/12892753973" class="fc-wa" aria-label="WhatsApp" target="_blank" rel="noopener">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.71.306 1.263.489 1.695.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347"/></svg>
      WhatsApp
    </a>
  </div>

  <script src="/script.js"></script>
</body>
</html>'''


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def page_title(svc_name, area):
    parent = area["parent"]
    if parent:
        return f"{svc_name} in {area['display']} ({parent}) | Punjabi-Speaking · Fix It Brampton"
    return f"{svc_name} in {area['display']} | Punjabi-Speaking · Fix It Brampton"


def area_label(area):
    if area["parent"]:
        return f"{area['display']}, {area['parent']}"
    return area["display"]


def build_html(svc_slug, svc, area_slug, area):
    slug = f"{svc_slug}-{area_slug}"
    url = f"https://fixitbrampton.ca/services/{slug}"
    title = page_title(svc["name"], area)
    meta_desc = f"{svc['name']} in {area_label(area)}. From ${svc['price_from']}. Flat quotes, Punjabi & English spoken, same-day text replies. {svc['intro'][:120]}"
    schema_service = {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": svc["name"],
        "name": f"{svc['name']} in {area_label(area)}",
        "description": f"{svc['name']} in {area_label(area)} by Fix It Brampton. {svc['intro']}",
        "provider": {"@id": "https://fixitbrampton.ca/#business"},
        "areaServed": {"@type": "Place", "name": area_label(area)},
        "offers": {
            "@type": "Offer",
            "priceCurrency": "CAD",
            "priceSpecification": {
                "@type": "PriceSpecification",
                "minPrice": str(svc["price_from"]),
                "maxPrice": str(svc["price_to"]),
                "priceCurrency": "CAD",
            },
        },
    }
    schema_breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://fixitbrampton.ca/"},
            {"@type": "ListItem", "position": 2, "name": "Services", "item": "https://fixitbrampton.ca/#services"},
            {"@type": "ListItem", "position": 3, "name": f"{svc['name']} in {area_label(area)}", "item": url},
        ],
    }
    # Area-specific FAQ
    area_faq_q = f"Do you service {area['display']}?"
    if area["parent"]:
        area_faq_a = (
            f"Yes — {area['display']} in {area['parent']} is one of our regular service areas. "
            f"{area['drive_notes'].capitalize()}. Postal codes we cover here include {', '.join(area['postal_codes'])}. "
            f"Common streets: {area['landmarks']}."
        )
    else:
        area_faq_a = (
            f"Yes — {area['display']} is one of our regular service areas. "
            f"{area['drive_notes'].capitalize()}. Postal codes we cover here include {', '.join(area['postal_codes'])}. "
            f"Landmarks nearby: {area['landmarks']}."
        )
    faq_entries = list(svc["faqs"]) + [(area_faq_q, area_faq_a)]
    schema_faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faq_entries
        ],
    }

    included_html = "\n            ".join(f"<li>{esc(i)}</li>" for i in svc["included"])
    faq_html_parts = []
    for q, a in faq_entries:
        faq_html_parts.append(
            f'''          <details class="faq-item">
            <summary>{esc(q)}</summary>
            <div class="answer">
              <p>{esc(a)}</p>
            </div>
          </details>'''
        )
    faq_html = "\n".join(faq_html_parts)

    related_html_parts = []
    for r in svc["related"]:
        rsvc = SERVICES[r]
        rurl = f"/services/{r}-{area_slug}"
        related_html_parts.append(
            f'''          <a class="service-card" href="{rurl}">
            <h3>{esc(rsvc["name"])} in {esc(area["display"])}</h3>
            <p>From ${rsvc["price_from"]}. {esc(rsvc["intro"][:110])}…</p>
          </a>'''
        )
    related_html = "\n".join(related_html_parts)

    hero_pa_subtitle = f"{area['pa']} ਵਿੱਚ {svc['pa']} — ਪੰਜਾਬੀ ਬੋਲਣ ਵਾਲਾ ਹੈਂਡੀਮੈਨ"

    area_description_paragraph = (
        f"Working in {area['display']} means we know {area['housing']}. "
        f"Most calls here come from {area['hook']} — so when you text us, "
        f"we already have a sense of what your walls, decks, and doors are like before we arrive."
    )

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="theme-color" content="#C97B2E">

  <title>{esc(title)}</title>
  <meta name="description" content="{esc(meta_desc)}">
  <meta name="keywords" content="{svc_slug.replace('-', ' ')} {area['display'].lower()}, {svc['name'].lower()} {area['display'].lower()}, punjabi handyman {area['display'].lower()}, handyman {area['display'].lower()}, fix it brampton {area['display'].lower()}">
  <link rel="canonical" href="{url}">

  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="mask-icon" href="/favicon.svg" color="#C97B2E">
  <link rel="apple-touch-icon" href="/favicon.svg">

  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(meta_desc)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{url}">
  <meta property="og:locale" content="en_CA">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght,SOFT@0,9..144,400..700,0..100;1,9..144,400..700,0..100&family=Manrope:wght@400;500;600;700&family=Noto+Sans+Gurmukhi:wght@400;500;600;700&family=Noto+Serif+Gurmukhi:wght@500;600;700&display=swap">

  <link rel="stylesheet" href="/style.css">

  <script type="application/ld+json">{json.dumps(schema_service)}</script>
  <script type="application/ld+json">{json.dumps(schema_breadcrumb)}</script>
  <script type="application/ld+json">{json.dumps(schema_faq)}</script>
</head>
<body>

{HEADER}

  <nav class="breadcrumb" aria-label="Breadcrumb">
    <div class="container">
      <ol>
        <li><a href="/">Home</a></li>
        <li><a href="/#services">Services</a></li>
        <li aria-current="page">{esc(svc["name"])} in {esc(area_label(area))}</li>
      </ol>
    </div>
  </nav>

  <main>

    <section class="service-hero">
      <div class="container">
        <h1>{esc(svc["name"])} in {esc(area["display"])} — <em>{esc(svc["hero_adjective"])}.</em></h1>
        <p class="service-pa-subtitle">{hero_pa_subtitle}</p>
        <p class="service-lede">{esc(svc["intro"])}</p>
        <p class="service-lede">{esc(area_description_paragraph)}</p>
        <div class="service-price-chip">
          <strong>From ${svc["price_from"]}</strong>
          <span>· {esc(svc["price_hint"])}</span>
        </div>
        <div class="service-actions">
          <a href="sms:2892753973?&amp;body=Hi%20Fix%20It%20Brampton%2C%20I%20need%20{svc_slug.replace('-', '%20')}%20in%20{area['display'].replace(' ', '%20').replace('/', '%2F')}.%20Photo%20attached." class="btn btn-primary">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            Text (289) 275-3973
          </a>
          <a href="https://wa.me/12892753973?text=Hi%20Fix%20It%20Brampton%2C%20{svc['name'].replace(' ', '%20')}%20in%20{area['display'].replace(' ', '%20').replace('/', '%2F')}%3F" class="btn btn-whatsapp" target="_blank" rel="noopener">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.71.306 1.263.489 1.695.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347"/></svg>
            WhatsApp
          </a>
        </div>
      </div>
    </section>

    <section class="included section-alt">
      <div class="container">
        <span class="section-eyebrow">What's Included</span>
        <h2 class="section-title">Flat price, <em>nothing skipped.</em></h2>
        <p class="section-lede">This is what every {esc(svc["name"])} job in {esc(area["display"])} covers. Extra materials (if any) come at cost with a photo of the receipt.</p>
        <div class="included-layout">
          <ul class="included-list">
            {included_html}
          </ul>
          <aside class="included-aside">
            <h3>Text a photo</h3>
            <p>Send a picture of the job and your {area["display"]} postal code. We'll text back a flat quote and the next available slot.</p>
            <p><a href="sms:2892753973" style="color: var(--amber-soft); font-weight:700;">(289) 275-3973</a></p>
            <span class="pa">{area["pa"]} ਵਿੱਚ ਸੇਵਾ ਉਪਲਬਧ।</span>
          </aside>
        </div>
      </div>
    </section>

    <section class="process">
      <div class="container">
        <span class="section-eyebrow">How It Works</span>
        <h2 class="section-title">Four steps. <em>No runaround.</em></h2>
        <div class="process-grid">
          <div class="process-step">
            <span class="step-num" aria-hidden="true"></span>
            <h3>Text a photo</h3>
            <p>Photo of the work and your {esc(area["display"])} postal code.</p>
            <span class="pa-caption">ਫੋਟੋ ਅਤੇ ਪਤਾ।</span>
          </div>
          <div class="process-step">
            <span class="step-num" aria-hidden="true"></span>
            <h3>Flat quote</h3>
            <p>Same-day reply with one fixed price. No hourly clock.</p>
            <span class="pa-caption">ਇੱਕ ਕੀਮਤ।</span>
          </div>
          <div class="process-step">
            <span class="step-num" aria-hidden="true"></span>
            <h3>Pick a time</h3>
            <p>Same-week slots including evenings and weekends.</p>
            <span class="pa-caption">ਸਮਾਂ ਤੁਹਾਡਾ।</span>
          </div>
          <div class="process-step">
            <span class="step-num" aria-hidden="true"></span>
            <h3>Done &amp; cleaned</h3>
            <p>Work shown, tested, and the room vacuumed before we leave.</p>
            <span class="pa-caption">ਸਾਫ਼ ਮੁਕੰਮਲ।</span>
          </div>
        </div>
      </div>
    </section>

    <section class="faq section-alt">
      <div class="container">
        <span class="section-eyebrow">{esc(svc["name"])} FAQ · {esc(area["display"])}</span>
        <h2 class="section-title">Before you <em>text.</em></h2>
        <div class="faq-list">
{faq_html}
        </div>
      </div>
    </section>

    <section class="related">
      <div class="container">
        <span class="section-eyebrow">Related in {esc(area["display"])}</span>
        <h2 class="section-title">While we're <em>in the neighbourhood</em>.</h2>
        <div class="related-grid">
{related_html}
        </div>
      </div>
    </section>

    <section class="cta-strip">
      <div class="container">
        <h2>{esc(svc["name"])} in {esc(area["display"])} — <em>flat quote today.</em></h2>
        <p>Text a photo, get a fixed price, book the next open slot. Same-day reply 8am–6pm.</p>
        <a href="sms:2892753973" class="btn btn-primary">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          Text (289) 275-3973
        </a>
        <p class="pa">ਸਾਡੇ ਨਾਲ ਪੰਜਾਬੀ ਵਿੱਚ ਗੱਲ ਕਰੋ</p>
      </div>
    </section>

  </main>

{FOOTER}
'''
    return html


def regenerate_sitemap(all_slugs):
    today = date.today().isoformat()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">',
        '  <url>',
        '    <loc>https://fixitbrampton.ca/</loc>',
        f'    <lastmod>{today}</lastmod>',
        '    <changefreq>weekly</changefreq>',
        '    <priority>1.0</priority>',
        '    <xhtml:link rel="alternate" hreflang="en-CA" href="https://fixitbrampton.ca/"/>',
        '    <xhtml:link rel="alternate" hreflang="pa" href="https://fixitbrampton.ca/"/>',
        '    <xhtml:link rel="alternate" hreflang="x-default" href="https://fixitbrampton.ca/"/>',
        '  </url>',
    ]
    # Service pages
    for slug in sorted(all_slugs):
        lines += [
            '  <url>',
            f'    <loc>https://fixitbrampton.ca/services/{slug}</loc>',
            f'    <lastmod>{today}</lastmod>',
            '    <changefreq>monthly</changefreq>',
            '    <priority>0.8</priority>',
            '  </url>',
        ]
    for anchor in ("services", "why", "process", "about", "area", "faq", "contact"):
        lines += [
            '  <url>',
            f'    <loc>https://fixitbrampton.ca/#{anchor}</loc>',
            f'    <lastmod>{today}</lastmod>',
            '    <changefreq>monthly</changefreq>',
            '    <priority>0.6</priority>',
            '  </url>',
        ]
    lines.append('</urlset>')
    SITEMAP.write_text("\n".join(lines), encoding="utf-8")


def main():
    SERVICES_DIR.mkdir(exist_ok=True)
    generated = []
    skipped = []
    all_slugs = set(PROTECTED)
    for svc_slug, svc in SERVICES.items():
        for area_slug, area in AREAS.items():
            slug = f"{svc_slug}-{area_slug}"
            all_slugs.add(slug)
            out = SERVICES_DIR / f"{slug}.html"
            if slug in PROTECTED:
                skipped.append(slug)
                continue
            html = build_html(svc_slug, svc, area_slug, area)
            out.write_text(html, encoding="utf-8")
            generated.append(slug)
    # state
    state = {
        "generated": sorted(generated),
        "protected": sorted(PROTECTED),
        "total_matrix": len(SERVICES) * len(AREAS),
        "last_run": date.today().isoformat(),
    }
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    regenerate_sitemap(all_slugs)
    print(f"Generated {len(generated)} pages (matrix = {len(SERVICES) * len(AREAS)}, protected = {len(PROTECTED)})")
    print(f"Sitemap: {len(all_slugs)} service URLs + 1 home + 7 anchors")


if __name__ == "__main__":
    main()
