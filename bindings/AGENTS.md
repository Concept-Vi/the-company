# bindings/ — THE LENSES (Tim Geldard's variable instrument; no hardcoded sectors)
One row per binding (bindings/<id>.py, file-discovered). A BINDING is a declared FILLING of the
equation's slots — centre / angle_from / radius_from / k — NOT the sectors themselves (those resolve
from angle_from against the live data + registries). The instrument opens by resolving the data-driven
default (raw kinds); every other lens is a swappable row. "Nothing hardcoded is valid, only what
occupies that variable at that point." Adding a lens = adding a file. Pure data (the floor).
Row: BINDING = {id, label, angle_from, radius_from, order_by?, groups?}.
angle_from: 'kind' (data-driven, one sector per distinct kind) · 'kind-group' (declared groups —
ONE lens, never the default) · <registry-name> (resolves once the event→row edge is formalized).
