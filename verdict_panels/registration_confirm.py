"""verdict_panels/registration_confirm.py — the REGISTRATION panel (GC7's founding row): three DISTINCT
lenses over one proposed registry dossier, replacing same-role draw-variance with judgment DIVERSITY.
Seats: confirm_registration (grounding — is every claim supported by the element?) · voice_lens
(altitude — does it read like the operator's entries?) · element_fit_lens (claims-fit — do the
capabilities/feature match what the snippet shows?). Quorum 2 of 3 — one dissent flags-not-drops,
exactly the jury's flag discipline. The s102 walk stop proposes re-jurying the 222 no-quorum entries
through THIS panel (the operator's call)."""

PANEL = {
    "id": "registration_confirm",
    "label": "Registration confirm panel (grounding · voice · element-fit)",
    "description": (
        "Judges a proposed registry dossier through three distinct lenses — is it grounded in the "
        "element, does it speak at the operator's altitude, do its claims fit what the element shows. "
        "Two of three grounded = pass; any dissent is named. Diversity catches what repeated draws of "
        "one judge cannot."),
    "seats": ["confirm_registration", "voice_lens", "element_fit_lens"],
    "quorum": 2,
}
