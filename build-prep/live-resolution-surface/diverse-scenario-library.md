# Live Intent Resolution Surface

## Diverse Scenario Library: The System in Motion

The point of these scenarios is not just “here are possible uses.” The point is to show the **temporal behaviour** of the system: how it starts with almost nothing, makes the unclear idea visible, narrows the artifact space, loads schemas, generates surfaces, captures reactions, closes decisions, and eventually produces a thing.

Across these examples, the same underlying engine works for different users, different artifact types, different levels of clarity, and different final outputs.

The repeated pattern is:

```text
half-thought
→ first anchors
→ generated possibilities
→ user reaction
→ tags / counts / observations
→ artifact candidates
→ schema activation
→ generative UI surfaces
→ missing information map
→ decision closure
→ handoff package
→ downstream generation / build / launch
→ memory retained
```

---

# Scenario 1

## From “I keep losing track of requests” to a deployed production web app

### User

A community workshop coordinator.

They are not technical. They do not ask for an app. They do not have a product spec. They just know a recurring operational pain.

---

## T0 — Half-thought input

The user starts with:

> “People keep messaging me about broken stuff, pickups, tools, and repair jobs. It all comes through texts and Facebook and random calls. I keep losing things. I don’t know, there should be some way to make it not suck.”

At this point, the user has not asked for software.

The possible artifact space includes:

* checklist
* spreadsheet
* workflow
* shared inbox
* CRM
* repair ticket system
* web app
* automation
* volunteer coordination tool
* public request form
* internal dashboard
* community operations process

The system should not immediately say:

> “I’ll build you a repair ticket web app.”

That would collapse too early.

---

## T1 — First anchor extraction

The system extracts anchors:

```text
who:
- people in the community
- workshop coordinator
- possibly volunteers or repairers

what:
- broken items
- pickups
- tools
- repair jobs
- incoming messages

where / channels:
- texts
- Facebook
- phone calls

problem:
- requests are scattered
- things are getting lost

emotional signal:
- frustration
- overload

artifact uncertainty:
- high

possible domains:
- workflow
- operations
- request tracking
- community service
- lightweight software
```

Initial tags:

```text
messy_incoming_requests: +1
multi_channel_input: +1
needs_tracking: +1
user_overloaded: +1
possible_workflow_system: +1
possible_web_app: +1
possible_intake_form: +1
possible_dashboard: +1
```

---

## T2 — First live surface render

The screen does not show a form.

It shows a generated surface titled:

## “This might be a way to stop requests disappearing.”

The surface contains five possibility cards:

```text
A. Shared Request Board
A simple internal board where every request becomes a card.

B. Public Request Form + Admin Dashboard
People submit requests through one link. You manage them in one place.

C. Volunteer Dispatch Workflow
Requests are sorted and assigned to volunteers automatically.

D. Lightweight CRM
People, jobs, items, history, and follow-ups all linked together.

E. Message Capture System
Keep using text/Facebook/calls, but forward everything into one triage inbox.
```

The system asks:

> “Which of these feels closest to the thing you wish existed? You can also say ‘not that’ or ‘a mix.’”

The user replies:

> “B maybe, but not too fancy. People shouldn’t need accounts. I just need to stop losing jobs and know who is doing what.”

---

## T3 — Reaction capture

The system records:

```text
prefers_public_intake: +1
rejects_user_accounts: +1
needs_internal_tracking: +1
needs_assignment_visibility: +1
low_complexity_preference: +1
```

Structured observation:

> The user does not primarily want a community platform. They want a lightweight request intake and tracking system that reduces operational loss.

Artifact candidates update:

```text
Public request form               active
Internal admin board               foreground
Full community portal              rejected
Volunteer assignment workflow      active
CRM                                dormant
Message capture system             supporting
```

The live surface updates.

A branch map appears:

```text
Repair Request System
├── Public side
│   └── simple submit request form
├── Internal side
│   ├── triage board
│   ├── assign person
│   └── track status
├── Notifications
│   ├── request received
│   ├── status changed
│   └── assigned volunteer
└── Later possibilities
    ├── Facebook/message capture
    ├── map of pickups
    └── volunteer portal
```

---

## T4 — Schema activation

The system activates multiple schemas:

```text
primary schemas:
- lightweight web application
- request intake workflow
- admin dashboard
- status tracking system

supporting schemas:
- notification workflow
- role / permission schema
- data model schema
- deployment handoff schema
```

Each schema brings missing fields.

The missing information map appears:

```text
Still needed to make this buildable:

Request types             unknown
Required request fields   partial
Statuses                  unknown
Admin roles               partial
Assignment logic          unknown
Notification method       open
Data privacy needs        open
Launch deadline           unknown
Hosting preference        assumed simple
```

Instead of asking the user to fill a long product form, the system generates targeted surfaces.

---

## T5 — Generated UI surface: request lifecycle

The system shows a request lifecycle card set:

```text
Choose the closest lifecycle:

A. New → Reviewed → Assigned → In Progress → Done

B. New → Needs Info → Accepted → Scheduled → Completed

C. New → Triage → Waiting for Dropoff → Repairing → Ready for Pickup

D. New → Urgent / Normal / Later → Assigned → Closed
```

The user says:

> “C is right for repairs, but some are pickups. Maybe there are two types.”

System update:

```text
request_type_split: +1
repair_lifecycle_selected: +1
pickup_lifecycle_needed: +1
```

Decision ledger entry:

```text
Decision:
Requests should have types, at minimum Repair and Pickup.

Reason:
User identified different lifecycles for repair jobs and pickup jobs.

Effect:
Data model requires request_type.
Status options may depend on request_type.
```

---

## T6 — Schema composition

The artifact is no longer just “web app.”

It becomes a composed artifact:

```text
Primary artifact:
- Lightweight web application

Functional sub-artifacts:
- public request intake form
- internal triage board
- request detail view
- assignment workflow
- status lifecycle
- notification system

Operational sub-artifacts:
- repair process
- pickup process
- volunteer assignment process
```

The system now shows a generated app structure:

```text
Public Screens:
1. Submit a request
2. Request received confirmation

Admin Screens:
1. Dashboard
2. Request detail
3. Assignment view
4. Status board
5. Settings

Data Objects:
- Request
- Person
- Item
- Assignment
- Status event
- Note
```

The user can click into any area.

They click “Submit a request.”

---

## T7 — Request form surface

The system generates three versions of the public form.

```text
Version A — Minimal
Name, contact, request type, description, photo.

Version B — Practical
Name, contact, request type, item category, description, location/pickup details, photos.

Version C — Detailed
Everything in B plus preferred times, urgency, safety notes, consent, estimated item size.
```

The user says:

> “B, but urgency too. And photos would be great but optional.”

Tags:

```text
prefers_practical_detail: +1
optional_photo_upload: +1
needs_urgency_field: +1
rejects_overly_detailed_form: +1
```

Decision:

```text
Public request form should use practical detail level, not minimal and not exhaustive.
```

Known fields update:

```text
Request:
- requester_name
- contact_method
- contact_value
- request_type
- item_category
- description
- location_or_pickup_details
- urgency
- photos_optional
```

---

## T8 — Internal worker activity behind the scenes

The user only sees a clean evolving surface, but internally the fan-out/fan-in architecture is running.

Local workers process the latest interaction:

```text
anchor_extractor:
- request type split detected
- urgency field added

tagger:
- practical_detail_preference
- optional_media
- rejects_overcomplication

schema_matcher:
- request intake schema foreground
- admin dashboard schema active
- notification schema supporting

missing_field_detector:
- status list still unresolved
- admin roles unresolved
- assignment rules unresolved
- notification channel unresolved

option_generator:
- generate status options
- generate role options
- generate dashboard layout options

decision_detector:
- practical request form accepted
- full portal rejected for v1

surface_recommender:
- next useful surface: admin board layout
```

The arbiter decides:

> Do not ask for hosting or technology yet. The user is still defining the operational model. Show admin board options next.

---

## T9 — Admin board surface

The system shows three dashboard models:

```text
A. Kanban Board
Columns for status: New, Waiting, Repairing, Ready, Complete.

B. List + Filters
A searchable list with status, urgency, request type, assigned person.

C. Daily Triage View
Today’s new requests, urgent items, and unassigned jobs.
```

The user says:

> “A with filters from B. I want to drag things between statuses.”

Decision:

```text
Admin dashboard should be a kanban-style board with filters.
```

Schema dependencies update:

```text
Drag-and-drop board requires:
- status model
- status transition rules
- permission rules
- request update history
```

The system opens a status model panel.

---

## T10 — Decision closure

The system begins closing required decisions.

Some are user-decided:

```text
Request types:
- Repair
- Pickup

Form complexity:
- practical detail

Dashboard:
- kanban board with filters

Accounts:
- no public accounts
- admin login required
```

Some are assumed visibly:

```text
Assumption:
Use email notifications for v1 instead of SMS, because email is easier and lower cost.

Status:
working assumption

User control:
accept / edit / reject
```

The user says:

> “Email is fine for v1.”

Decision ledger updates:

```text
Decision:
Use email notifications for v1.

Reason:
Simpler and accepted by user.

Effect:
SMS integration postponed.
```

Some are delegated:

```text
Technology stack:
User delegates to system.

Decision:
Use a standard hosted web app architecture with managed database, authentication for admins, file storage for optional photos, and simple deployment.

Reason:
User has no stack preference and wants a working hosted system.
```

---

## T11 — Execution readiness map

The system shows:

```text
Execution readiness:

Artifact type             ready
Public request form        ready
Admin dashboard            ready
Data model                 partial
Permissions                partial
Notifications              ready enough
Deployment target          assumed
Visual style               open
Acceptance criteria        forming
```

The system proactively says:

> “The weakest part is now the data model and permissions. I can generate a sensible v1 model and keep assumptions visible.”

User selects:

> Autopilot with visible assumptions.

---

## T12 — Spec compilation

The system compiles the handoff package.

```text
Project:
Community Repair Request Tracker

Artifact type:
Production web application

Primary users:
- community members submitting requests
- workshop coordinator managing requests
- volunteers assigned to jobs

Core workflows:
1. Submit request
2. Review request
3. Assign request
4. Update status
5. Notify requester
6. Complete or archive request

Public requirements:
- no account required
- simple form
- optional photos
- confirmation message
- email confirmation if provided

Admin requirements:
- admin login
- kanban board
- filters by request type, urgency, status, assigned person
- drag status changes
- request detail view
- internal notes
- assignment field
- status history

Data objects:
- Request
- Requester
- Assignment
- StatusEvent
- Note
- PhotoAttachment
- AdminUser

Assumptions:
- email notifications only for v1
- no public account system
- no payment system
- no map view in v1
- SMS and Facebook capture are future features

Acceptance criteria:
- a community member can submit a request without logging in
- an admin can see the request in the dashboard
- an admin can assign a volunteer
- an admin can change status by dragging the card
- status changes are recorded
- requester receives notification when request is received and completed
- optional photo upload works
- private admin notes are not visible publicly
```

---

## T13 — Downstream build workflow

The handoff package is passed to downstream execution agents.

The system launches subworkflows:

```text
Design workflow:
- generate screen wireframes
- create component hierarchy
- define responsive layout
- produce visual style options

Code workflow:
- scaffold app
- implement database schema
- implement public request form
- implement admin authentication
- implement dashboard
- implement status updates
- implement email notifications

Test workflow:
- generate test cases from acceptance criteria
- run form submission test
- run admin status update test
- run photo upload test
- run notification test

Deployment workflow:
- provision hosted database
- configure storage
- configure authentication
- configure environment variables
- deploy web app
- run smoke tests
```

The user sees a workflow monitor:

```text
Design                complete
Database schema        complete
Public form            complete
Admin board            building
Notifications          building
Tests                  pending
Deployment             pending
```

---

## T14 — Final output

The system produces:

```text
Live hosted web app:
- public request submission URL
- admin dashboard URL
- admin credentials setup flow
- deployment notes
- v1 user guide
- future feature backlog
```

It also creates:

```text
Documentation:
- product brief
- technical summary
- data model
- admin guide
- acceptance test results
- launch checklist
```

---

## T15 — Memory retained

The system stores:

```text
User-level memory:
- prefers simple practical systems over full platforms
- accepts autopilot for technical decisions
- prefers visible assumptions
- likely values low-maintenance tools

Project memory:
- full community portal rejected for v1
- public accounts rejected
- email accepted for v1
- SMS / Facebook capture future
- kanban board selected
```

Next time this user says:

> “I’ve got another messy community thing…”

The system starts with useful memory instead of zero.

---

# Scenario 2

## From “my students just don’t get it” to an interactive lesson pack, teacher guide, and classroom activity

### User

A high school science teacher.

They do not know whether they need slides, a worksheet, a game, an animation, or a lesson plan.

---

## T0 — Half-thought input

User:

> “My students just don’t get energy transfer. They can repeat definitions but they don’t understand it. I need something better for next week.”

Possible artifact space:

* lesson plan
* slides
* worksheet
* simulation
* physical classroom activity
* quiz
* explainer video
* interactive web module
* teacher guide
* assessment rubric
* analogy set
* lab activity

---

## T1 — Anchor extraction

```text
who:
- students
- teacher

when:
- next week

topic:
- energy transfer

problem:
- memorisation without understanding

desired outcome:
- conceptual understanding

artifact type:
- unresolved

possible domains:
- education
- explanation
- interactive learning
- assessment
```

Tags:

```text
teaching_context: +1
conceptual_understanding_needed: +1
deadline_next_week: +1
possible_lesson_plan: +1
possible_interactive_activity: +1
possible_assessment: +1
```

---

## T2 — First generated surface

The system displays:

```text
This could become:

A. A visual explanation sequence
B. A hands-on classroom activity
C. An interactive simulation
D. A misconception-based quiz
E. A complete lesson pack
```

User says:

> “Probably E, but I want something they can do, not just watch.”

Tags:

```text
prefers_complete_pack: +1
needs_student_activity: +1
rejects_passive_content: +1
```

Observation:

> The user needs a teachable package, but the core artifact should be active learning rather than static explanation.

---

## T3 — Artifact composition

```text
Primary artifact:
- active learning lesson pack

Supporting artifacts:
- teacher guide
- student activity
- visual explanation
- misconception quiz
- reflection worksheet
```

Active schemas:

```text
- lesson plan schema
- classroom activity schema
- concept explanation schema
- assessment schema
- worksheet schema
```

Missing map:

```text
Student year level       unknown
Class duration           unknown
Available materials      unknown
Curriculum standard      optional
Class size               unknown
Assessment need          open
Technology availability  unknown
```

---

## T4 — Proactive surface: learning mode options

Instead of asking for a lesson plan, the system shows:

```text
Which learning experience feels closest?

A. Physical demonstration
Students pass objects/energy tokens through a system.

B. Interactive simulation
Students adjust variables and see energy flow.

C. Mystery investigation
Students explain where energy went in a scenario.

D. Build-and-test challenge
Students create a model and test predictions.
```

User:

> “C and D. They like solving things.”

Tags:

```text
prefers_inquiry_learning: +1
prefers_challenge_based_activity: +1
students_like_problem_solving: +1
```

Decision:

```text
Lesson should use inquiry/challenge format, not lecture-first format.
```

---

## T5 — Schema rendering

The UI changes into a lesson design surface:

```text
Lesson Pack
├── Hook
├── Challenge
├── Group task
├── Teacher prompts
├── Misconception checks
├── Explanation bridge
├── Exit ticket
└── Extension
```

The system generates a preview:

```text
Working concept:
"The Missing Energy Case"

Students investigate several everyday scenarios where energy appears to disappear:
- a ball stops rolling
- a phone heats while charging
- a lamp warms a room
- a bouncing ball loses height

They must explain where the energy went using evidence cards.
```

User:

> “That’s good. Make it less childish. Year 10.”

Tags:

```text
year_level_10: +1
tone_less_childish: +1
accepts_mystery_structure: +1
```

---

## T6 — Decision ledger

```text
Decision:
Use an investigation/challenge structure called "The Missing Energy Case."

Reason:
User selected inquiry/challenge modes and responded positively to the generated concept.

Decision:
Target Year 10 students.

Reason:
User specified Year 10.

Decision:
Tone should be mature enough for teenagers, not childish.

Reason:
User explicitly corrected tone.
```

---

## T7 — Missing fields resolved by options

The system shows material options:

```text
Available material level?

A. No materials, paper only
B. Basic classroom materials
C. Devices available
D. Lab equipment available
```

User selects:

> “Basic classroom materials, some devices but not guaranteed.”

The system assumes:

```text
No required individual device access.
Printable activity must work offline.
Optional digital simulation can be extension only.
```

User accepts.

---

## T8 — Handoff package

The compiled output:

```text
Artifact:
Year 10 active learning lesson pack

Topic:
Energy transfer and transformation

Core learning problem:
Students memorise definitions but do not understand where energy goes in real systems.

Learning experience:
Inquiry challenge / investigation

Components:
- teacher guide
- student evidence cards
- group activity worksheet
- misconception check
- visual explanation
- exit ticket
- optional extension simulation prompt

Constraints:
- usable next week
- basic classroom materials only
- no required individual devices
- not childish
- active, not passive

Success criteria:
- students explain energy transfer in everyday examples
- students distinguish energy transfer from energy disappearance
- students use evidence rather than definitions only
```

---

## T9 — Downstream generation

Downstream workflows produce:

```text
Teacher guide
Student worksheet
Evidence card set
Slide deck
Exit ticket
Optional digital simulation prompt
Printable PDF bundle
```

The live surface shows previews. The teacher rejects one illustration as too cartoonish. The system updates the style.

Memory retained:

```text
User teaches Year 10.
Prefers active learning.
Dislikes childish tone.
Often needs next-week practical materials.
```

---

# Scenario 3

## From “this policy rollout will be a mess” to a communication plan, workshop, FAQ, and internal workflow

### User

A mid-level operations manager in a company.

They are responsible for rolling out a new internal policy but do not know what deliverables they need.

---

## T0 — Half-thought input

User:

> “We have this new hybrid work policy and I already know people are going to misunderstand it. Leadership thinks sending a PDF is enough. It is absolutely not.”

Possible outputs:

* policy summary
* FAQ
* announcement email
* manager talking points
* workshop
* intranet page
* decision tree
* approval workflow
* training session
* change management plan
* feedback survey
* compliance checklist

---

## T1 — First anchors

```text
topic:
- hybrid work policy

stakeholders:
- employees
- leadership
- managers

problem:
- misunderstanding expected
- PDF insufficient

goal:
- successful rollout
- clarity
- adoption

artifact uncertainty:
- high

possible domains:
- communication
- change management
- policy
- training
- workflow
```

Tags:

```text
policy_rollout: +1
change_management: +1
rejects_static_pdf: +1
needs_clarity: +1
multiple_stakeholders: +1
```

---

## T2 — Possibility cards

The system shows:

```text
This is probably not one artifact. It may be a rollout package.

Possible components:

A. Plain-language policy summary
B. Employee FAQ
C. Manager conversation guide
D. Decision tree for edge cases
E. Launch email sequence
F. Feedback and issue capture workflow
G. Short live workshop
```

User:

> “Yes, package. The decision tree is important. Managers will get hammered with edge cases.”

Tags:

```text
artifact_package: +1
decision_tree_important: +1
manager_enablement_needed: +1
edge_cases_expected: +1
```

---

## T3 — Artifact composition

```text
Primary artifact:
- policy rollout package

Supporting artifacts:
- plain-language summary
- manager guide
- decision tree
- FAQ
- email sequence
- feedback workflow
- workshop outline
```

Schemas active:

```text
- change management schema
- internal communication schema
- policy explanation schema
- decision artifact schema
- workshop schema
- FAQ schema
```

---

## T4 — Live surface changes

The interface becomes a rollout map:

```text
Hybrid Work Rollout
├── Audience groups
│   ├── employees
│   ├── managers
│   └── leadership
├── Information artifacts
│   ├── summary
│   ├── FAQ
│   └── intranet page
├── Decision artifacts
│   └── manager decision tree
├── Communication sequence
│   ├── announcement
│   ├── reminder
│   └── follow-up
└── Feedback loop
    ├── question intake
    ├── unresolved cases
    └── policy clarification updates
```

The user clicks “decision tree.”

---

## T5 — Generated decision tree options

The system generates:

```text
Decision tree could be structured by:

A. Employee situation
Remote, hybrid, office-based, exception request.

B. Manager decision
Approve, escalate, deny, clarify.

C. Policy clause
Eligibility, days, locations, equipment, exceptions.

D. Common edge cases
Childcare, travel, illness, interstate work, performance concerns.
```

User:

> “D first. That’s how people will actually ask.”

Decision:

```text
Decision tree should begin from common real-world edge cases, not policy clauses.
```

Observation:

> The rollout should be designed around how employees ask questions, not how the policy is written.

That observation affects every generated artifact.

---

## T6 — Missing map

```text
Still needed:

Policy source text          missing
Common edge cases           forming
Tone                        open
Leadership position         unknown
Escalation rules            unknown
Approval authority          unknown
Launch date                 unknown
Feedback channel            open
```

The system asks through modes:

```text
How should I proceed?

[Paste policy]
Use exact source text.

[Generate placeholders]
Create structure now and fill policy details later.

[Interview me]
Ask for known rules.

[Autopilot]
Assume a standard hybrid policy and mark assumptions.
```

User chooses:

> “Generate placeholders. I’ll paste policy later.”

The system proceeds without blocking.

---

## T7 — Outputs generated

The system produces a placeholder rollout kit:

```text
1. Plain-language summary template
2. Manager decision tree skeleton
3. Employee FAQ structure
4. Launch email draft
5. Manager briefing agenda
6. Feedback intake form
7. Unresolved case escalation workflow
```

Assumptions are visible:

```text
Assumptions:
- policy includes eligibility rules
- manager approval is required for exceptions
- HR handles escalations
- launch happens within 2–4 weeks
```

The user can later replace assumptions with real policy text.

---

## T8 — Final handoff

This does not become a web app. It becomes a coordinated rollout system.

The handoff package includes:

```text
Artifact composition:
- communication package
- decision artifact
- workshop artifact
- feedback workflow

Audience:
- employees
- managers
- leadership

Design rule:
Organise around real employee questions, not policy sections.

Success criteria:
- managers can answer common cases
- employees understand core rules
- unclear cases are captured and escalated
- policy updates can be reflected in FAQ
```

Memory retained:

```text
User is operations-focused.
User distrusts static PDF rollouts.
User values edge cases and manager enablement.
```

---

# Scenario 4

## From “I want an art thing that feels like memory leaking” to a multimedia installation, grant pitch, and exhibition plan

### User

An artist.

They do not want business language. They are not asking for a “project plan.” They have a feeling and some imagery.

---

## T0 — Half-thought input

User:

> “I keep thinking about memory leaking out of rooms. Like, not ghosts exactly, but places remembering people badly. I want to make something with that, maybe for a small gallery.”

Possible artifact space:

* poem
* short film
* installation
* audio experience
* visual artwork
* interactive room
* exhibition concept
* grant application
* artist statement
* projection piece
* performance
* physical sculpture
* soundscape

---

## T1 — Anchor extraction

```text
theme:
- memory
- rooms
- places remembering people
- leakage
- absence

negative boundary:
- not exactly ghosts

possible setting:
- small gallery

possible artifact:
- unresolved, likely art/media/installation

emotional tone:
- haunting
- intimate
- decayed
- ambiguous
```

Tags:

```text
artistic_intent: +1
memory_theme: +1
spatial_metaphor: +1
not_literal_ghosts: +1
possible_installation: +1
possible_audio_visual: +1
```

---

## T2 — The system does not over-formalise

A bad system would say:

> “Please define target audience and success metrics.”

This system instead shows a mood/medium surface:

```text
This could become:

A. Sound installation
Rooms whisper fragments that never complete.

B. Projection piece
Walls slowly reveal and lose traces of past occupants.

C. Walkthrough installation
Visitors move through stations where memories distort.

D. Short film
A room changes as it misremembers someone.

E. Written / visual series
Fragments of rooms, objects, and false memories.
```

User:

> “C, but with B. I want people to move through it. And it should not explain itself too much.”

Tags:

```text
prefers_installation: +1
prefers_projection: +1
visitor_movement_required: +1
rejects_overexplanation: +1
```

---

## T3 — Artifact composition

```text
Primary artifact:
- gallery installation

Supporting artifacts:
- projection design
- soundscape
- spatial visitor path
- artist statement
- grant/exhibition pitch
- technical requirements
```

Schemas active:

```text
- installation art schema
- spatial experience schema
- projection media schema
- soundscape schema
- exhibition proposal schema
```

---

## T4 — Live surface rendering

The UI becomes a spatial concept board:

```text
Installation Concept
├── Visitor path
├── Rooms / zones
├── Memory behaviours
├── Sound
├── Projection
├── Materials
├── Technical setup
├── Artist statement
└── Gallery proposal
```

The system generates “memory behaviour” options:

```text
A. Memory fades when approached
B. Memory appears only in peripheral vision
C. Memory repeats incorrectly
D. Memory attaches to objects
E. Memory leaks between rooms
```

User:

> “C and E. Repeating incorrectly is good.”

Observation:

> The work is about distortion rather than haunting. The system should avoid literal ghost imagery.

Decision ledger:

```text
Decision:
The installation should focus on misremembering and leakage, not supernatural haunting.

Reason:
User explicitly rejected "ghosts" and accepted distortion/repetition motifs.
```

---

## T5 — Missing information map

```text
Still unresolved:

Gallery size               unknown
Number of zones            open
Budget                     unknown
Available equipment        unknown
Projection method          open
Sound setup                open
Audience flow              forming
Duration per visitor       open
Artist statement tone      forming
```

The system offers progress modes:

```text
[Concept first]
Develop the artistic language.

[Gallery proposal]
Turn this into a pitch.

[Technical plan]
Work out equipment and layout.

[Generate mock experience]
Show a visitor walkthrough.
```

User selects:

> “Generate mock experience.”

---

## T6 — Generated visitor walkthrough

The system outputs:

```text
Visitor enters a dim first zone. A projection shows a doorway, but the doorway is slightly misaligned with the actual wall. A voice repeats a domestic phrase, changing one word each time.

As the visitor moves forward, the phrase begins appearing as text in another room before it is spoken. The rooms seem to be remembering out of order.

By the final zone, the visitor sees fragments from earlier rooms layered incorrectly, as if the space has confused which memory belongs where.
```

User:

> “Yes. That’s it. But less theatrical.”

Tags:

```text
accepts_out_of_order_memory: +1
tone_less_theatrical: +1
prefers_subtlety: +1
```

The system updates style rules.

---

## T7 — Handoff package

The final package includes:

```text
Artifact:
Small-gallery multimedia installation

Working title:
Rooms Remember Badly

Core concept:
A spatial installation where rooms appear to misremember former occupants through distorted projections, repeated phrases, and leaking fragments between zones.

Visitor experience:
Subtle, slow, spatial, non-literal.

Components:
- 3-zone visitor path
- projection behaviours
- sound loop rules
- object/material suggestions
- lighting plan
- artist statement
- grant proposal summary
- technical equipment list
- installation diagram

Style rules:
- avoid literal ghosts
- avoid over-explanation
- use repetition with slight error
- make memory feel spatial and unstable
```

Downstream generation can produce:

* gallery proposal PDF
* artist statement
* technical rider
* floor plan
* projection script
* sound text fragments
* budget estimate
* installation checklist

Memory retained:

```text
User prefers subtlety over theatricality.
User uses poetic spatial metaphors.
User may reject overly commercial framing.
```

---

# Scenario 5

## From “my mornings are chaos” to a household operating system, visual routine, automations, and child-friendly cards

### User

A parent.

They do not want “productivity software.” They want life to be less chaotic.

---

## T0 — Half-thought input

User:

> “Every school morning is a disaster. Shoes, lunchboxes, permission slips, someone crying, me yelling. I need some kind of system but not another app I have to maintain.”

Possible artifacts:

* family routine
* checklist
* visual schedule
* printable cards
* home automation
* reminder system
* packing station layout
* evening prep process
* child reward chart
* calendar integration
* fridge board
* parent script
* physical organisation setup

---

## T1 — Anchor extraction

```text
who:
- parent
- children

when:
- school mornings

problem:
- repeated chaos
- forgotten items
- emotional escalation

negative preference:
- not another app to maintain

desired outcome:
- calmer mornings

possible domains:
- routine design
- household workflow
- child-friendly visual system
- physical organisation
```

Tags:

```text
household_workflow: +1
morning_routine: +1
emotional_load: +1
rejects_app_maintenance: +1
needs_low_friction_system: +1
```

---

## T2 — Possibility cards

```text
This could become:

A. Printable visual routine cards
B. Evening reset checklist
C. Launch-pad station by the door
D. Parent reminder flow
E. Child responsibility board
F. Full family morning system
```

User:

> “F, but physical. I don’t want to be checking my phone.”

Tags:

```text
prefers_physical_system: +1
rejects_phone_based_solution: +1
whole_routine_needed: +1
```

---

## T3 — Artifact composition

```text
Primary artifact:
- household morning routine system

Supporting artifacts:
- physical launch station
- child visual cards
- evening prep checklist
- parent reminder script
- weekly reset routine
- optional calendar reminders
```

Schemas active:

```text
- routine design schema
- checklist schema
- child-friendly visual design schema
- physical layout schema
- behaviour support schema
```

The live surface becomes a routine map:

```text
School Morning System
├── Night before
├── Wake-up
├── Food
├── Clothes
├── Bags
├── Shoes
├── Door exit
└── Recovery plan
```

---

## T4 — System makes the hidden structure visible

The system observes:

> The problem may not be the morning itself. The morning is overloaded because decisions and preparation are happening too late.

It displays a conflict card:

```text
Possible root issue:
Too many morning decisions.

Design implication:
Move decisions and item gathering to the evening.
```

User:

> “Yes. That’s exactly it.”

Decision:

```text
System should shift preparation from morning to previous evening.
```

---

## T5 — Generated physical setup

The system generates three physical setup concepts:

```text
A. Door Launch Pad
Each child has a basket/hook area for shoes, bag, hat, lunchbox.

B. Kitchen Command Strip
Lunch, forms, water bottles, and school notes live together.

C. Bedroom-to-Door Path
Visual cards placed at each physical location in sequence.
```

User:

> “A and C. Kitchen is too crowded.”

Tags:

```text
prefers_door_station: +1
prefers_location_based_cards: +1
rejects_kitchen_centre: +1
```

---

## T6 — Missing map

```text
Still needed:

Number of children         unknown
Ages                       unknown
School departure time      unknown
Common failure points      partial
Available wall/door space  unknown
Printer access             unknown
Reward style               open
```

The system asks through a compact surface:

```text
Tell me the basics:

Children:
[1] [2] [3] [4+]

Card style:
[Pictures] [Words] [Both]

Tone:
[Playful] [Calm] [Mission mode] [Minimal]
```

User selects:

```text
2 children
Pictures + words
Calm
```

---

## T7 — Final package

The system outputs:

```text
Artifact:
Physical household morning system

Components:
- evening reset checklist
- door launch-pad layout
- child visual cards
- parent calm script
- forgotten-item recovery rule
- Sunday reset checklist

Design rules:
- physical first, not phone-based
- calm tone
- pictures plus words
- reduce morning decisions
- make success visible to children

Printable outputs:
- child routine cards
- door checklist
- evening prep list
- weekly reset card
```

Downstream generation produces:

* printable card PDF
* wall layout diagram
* parent guide
* optional reminder automation
* shopping list for hooks/baskets/labels

Memory retained:

```text
User wants low-maintenance systems.
User prefers physical workflows over phone apps for family routines.
User responds strongly to root-cause reframing.
```

This scenario shows the system producing a physical/social/process artifact, not software.

---

# Scenario 6

## From “I need to make people care about this data” to an interactive public report, explainer, and advocacy site

### User

A small environmental nonprofit.

They have spreadsheets and reports but no clear communication artifact.

---

## T0 — Half-thought input

User:

> “We have all this water quality data and nobody cares. The council asks for reports, but the public needs to understand what’s happening. I don’t know if this is a report, a website, a campaign, or what.”

Possible artifacts:

* technical report
* public explainer
* interactive data story
* advocacy website
* dashboard
* social campaign
* presentation
* policy brief
* map
* community workshop
* media kit

---

## T1 — Anchor extraction

```text
who:
- council
- public
- nonprofit

what:
- water quality data

problem:
- data exists but does not create understanding or action

artifact uncertainty:
- report / website / campaign / dashboard

possible domains:
- data communication
- public advocacy
- policy
- environmental reporting
```

Tags:

```text
data_to_story: +1
public_understanding_needed: +1
multiple_audiences: +1
possible_report: +1
possible_website: +1
possible_campaign: +1
```

---

## T2 — Live surface: audience split

The system proactively shows:

```text
This may need different artifacts for different audiences.

Council needs:
- evidence
- methodology
- recommendations
- credibility

Public needs:
- plain language
- visual story
- local relevance
- action steps

Media needs:
- clear headline
- key facts
- images/charts
- quotes
```

User:

> “Yes. That’s the problem. The council version kills the public version.”

Observation:

> The core issue is audience conflict. A single report cannot serve all audiences equally.

Decision:

```text
Use a multi-artifact communication package instead of one universal report.
```

---

## T3 — Artifact composition

```text
Primary artifact:
- public interactive data story

Supporting artifacts:
- council technical report
- policy brief
- media kit
- social posts
- public explainer
```

Schemas active:

```text
- data story schema
- report schema
- policy brief schema
- public explainer schema
- interactive website schema
- chart/map schema
```

---

## T4 — Generated contrast set

The system shows three possible public framings:

```text
A. “The river is changing”
A slow visual story showing change over time.

B. “Can I swim here?”
A practical public-facing safety and location guide.

C. “What changed after the storm?”
A cause-and-effect story around specific events.

D. “Three things the data shows”
A concise advocacy campaign.
```

User:

> “A with some B. People care when it connects to places they know.”

Tags:

```text
prefers_place_based_story: +1
change_over_time_frame: +1
public_practical_relevance: +1
```

---

## T5 — Schema-rendered UI

The interface becomes a data story structure:

```text
Interactive Data Story
├── Opening claim
├── Place-based map
├── Time trend
├── Key indicators
├── What this means
├── Local stories
├── What needs to change
└── Take action
```

Missing map:

```text
Data files              missing
Locations               unknown
Indicators              unknown
Time range              unknown
Council recommendations open
Public action           open
Tone                    open
```

The system asks:

```text
What can you provide now?

[Upload data]
[Describe findings]
[Start with story structure]
[Generate placeholder site]
```

User chooses:

> “Start with story structure. Data later.”

The system does not block.

---

## T6 — Generated preview

It generates a public site outline:

```text
Page title:
The River Is Changing

Hero:
A local river image or map with one plain-language claim.

Section 1:
What we measured

Section 2:
What changed over time

Section 3:
What it means for places people know

Section 4:
What council can do

Section 5:
What residents can do

Download:
Full technical report for council
```

User:

> “Good. But less alarmist. We need credibility.”

Tags:

```text
tone_credible_not_alarmist: +1
needs_public_trust: +1
```

Decision:

```text
Tone should be credible, calm, evidence-led, and locally grounded.
```

---

## T7 — Final handoff

```text
Artifact composition:
- interactive public data story website
- council report
- policy brief
- media kit

Primary audience:
local public

Secondary audience:
council and media

Design rules:
- place-based
- calm and credible
- visual but not sensational
- plain language
- link public claims to technical evidence

Website sections:
- opening claim
- map / location view
- time trend
- key indicators
- meaning
- recommendations
- action

Data requirements:
- water quality indicators
- location names
- dates
- thresholds
- methodology
```

Downstream workflows:

```text
Data workflow:
- clean uploaded spreadsheets
- identify indicators
- generate charts

Writing workflow:
- public explainer
- technical report
- policy brief

Web workflow:
- generate interactive site
- integrate charts/maps
- deploy public page

Media workflow:
- press release
- social cards
- summary images
```

Memory retained:

```text
Organisation needs multi-audience outputs.
Prefers credible calm tone.
Public-facing work should be place-based.
```

This scenario shows the system splitting one vague communication problem into a coordinated artifact ecosystem.

---

# Scenario 7

## From “I want a day out that won’t exhaust me” to an accessibility-aware route, schedule, contingency plan, and shareable itinerary

### User

A person planning a day trip with fatigue and accessibility constraints.

They do not need a generic itinerary. They need a plan that fits their body, energy, time, transport, and preferences.

---

## T0 — Half-thought input

User:

> “I want to go into the city Saturday, maybe see something interesting and get lunch, but I can’t do one of those exhausting days. I need it to be manageable.”

Possible artifacts:

* itinerary
* route
* accessibility-aware plan
* transport plan
* map
* restaurant shortlist
* pacing schedule
* contingency plan
* companion share sheet
* packing checklist

---

## T1 — Anchors

```text
when:
- Saturday

where:
- city

goals:
- see something interesting
- lunch
- manageable day

constraints:
- fatigue / energy limitation
- avoid exhausting schedule

artifact type:
- route / plan likely
```

Tags:

```text
route_plan: +1
accessibility_sensitive: +1
energy_constraint: +1
needs_pacing: +1
possible_itinerary: +1
```

The system should not simply list attractions.

It should recognise the plan is constrained by energy management.

---

## T2 — First surface: day shape

The system shows:

```text
What kind of day should this be?

A. One main activity + lunch + home
B. Two short stops with rest between
C. Flexible wandering with escape routes
D. Specific appointment-style itinerary
```

User:

> “A or B. I want to feel like I did something, not push it.”

Tags:

```text
prefers_low_density_plan: +1
wants_meaningful_activity: +1
avoid_overpacked_day: +1
```

Observation:

> The plan should optimise for energy preservation and emotional satisfaction, not maximum number of stops.

---

## T3 — Artifact composition

```text
Primary artifact:
- manageable city day itinerary

Supporting artifacts:
- transport route
- rest stop map
- lunch shortlist
- contingency plan
- companion share version
- packing checklist
```

Schemas active:

```text
- itinerary schema
- route schema
- accessibility constraint schema
- decision artifact schema
- contingency plan schema
```

---

## T4 — Missing map

```text
Still needed:

Starting location          unknown
City                       unknown
Mobility constraints       open
Transport mode             open
Budget                     open
Food preferences           open
Energy limit               forming
Must-see interests         unknown
```

The system asks through generated sliders/cards:

```text
Energy budget:
[Very low] [Low] [Moderate] [High]

Transport:
[Public transport] [Drive] [Taxi/rideshare] [Walk mostly]

Activity style:
[Gallery] [Market] [Nature] [Bookshop/cafe] [Museum] [Surprise me]
```

User selects:

```text
Energy: low
Transport: public transport + taxi if needed
Activity: gallery or bookshop/cafe
```

---

## T5 — Decision closure and assumptions

Decision ledger:

```text
Decision:
Use low-density itinerary with one main activity and one optional second stop.

Reason:
User wants meaningful day without exhaustion.

Decision:
Include taxi fallback.

Reason:
User selected public transport but allowed taxi if needed.

Decision:
Include rest stops as first-class route objects.

Reason:
Energy constraint is central.
```

Assumption shelf:

```text
Assumption:
Plan should include a clear exit point after the main activity.

Assumption:
Lunch should be seated, nearby, and not require long waiting.

Assumption:
Walking distance should be minimised.
```

User accepts all.

---

## T6 — Generated plan structure

The system generates:

```text
Day Plan Structure

1. Leave home
2. Transit to main area
3. Main activity
4. Rest buffer
5. Lunch
6. Optional second stop only if energy allows
7. Easy route home
8. Taxi fallback at two points
```

It shows the plan as a branching route:

```text
Main Path:
Home → Gallery → Lunch → Home

Optional Branch:
Lunch → Bookshop/Cafe → Home

Fallback:
Any point → taxi home
```

---

## T7 — Final output

The final artifact is not a web app. It is a route/plan artifact.

```text
Outputs:
- personal itinerary
- route map
- rest stop list
- lunch shortlist
- optional branch
- taxi fallback points
- shareable companion version
- packing checklist
```

The shareable version says:

```text
The goal is a manageable day, not fitting in everything.
The plan includes rest buffers and optional stops.
If energy drops, the fallback plan is already chosen.
```

Memory retained:

```text
User prefers low-density plans.
Energy preservation is a primary constraint.
Plans should include exit ramps and optional branches.
```

This scenario demonstrates that the system is universal enough to produce a route/planning artifact rather than a digital product.

---

# Scenario 8

## From “I have a haunted library idea” to a narrative bible, game mechanic, prototype, and pitch deck

### User

An indie game designer or writer.

They have atmosphere and a hook, but no structured game concept.

---

## T0 — Half-thought input

User:

> “I keep thinking about a library that rewrites itself. Like the books are changing because the building is trying to hide something. I don’t know if it’s a game, a story, or a weird interactive thing.”

Possible artifacts:

* short story
* game concept
* interactive fiction
* puzzle game
* narrative website
* world bible
* pitch deck
* prototype
* mystery plot
* character system
* visual style guide

---

## T1 — Anchors

```text
setting:
- library

core mechanic / image:
- rewrites itself
- changing books
- building hides something

genre:
- mystery / supernatural / psychological

artifact uncertainty:
- game / story / interactive thing
```

Tags:

```text
narrative_artifact: +1
possible_game: +1
interactive_fiction: +1
mystery_structure: +1
setting_library: +1
living_environment: +1
```

---

## T2 — Possibility board

The system shows:

```text
This could become:

A. Short story
A literary mystery about memory and truth.

B. Interactive fiction
Reader choices change which books exist.

C. Puzzle game
Players compare changing texts to uncover hidden events.

D. Narrative web experience
A browser-based library interface where pages mutate.

E. Full game pitch
World, mechanic, characters, prototype plan.
```

User:

> “C and D. I like the idea that the interface is the library catalogue.”

Tags:

```text
prefers_puzzle_mechanic: +1
prefers_browser_interface: +1
catalogue_as_interface: +1
interactive_artifact: +1
```

Decision:

```text
The core interface should be a library catalogue that changes over time.
```

---

## T3 — Artifact composition

```text
Primary artifact:
- interactive narrative puzzle prototype

Supporting artifacts:
- world bible
- mystery structure
- catalogue UI
- puzzle rules
- visual style guide
- pitch deck
```

Schemas active:

```text
- narrative schema
- game mechanic schema
- puzzle schema
- interactive web prototype schema
- worldbuilding schema
- pitch deck schema
```

---

## T4 — Generated mechanics surface

The system displays:

```text
Possible core mechanics:

A. Compare editions
Books have different versions. Differences reveal clues.

B. Catalogue drift
Search results change based on what the player knows.

C. Forbidden indexing
Some books cannot be found until miscatalogued.

D. Room memory
Library rooms change the text of books nearby.

E. Librarian notes
Marginalia contradicts the catalogue.
```

User:

> “A, B, and E. C sounds cool but maybe later.”

Tags:

```text
compare_versions_mechanic: +1
dynamic_search_results: +1
marginalia_clues: +1
forbidden_indexing_future: +1
```

Decision:

```text
v1 prototype mechanics:
- compare editions
- changing search results
- contradictory marginalia
```

---

## T5 — Missing map

```text
Still needed:

Player goal              unknown
Mystery being hidden     unknown
Prototype length         open
Number of books          open
Visual style             open
Ending style             unknown
Technology scope         open
```

The system generates mystery options:

```text
What is the library hiding?

A. A person was erased from records
B. The building caused a disaster
C. The books are protecting the reader
D. The catalogue is alive and afraid
E. The librarian changed history
```

User:

> “A, but not literally erased from reality. Erased from institutional memory.”

Observation:

> The story is about institutional forgetting, not cosmic disappearance.

Style tags:

```text
institutional_memory_theme: +1
rejects_literal_magic_excess: +1
prefers_grounded_supernatural: +1
```

---

## T6 — Schema-rendered prototype surface

The UI becomes a prototype planning board:

```text
Prototype
├── Catalogue screen
├── Search mechanic
├── Book detail page
├── Edition comparison
├── Marginalia layer
├── Clue state
├── Ending trigger
└── Pitch summary
```

The system generates the first prototype loop:

```text
Player searches for a missing author.
Initial catalogue says no records found.
After reading marginalia in an unrelated book, search results change.
A second edition of a book appears.
Comparing editions reveals that one staff member was removed from acknowledgements.
This unlocks a restricted shelf entry.
```

User:

> “Yes. That feels playable.”

Decision:

```text
Prototype loop accepted.
```

---

## T7 — Handoff package

```text
Artifact:
Interactive narrative puzzle web prototype

Working title:
The Catalogue Forgets

Core premise:
A library catalogue changes as the player uncovers evidence of a person erased from institutional memory.

Primary interface:
Searchable library catalogue

Core mechanics:
- changing search results
- edition comparison
- marginalia clues
- clue-state-dependent content

Prototype scope:
10–15 minute browser experience

Outputs:
- narrative bible
- puzzle flow
- UI wireframe
- data model for books/clues
- prototype build spec
- pitch deck
```

Downstream build:

```text
Writing workflow:
- book entries
- marginalia
- clue text
- ending text

Design workflow:
- catalogue UI
- book detail screen
- edition comparison view

Code workflow:
- web prototype
- state management
- searchable catalogue
- clue unlock logic

Pitch workflow:
- one-page concept
- 8-slide deck
```

Memory retained:

```text
User likes interface-as-world design.
User prefers grounded supernatural ideas.
User may save rejected mechanics as later expansions.
```

This scenario shows the same system producing a hybrid narrative/game/software artifact.

---

# Scenario 9

## From “our warehouse handovers are chaos” to an internal workflow, SOP, dashboard, and automation plan

### User

A warehouse supervisor.

They do not think in AI terms. They have a recurring operational breakdown.

---

## T0 — Half-thought input

User:

> “Every shift says the previous shift didn’t leave things properly. Stock gets moved, notes are missing, and then everyone blames everyone else. I need something to stop the handover fights.”

Possible artifacts:

* SOP
* shift handover checklist
* dashboard
* inventory movement log
* incident report
* staff communication workflow
* QR-code station system
* mobile form
* accountability process
* training module
* physical board

---

## T1 — Anchors

```text
who:
- warehouse shifts
- supervisors
- staff

when:
- shift handover

problem:
- missing notes
- moved stock
- blame
- poor accountability

goal:
- reduce conflict
- improve continuity

artifact uncertainty:
- workflow / SOP / software / physical board
```

Tags:

```text
handover_process: +1
operations_context: +1
accountability_needed: +1
missing_information: +1
shift_based_workflow: +1
```

---

## T2 — Possibility cards

```text
This could become:

A. Shift handover checklist
B. Digital handover log
C. Physical station board
D. Stock movement exception log
E. Supervisor dashboard
F. Handover SOP and training pack
```

User:

> “B and F. Physical board won’t survive here.”

Tags:

```text
prefers_digital_log: +1
needs_SOP: +1
rejects_physical_board: +1
```

---

## T3 — Artifact composition

```text
Primary artifact:
- digital shift handover workflow

Supporting artifacts:
- SOP
- handover form
- exception log
- supervisor dashboard
- training guide
```

Schemas active:

```text
- workflow schema
- SOP schema
- form schema
- dashboard schema
- accountability schema
```

---

## T4 — Process surface

The system maps the current handover:

```text
Current implied process:
Shift ends
→ notes may or may not be written
→ stock may be moved
→ next shift discovers issue
→ blame / argument
```

The system shows a conflict card:

```text
Root issue:
The handover is informal, so responsibility is reconstructed after the fact.

Design implication:
Capture state before shift end, not after problems appear.
```

User:

> “Exactly. It has to happen before they clock off.”

Decision:

```text
Handover submission must occur before shift close.
```

---

## T5 — Generated workflow options

```text
A. End-of-shift checklist
Staff complete required fields before clock-off.

B. Exception-first log
Only unusual issues are recorded.

C. Supervisor sign-off
Supervisor reviews and accepts handover.

D. Photo-backed station status
Staff attach photos of key areas.
```

User:

> “A and C. Photos maybe for problem areas.”

Decision:

```text
Use required end-of-shift checklist with supervisor sign-off.
Photo evidence optional for exceptions.
```

---

## T6 — Missing map

```text
Still needed:

Shift types              unknown
Required handover fields unknown
Supervisor roles         partial
Stock zones              unknown
Exception categories     unknown
Existing systems         unknown
Device availability      unknown
```

The system offers:

```text
Build from:

[Generic warehouse handover template]
[Interview me]
[Upload current checklist]
[Generate options by zone]
```

User selects:

> “Generic template, then I’ll edit.”

The system generates:

```text
Handover fields:
- shift
- supervisor
- zones checked
- unresolved stock issues
- damaged goods
- equipment issues
- safety issues
- priority notes for next shift
- exceptions
- sign-off
```

User edits fields.

---

## T7 — Final handoff

```text
Artifact:
Digital warehouse shift handover system

Outputs:
- mobile-friendly handover form
- supervisor dashboard
- SOP
- training guide
- exception categories
- accountability rules
- implementation plan

Rules:
- handover must be submitted before shift close
- supervisor sign-off required
- exceptions can include optional photos
- next shift sees unresolved issues first
- edits are timestamped

Acceptance criteria:
- staff can submit handover in under 3 minutes
- supervisor can review open issues
- next shift can see unresolved exceptions
- history is searchable
- accountability does not rely on memory
```

Downstream workflows:

```text
No-code workflow option:
- form + database + dashboard

Custom web app option:
- mobile form
- authenticated supervisors
- dashboard
- audit history

Documentation workflow:
- SOP
- training sheet
- rollout email
```

Memory retained:

```text
User values operational practicality.
User rejects fragile physical systems.
User prefers templates they can edit.
```

---

# Scenario 10

## From “I want a tiny business but don’t know what the offer is” to offer design, landing page, booking flow, and launch kit

### User

A skilled individual who wants to start a service business but has not defined the offer.

---

## T0 — Half-thought input

User:

> “People keep asking me to help organise their digital mess. Files, photos, passwords, subscriptions, all that. I could probably make a tiny business out of it, but I don’t know how to package it.”

Possible artifacts:

* business offer
* service package
* landing page
* pricing model
* booking flow
* intake form
* client checklist
* service workflow
* brand name
* launch emails
* ads
* operations manual

---

## T1 — Anchors

```text
who:
- people with digital mess

problem:
- files, photos, passwords, subscriptions disorganised

user capability:
- can help organise

goal:
- package into tiny business

artifact uncertainty:
- business model / offer / website / workflow
```

Tags:

```text
service_business: +1
offer_design_needed: +1
digital_organisation_domain: +1
possible_landing_page: +1
possible_service_workflow: +1
```

---

## T2 — Possibility surface

```text
This could be packaged as:

A. Digital Declutter Session
One-off guided clean-up.

B. Family Digital Archive Setup
Photos, files, memories, backups.

C. Password and Subscription Reset
Practical safety and account clean-up.

D. Monthly Digital Admin Service
Ongoing help.

E. Life Admin Rescue Package
Files, accounts, subscriptions, forms, reminders.
```

User:

> “A and E. I don’t want to touch people’s passwords though.”

Tags:

```text
prefers_one_off_service: +1
broad_life_admin_positioning: +1
rejects_password_handling: +1
privacy_boundary: +1
```

Decision:

```text
Service should avoid direct password handling.
```

---

## T3 — Artifact composition

```text
Primary artifact:
- service offer package

Supporting artifacts:
- landing page
- booking flow
- client intake form
- service checklist
- privacy boundary statement
- launch copy
```

Schemas active:

```text
- offer design schema
- service workflow schema
- landing page schema
- intake form schema
- trust/privacy schema
- pricing schema
```

---

## T4 — Generated offer directions

```text
Offer concepts:

A. Digital Declutter Day
A focused session to sort files, photos, subscriptions, and digital clutter.

B. Life Admin Reset
A guided reset for digital paperwork, subscriptions, and recurring admin.

C. Family Archive Starter
Organise family photos and important documents.

D. Calm Inbox & Files
A lighter offer focused on email and file structure.
```

User:

> “Life Admin Reset sounds right. Less corporate. More calm.”

Tags:

```text
accepts_life_admin_reset: +1
tone_calm: +1
rejects_corporate_tone: +1
```

---

## T5 — Live landing page preview

The system generates a landing page preview:

```text
Life Admin Reset

A calm, practical session to help you get your digital life back under control.

For people who have:
- files everywhere
- subscriptions they’ve lost track of
- photos they keep meaning to organise
- admin they avoid because it feels too much

What we do:
- sort your digital clutter
- make a simple folder structure
- identify subscriptions and recurring tasks
- create a maintenance plan

What we do not do:
- handle your passwords
- access sensitive accounts without you present
- make financial or legal decisions for you
```

User:

> “That disclaimer is good. Keep that kind of clarity.”

Decision:

```text
Trust boundaries should be explicit and plain-language.
```

---

## T6 — Missing map

```text
Still needed:

Session length          unknown
Price                   open
Remote or in-person     unknown
Client intake           partial
Booking tool            open
Brand tone              forming
Launch audience         unknown
```

The system asks through option cards:

```text
Package size:

A. 90-minute starter
B. Half-day reset
C. Full-day reset
D. Two-session package
```

User:

> “Half-day reset and maybe a cheaper starter.”

Artifact composition updates:

```text
Offers:
- 90-minute starter
- half-day reset
```

---

## T7 — Final handoff

```text
Artifact:
Tiny service business launch kit

Offer:
Life Admin Reset

Packages:
- 90-minute starter
- half-day reset

Boundaries:
- no direct password handling
- no legal/financial advice
- client remains present for sensitive accounts

Outputs:
- landing page copy
- service workflow
- intake form
- booking questions
- pricing options
- launch post
- client checklist
- privacy/trust statement
```

Downstream execution:

```text
Website workflow:
- generate one-page site
- create booking form
- create confirmation email

Operations workflow:
- service checklist
- client prep email
- post-session summary template

Marketing workflow:
- launch announcement
- social posts
- referral message
```

Memory retained:

```text
User prefers calm tone.
User wants explicit trust boundaries.
User is cautious around sensitive access.
```

---

# Scenario 11

## From “we need a better way to choose projects” to a decision system, scoring surface, governance process, and dashboard

### User

A leadership team at a small company.

They are overwhelmed by too many possible initiatives.

---

## T0 — Half-thought input

User:

> “We have too many ideas and no good way to decide what to actually do. Every meeting ends with more projects, not fewer.”

Possible artifacts:

* prioritisation framework
* decision matrix
* strategy workshop
* project intake process
* scoring dashboard
* governance policy
* roadmap
* meeting structure
* portfolio board
* evaluation rubric

---

## T1 — Anchors

```text
who:
- leadership team

problem:
- too many ideas
- no decision process
- meetings create more projects

goal:
- choose what to do
- reduce overload

possible artifact:
- decision system
- prioritisation process
- dashboard
- workshop
```

Tags:

```text
decision_artifact: +1
prioritisation_needed: +1
project_overload: +1
governance_needed: +1
meeting_failure: +1
```

---

## T2 — Possibility surface

```text
This could become:

A. Project scoring matrix
B. Decision workshop format
C. Project intake and triage process
D. Portfolio dashboard
E. Strategy governance system
```

User:

> “C and A. The problem starts before the meeting.”

Observation:

> The decision system needs an intake filter before ideas reach leadership discussion.

Decision:

```text
Create a project intake and triage process with scoring matrix.
```

---

## T3 — Artifact composition

```text
Primary artifact:
- project prioritisation system

Supporting artifacts:
- intake form
- scoring rubric
- meeting process
- portfolio dashboard
- decision rules
- governance cadence
```

Schemas active:

```text
- decision matrix schema
- project intake schema
- governance process schema
- dashboard schema
- meeting schema
```

---

## T4 — Generated criteria options

```text
Possible scoring criteria:

A. Strategic alignment
B. Customer impact
C. Revenue potential
D. Operational effort
E. Risk
F. Time to value
G. Required capacity
H. Reversibility
```

User:

> “A, B, D, F, and capacity. Revenue matters but not for everything.”

Tags:

```text
strategic_alignment: +1
customer_impact: +1
effort_constraint: +1
time_to_value: +1
capacity_constraint: +1
revenue_secondary: +1
```

Decision:

```text
Revenue should not be a universal scoring requirement.
```

---

## T5 — Decision closure surface

The system shows scoring model options:

```text
A. Simple 1–5 score
B. T-shirt sizing
C. Must / Should / Could
D. Weighted score
E. Red / Amber / Green
```

User:

> “T-shirt sizing for effort, 1–5 for impact. Weighted scores get fake.”

This is a critical reaction.

Tags:

```text
rejects_fake_precision: +1
prefers_mixed_evaluation: +1
```

Decision:

```text
Use mixed evaluation model:
- 1–5 for impact/alignment
- t-shirt size for effort/capacity
- no weighted total score in v1
```

This mirrors the earlier doctrine: avoid fake certainty.

---

## T6 — Final handoff

```text
Artifact:
Project prioritisation and intake system

Components:
- project idea intake form
- triage rubric
- leadership review board
- decision rules
- meeting agenda
- portfolio dashboard
- archive / parking lot

Rules:
- ideas must pass intake before leadership review
- capacity must be considered before approval
- no automatic weighted score
- every approved project must have owner, outcome, and review date

Outputs:
- intake form
- scoring guide
- dashboard structure
- workshop agenda
- governance SOP
```

Downstream execution:

```text
No-code system:
- form
- project database
- dashboard
- review workflow

Document system:
- governance guide
- scoring rubric
- meeting templates
```

Memory retained:

```text
Team dislikes fake precision.
Team needs upstream filtering.
Capacity is a recurring constraint.
```

---

# Scenario 12

## From “we should do something for our town’s anniversary” to an event, exhibit, website, oral history project, and volunteer workflow

### User

A local history group.

They start with a vague civic/cultural idea.

---

## T0 — Half-thought input

User:

> “The town turns 150 next year and we should do something, but nobody agrees what. Some people want a dinner, some want a book, some want school involvement. It’s all vague.”

Possible artifacts:

* event
* exhibition
* commemorative book
* website
* oral history archive
* school program
* volunteer workflow
* fundraising plan
* social media campaign
* timeline installation
* walking tour

---

## T1 — Anchors

```text
who:
- local history group
- town residents
- schools
- volunteers

when:
- next year

occasion:
- 150th anniversary

problem:
- no agreement on artifact

possible artifacts:
- event, book, school program, archive, website
```

Tags:

```text
civic_project: +1
multi_stakeholder: +1
anniversary_event: +1
artifact_uncertain: +1
community_history: +1
```

---

## T2 — Possibility surface

The system shows:

```text
This may be a program, not one artifact.

Possible program models:

A. One big event
Dinner, speeches, performances.

B. Public exhibition
Photos, stories, timeline, objects.

C. Oral history archive
Collect stories from residents.

D. School-linked history project
Students interview elders and create displays.

E. Multi-part anniversary program
Small event + exhibit + website + school involvement.
```

User:

> “E. That’s probably why we’re stuck. It’s not one thing.”

Decision:

```text
Treat anniversary as a multi-artifact community program.
```

---

## T3 — Artifact composition

```text
Primary artifact:
- anniversary program

Supporting artifacts:
- public event
- small exhibition
- oral history archive
- school activity
- website
- volunteer workflow
- sponsorship package
```

Schemas active:

```text
- event schema
- exhibition schema
- oral history schema
- education program schema
- volunteer coordination schema
- website schema
- sponsorship schema
```

---

## T4 — Live program map

The screen renders:

```text
Town 150 Program
├── Public Event
├── Exhibition
├── Oral Histories
├── Schools
├── Website
├── Volunteers
├── Sponsorship
└── Timeline
```

The user clicks “oral histories.”

The system generates options:

```text
Oral history collection could be:

A. 10 featured interviews
B. Open community submission
C. Student-led elder interviews
D. Themed story prompts
E. Audio booth at event
```

User:

> “C and D. Students interviewing elders would be meaningful.”

Tags:

```text
school_involvement: +1
intergenerational_storytelling: +1
themed_prompts: +1
```

---

## T5 — Missing map

```text
Still needed:

Budget                    unknown
Venue                     unknown
Volunteer capacity         unknown
School contacts            partial
Anniversary date           known next year, exact open
Archive permission rules   unknown
Sponsorship needs          open
Program scale              forming
```

The system flags a risk:

```text
Risk:
The program is expanding into many artifacts. Without a scope boundary, it may become unmanageable.

Suggested scope:
Define a minimum viable anniversary program.
```

User:

> “Yes. Minimum version first.”

Decision:

```text
Define minimum viable anniversary program before expanding.
```

---

## T6 — Minimum viable program

The system proposes:

```text
Minimum viable anniversary program:

1. One public afternoon event
2. Small photo/story exhibition
3. 10 student-led oral histories
4. Simple website page
5. Volunteer sign-up form
6. Sponsorship one-pager
```

User:

> “That’s realistic.”

Decision ledger:

```text
MVP anniversary scope accepted.
```

---

## T7 — Final handoff

```text
Artifact:
Town 150 minimum viable community program

Components:
- public event
- exhibition
- oral history project
- school involvement
- simple website
- volunteer workflow
- sponsorship sheet

Outputs:
- program plan
- volunteer roles
- event run sheet
- school interview kit
- oral history consent form
- exhibition layout
- website structure
- sponsorship one-pager
```

Downstream workflows:

```text
Event workflow:
- run sheet
- role assignments
- logistics checklist

Education workflow:
- student interview guide
- teacher pack
- consent process

Website workflow:
- anniversary landing page
- story submission form
- oral history archive structure

Design workflow:
- poster
- exhibition panels
- sponsorship PDF
```

Memory retained:

```text
Group benefits from scope reduction.
Community projects may need program composition, not single-artifact framing.
```

---

# Scenario 13

## From “I want something that explains my research” to a paper summary, interactive explainer, conference talk, and public demo

### User

A researcher.

They have complex work and multiple possible audiences.

---

## T0 — Half-thought input

User:

> “My research is too hard to explain. The paper is dense, the talk is coming up, and I also need something public-facing. I don’t know where to start.”

Possible artifacts:

* paper summary
* conference talk
* slide deck
* public explainer
* interactive demo
* diagram
* abstract
* poster
* video script
* website
* press summary

---

## T1 — Anchors

```text
who:
- research peers
- conference audience
- public audience

what:
- research

problem:
- hard to explain
- dense paper
- talk upcoming

artifact uncertainty:
- multiple outputs needed
```

Tags:

```text
research_communication: +1
multi_audience: +1
needs_simplification: +1
possible_talk: +1
possible_public_explainer: +1
```

---

## T2 — Audience split surface

The system shows:

```text
This likely needs layered explanation, not one explanation.

Layer 1 — Expert
Precise, technical, defensible.

Layer 2 — Adjacent academic
Conceptual, still rigorous.

Layer 3 — Public
Plain language, metaphor, why it matters.

Layer 4 — Demo
Interactive or visual proof of the idea.
```

User:

> “Yes. I keep mixing those audiences.”

Observation:

> The core problem is audience-layer collapse.

Decision:

```text
Use layered explanation architecture.
```

---

## T3 — Artifact composition

```text
Primary artifact:
- layered research communication package

Supporting artifacts:
- expert abstract
- conference talk
- public explainer
- core diagram
- demo concept
- Q&A prep
```

Schemas active:

```text
- research explanation schema
- presentation schema
- public explainer schema
- diagram schema
- demo schema
```

---

## T4 — Concept extraction surface

The system asks through generated cards:

```text
What is the best public-facing shape?

A. “We found a new way to…”
B. “The problem everyone misses is…”
C. “Imagine if…”
D. “This changes how we measure…”
E. “The old model assumes X, but…”
```

User:

> “E. The old model assumes something that breaks in messy real data.”

Tags:

```text
contrast_explanation: +1
old_model_vs_new_model: +1
messy_real_data_theme: +1
```

The system generates a central explanation:

```text
The work is about what happens when a model that works in clean conditions is used in messy real-world conditions.
```

User:

> “That’s much closer.”

---

## T5 — Final handoff

```text
Artifact:
Layered research communication package

Core explanation:
Old model works under clean assumptions; this research addresses failure under messy real-world conditions.

Outputs:
- expert abstract
- adjacent-field summary
- public explainer
- conference talk structure
- central diagram
- demo concept
- Q&A prep

Design rule:
Do not start with methods. Start with the broken assumption.
```

Downstream generation:

```text
Writing workflow:
- summaries at three levels

Slides workflow:
- conference deck

Visual workflow:
- core diagram

Demo workflow:
- simple interactive example
```

Memory retained:

```text
User benefits from layered audience separation.
User tends to overmix expert and public explanation.
```

---

# Scenario 14

## From “I want to make a meal plan but I hate meal plans” to a flexible food system, shopping logic, and weekly rhythm

### User

A person trying to reduce decision fatigue around food.

---

## T0 — Half-thought input

User:

> “I need to eat better but I hate meal plans. They make me feel trapped. I just want the fridge to make sense.”

Possible artifacts:

* meal plan
* flexible food system
* grocery list
* fridge layout
* recipe bank
* decision tree
* weekly prep rhythm
* shopping template
* dietary tracker
* habit system

---

## T1 — Anchors

```text
goal:
- eat better

negative preference:
- hates meal plans
- feels trapped

desired state:
- fridge makes sense

artifact uncertainty:
- food system, not traditional meal plan
```

Tags:

```text
food_system: +1
rejects_rigid_meal_plan: +1
decision_fatigue: +1
wants_flexible_structure: +1
```

Observation:

> User does not need a fixed meal plan. They need a flexible decision system for food.

---

## T2 — Possibility surface

```text
This could become:

A. Flexible meal matrix
Choose from categories, not fixed days.

B. Fridge zones
Organise ingredients by use.

C. Default meals list
Reliable meals for low-energy days.

D. Shopping template
Buy building blocks, not recipes.

E. Weekly reset rhythm
Small repeatable prep routine.
```

User:

> “A, C, D. Fridge zones maybe too.”

Artifact composition:

```text
Primary artifact:
- flexible food decision system

Supporting artifacts:
- meal matrix
- default meals
- shopping template
- fridge layout
- weekly reset routine
```

Schemas active:

```text
- routine schema
- decision schema
- shopping list schema
- preference schema
- physical layout schema
```

---

## T3 — Generated system

The system generates:

```text
Food System

Instead of planning exact meals, keep options in slots:

Proteins:
- quick
- batch
- emergency

Carbs / bases:
- rice
- wraps
- pasta
- potatoes

Vegetables:
- fresh easy
- roastable
- frozen backup

Flavour kits:
- sauce
- spice
- dressing

Default meals:
- bowl
- wrap
- pasta
- tray bake
- eggs/toast
```

User:

> “Yes. That feels like freedom.”

Tags:

```text
accepts_modular_food_system: +1
freedom_value: +1
rejects_fixed_schedule: +1
```

Decision:

```text
Food system should be modular and choice-preserving, not calendar-based.
```

---

## T4 — Final output

```text
Artifact:
Flexible food operating system

Components:
- modular meal matrix
- grocery template
- fridge zone guide
- default meal list
- low-energy backup plan
- weekly reset routine

Rules:
- no fixed daily meal calendar
- always include emergency meals
- shop by building blocks
- support choice at point of eating
```

Memory retained:

```text
User prefers flexible systems over rigid schedules.
Feeling trapped is a key rejection signal.
```

This shows the system can produce a personal-life operating artifact with no software required.

---

# Scenario 15

## From “our new AI tool needs onboarding” to an in-product flow, help docs, training workspace, and telemetry plan

### User

A product team.

They have already built a tool, but users do not understand how to adopt it.

---

## T0 — Half-thought input

User:

> “People sign up for the AI tool and then just stare at it. They don’t know what to do first. We need onboarding but not one of those annoying tours.”

Possible artifacts:

* product onboarding flow
* empty state
* guided setup
* sample projects
* templates
* help docs
* lifecycle emails
* demo workspace
* analytics plan
* activation metric
* support flow

---

## T1 — Anchors

```text
who:
- new users

problem:
- sign up but do not know what to do
- blank-state confusion

negative preference:
- annoying tours

goal:
- activation
- first useful action

artifact type:
- product onboarding system
```

Tags:

```text
product_onboarding: +1
blank_state_problem: +1
rejects_annoying_tour: +1
activation_needed: +1
```

---

## T2 — Possibility surface

```text
Onboarding could be:

A. Guided product tour
B. Starter templates
C. Demo workspace
D. First task wizard
E. Contextual empty states
F. Lifecycle emails
```

User:

> “B, C, E. Not A.”

Tags:

```text
prefers_templates: +1
prefers_demo_workspace: +1
prefers_contextual_help: +1
rejects_guided_tour: +1
```

Decision:

```text
Onboarding should teach through usable examples, not pop-up tours.
```

---

## T3 — Artifact composition

```text
Primary artifact:
- in-product onboarding system

Supporting artifacts:
- starter templates
- demo workspace
- empty-state copy
- activation checklist
- help docs
- lifecycle emails
- telemetry plan
```

Schemas active:

```text
- product onboarding schema
- UX writing schema
- template schema
- analytics schema
- lifecycle email schema
```

---

## T4 — Missing map

```text
Still needed:

Target user segments        unknown
First value moment          unknown
Core user action            unknown
Available templates         unknown
Activation metric           unknown
Tone                        open
```

The system flags:

```text
Blocking decision:
What is the first value moment?

Without this, onboarding may optimise for activity instead of success.
```

It shows options:

```text
First value moment might be:

A. User creates first project
B. User imports data
C. User generates first useful output
D. User invites teammate
E. User uses a template successfully
```

User:

> “C. First useful output.”

Decision:

```text
Activation should be based on generating first useful output.
```

---

## T5 — Generated onboarding design

The system generates:

```text
New User Experience

1. Welcome screen asks what they want to accomplish.
2. User chooses from starter templates.
3. Demo workspace shows completed example.
4. Empty states explain next useful action.
5. User generates first output.
6. System prompts them to save, share, or refine.
7. Follow-up email shows next use cases.
```

User:

> “Good. It needs to feel competent, not cute.”

Tags:

```text
tone_competent: +1
rejects_cute_tone: +1
```

---

## T6 — Final handoff

```text
Artifact:
AI tool onboarding system

Components:
- welcome screen
- starter templates
- demo workspace
- contextual empty states
- first-output flow
- activation checklist
- help docs
- lifecycle emails
- telemetry events

Design rules:
- no pop-up tour
- teach through examples
- optimise for first useful output
- tone competent, not cute

Telemetry:
- selected use case
- template selected
- first output generated
- output saved
- second session returned
```

Downstream workflows:

```text
Design:
- onboarding screens
- empty states
- demo workspace

Engineering:
- template selection flow
- demo workspace
- telemetry events

Content:
- template examples
- help docs
- lifecycle emails
```

Memory retained:

```text
Team prefers product-led onboarding.
Team rejects intrusive tours.
Activation = first useful output.
```

This scenario shows the system acting inside an existing product context.

---

# What these scenarios prove

Across all scenarios, the same system is not changing its core nature. It is changing its active schemas, surfaces, and handoff packages.

The community workshop scenario becomes a production web application.

The teacher scenario becomes a lesson pack.

The policy scenario becomes a rollout system.

The artist scenario becomes an installation and proposal.

The parent scenario becomes a physical household routine.

The nonprofit scenario becomes a public data story and advocacy package.

The accessibility planning scenario becomes a route and contingency artifact.

The game scenario becomes a narrative prototype and pitch.

The warehouse scenario becomes an operational workflow and dashboard.

The tiny business scenario becomes an offer, website, and launch kit.

The leadership scenario becomes a decision system.

The town anniversary scenario becomes a multi-artifact community program.

The research scenario becomes layered communication outputs.

The food scenario becomes a personal operating system.

The product team scenario becomes an onboarding system.

That is the universal claim in motion:

```text
The input can be vague.
The user can be anyone.
The output can be anything.
The system behaviour is still coherent.
```

The constant is not the artifact type.

The constant is the resolution process:

```text
latent intent
→ anchors
→ options
→ reactions
→ traces
→ schemas
→ surfaces
→ decisions
→ specification
→ execution
```

That is the core temporal pattern of the Live Intent Resolution Surface.
