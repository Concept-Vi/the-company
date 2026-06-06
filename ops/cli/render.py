"""render — the human/AI-readable views (status, health). stdlib-only."""
from registry import ceiling_mb, shared_ports
from systemd import verdict, port_open
from gpu import committed_mb, read_gpu, budget_vram, is_gpu_service


def status(reg):
    shared = shared_ports(reg)
    out = ["", "  THE COMPANY — service command center      (`company help` for commands)", ""]
    for g, gdesc in reg["groups"].items():
        members = [(k, v) for k, v in reg["services"].items() if v["group"] == g]
        if not members:
            continue
        out.append(f"  \033[1m{g.upper()}\033[0m — {gdesc}")
        for k, v in members:
            label, sym = verdict(v, shared)
            port = f":{v['port']}" if v.get("port") else ""
            vm = budget_vram(reg, k) if is_gpu_service(v) else 0
            vram = f"~{vm/1000:.1f}G" if vm else ""
            note = f"   ⚠ {v['note']}" if v.get("note") else ""
            out.append(f"    {sym}  {k:<15}{label:<22}{port:<7}{vram:<7}{v['title']}{note}")
        out.append("")
    committed = committed_mb(reg)
    gpu = read_gpu()
    measured = f" · measured {gpu['used']/1024:.1f}/{gpu['total']/1024:.1f} GB used" if gpu else ""
    out.append(f"  GPU budget: ~{committed/1000:.1f} GB of {ceiling_mb(reg)/1000:.1f} GB "
               f"committed by running services{measured}   (`company gpu` for detail)")
    out.append("")
    return "\n".join(out)


def health(reg):
    out = []
    for k, v in reg["services"].items():
        if not v.get("port"):
            continue
        out.append(f"  {'✓' if port_open(v['port']) else '✗'} {k:<15} :{v['port']}")
    return "\n".join(out)
