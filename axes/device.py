"""axes/device.py — the DEVICE/medium axis (where & in what substance). The axis Tim NAMED — a spoke, not the
hub. The ROOT of the continuous layout derivations (screen size); orientation/medium are discrete picks."""

AXIS = {
    "id": "device",
    "namespace": "device",
    "fields": {"w": "continuous", "h": "continuous", "orient": "discrete", "kind": "discrete"},
    "value_source": "live",   # window dims (live); kind is browser-DERIVED (size/pointer bucket), NOT authoritative
    "desc": "Where & in what medium — w/h are the continuous root of all layout derivation; orient (portrait/"
            "landscape, h>w) + kind (native-mobile/desktop, derived) are discrete. 'desktop' = landscape + a size "
            "threshold, NOT a third enum (orthogonal axes). The device-axis resolver's coordinate (RESOLVER-CONTRACT §1).",
}
