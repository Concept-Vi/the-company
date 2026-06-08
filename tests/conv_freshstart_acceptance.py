"""tests/conv_freshstart_acceptance.py — V-A · a NEW conversation actually starts FRESH.

Tim's bug (from his phone): "There is a new conversation button … but the first response seems
to default to the same original one so I can't actually start new conversations."

ROOT CAUSE (evidenced): chat() persisted + RETURNED its turns thread-scoped (the additive
`thread_id` on chat.jsonl + the thread-aware `history` field), but the history it FED THE MODEL
was `self.store.chat_history(20)` — the GLOBAL stream, ignoring `_current_thread`. So right after
"new conversation" the model was still shown the PRIOR conversation's last 20 turns → the first
reply "defaulted to the same original one". The persisted/returned history already looked fresh,
so the leak was INVISIBLE to anyone checking the returned `history` — it lived ONLY in the model
input. THIS TEST ASSERTS ON THE MODEL INPUT (the captured `msgs`), which is what discriminates the
buggy code from the fixed code.

This suite proves (model-free — `complete_with_tools` is STUBBED and the stub CAPTURES the msgs):

  1. FRESH-START — converse on conversation #1, then new_conversation() → conversation #2; the
     FIRST turn in #2 feeds the model a `msgs` whose chat-history slice is EMPTY (it does NOT
     carry conversation #1's content). This is the bug-discriminating assertion.

  2. CONTINUITY (no over-correction into amnesia) — a SECOND turn in #2 feeds the model a `msgs`
     that INCLUDES #2's first turn. Fresh ≠ forgetful within the same thread.

  3. EMPTY HISTORY ON A NEW THREAD — the RETURNED history of #2's first turn is exactly that
     turn's two records (user+assistant), never #1's content.

  4. NO LEAK BACKWARD EITHER — #1's turns never carry #2's thread_id (the threads are isolated).

  5. LEGACY GLOBAL STREAM PRESERVED — with NO current thread (None), chat() feeds the model the
     global chat_history (back-compat, byte-for-byte the prior behaviour).

  6. LIST / REOPEN — list_conversations shows both threads; load_conversation(#1) returns #1's
     real history (reopen still works).

  7. RELOAD-SURVIVAL (persisted data) — a FRESH Suite on the SAME store still lists both threads
     and load_conversation returns each thread's turns intact. (The current-POINTER is in-memory
     by design — line 4152 — so reload-survival is scoped to the PERSISTED thread data, which is
     what Tim's reopen path reads.)

MODEL-FREE: no GPU, no endpoint. The brain call is replaced by a stub that records every msgs
array it is handed and returns a fixed reply.
"""
import faulthandler
import os
import sys
import tempfile

faulthandler.dump_traceback_later(120, exit=True)   # hang-guard

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


NODES = os.path.join(ROOT, "nodes")
reg = NodeRegistry(); reg.discover([NODES])

# the captured model inputs — one entry per chat() call: the msgs array handed to the brain.
CAPTURED: list[list[dict]] = []


def fresh_suite(store_dir):
    s = Suite(FsStore(store_dir), reg, nodes_dir=NODES)
    _install_stubs(s)
    return s


def _install_stubs(s: Suite):
    """Replace the brain + capability gate so chat() runs model-free AND we capture the msgs."""
    # 1) capability gate: pretend the configured model is tool-capable (no endpoint probe).
    s._model_supports_tools = lambda model, base_url: True
    # 2) the brain call: capture msgs, return a no-tool text reply. We monkeypatch the module-level
    #    fabric.client.complete_with_tools that chat() imports + calls.
    import fabric.client as _fc

    def _stub_complete_with_tools(transport, msgs, **kw):
        CAPTURED.append([dict(m) for m in msgs])   # snapshot the EXACT model input
        return {"content": "stub reply", "tool_calls": []}

    _fc.complete_with_tools = _stub_complete_with_tools
    # 3) transport builder + config: avoid touching a live endpoint when chat() builds the transport.
    import fabric.transport as _ft
    _ft.openai_tools_transport = lambda **kw: object()
    # ensure a present-tense default mode (listening) so chat() doesn't take the off-path.
    s.set_rhm_config({"mode": "listening", "model": "stub-model", "base_url": "http://stub/v1", "persona": ""})


def history_slice(msgs: list[dict]) -> list[dict]:
    """The chat-history turns the model was fed = everything between the system block and the final
    user turn. (msgs = [system] + history... + [final user message].)"""
    return [m for m in msgs[1:-1]]


def joined(msgs: list[dict]) -> str:
    return "\n".join(m.get("content", "") for m in msgs)


def main():
    tmp = tempfile.mkdtemp(prefix="freshstart-")
    store_dir = os.path.join(tmp, "store")
    s = fresh_suite(store_dir)
    gid = "g0"

    # --- conversation #1 ---------------------------------------------------------------------
    c1 = s.new_conversation("first")
    tid1 = c1["thread_id"]
    CAPTURED.clear()
    s.chat("ORIGINAL_TOPIC_alpha", gid)            # turn 1 of conv #1
    s.chat("ORIGINAL_TOPIC_beta", gid)             # turn 2 of conv #1
    # sanity: conv #1's second turn saw conv #1's FIRST turn in the model input (within-thread continuity)
    check("conv#1 turn2 model-input carries conv#1 turn1",
          "ORIGINAL_TOPIC_alpha" in joined(CAPTURED[-1]))

    # --- conversation #2 (the bug scenario) --------------------------------------------------
    c2 = s.new_conversation("second")
    tid2 = c2["thread_id"]
    check("new_conversation made #2 current", s.current_conversation() == tid2)
    check("the two threads are distinct ids", tid1 != tid2)

    CAPTURED.clear()
    r2a = s.chat("BRAND_NEW_QUESTION", gid)        # FIRST turn of conv #2 — the moment Tim's bug fires

    # (1) THE BUG-DISCRIMINATING ASSERTION: the CONVERSATION-TURN history fed to the model for #2's
    # first turn must be EMPTY (it must NOT replay #1's back-and-forth). This is what's red on the
    # buggy code (global history replays #1's turns as role/content) and green on the fix.
    first_input = CAPTURED[-1]
    hist = history_slice(first_input)
    check("FRESH-START: #2 first-turn model-input conversation-history is EMPTY (no prior-thread turns)",
          len(hist) == 0)
    # #1's content must be ABSENT from the conversation turns specifically. (Where prior text appears at
    # all in a fresh conversation's system block, it is CONFINED to the whole-system "recent activity"
    # telemetry line — a 48-char snippet ticker, NOT replayed turns. That is a SEPARATE, weaker mechanism
    # (_chat_context's recent_events) flagged for the lead, by design cross-thread, and out of V-A's tight
    # scope. We pin that boundary honestly here rather than assert on the whole input.)
    check("FRESH-START: #1's content is ABSENT from #2's first model-input CONVERSATION TURNS",
          all("ORIGINAL_TOPIC" not in (m.get("content") or "") for m in hist))
    leak_lines = [m.get("content", "") for m in first_input
                  if "ORIGINAL_TOPIC" in (m.get("content") or "")]
    check("FRESH-START: any residual prior content is CONFINED to the recent-activity telemetry line",
          all("recent activity:" in ln for ln in leak_lines))   # vacuously true if none; the system block only
    check("FRESH-START: the new question itself IS the final user message",
          first_input[-1].get("content") == "BRAND_NEW_QUESTION")

    # (3) the RETURNED history is just this turn's two records, not #1's.
    check("#2 first-turn returned history = exactly its 2 records (user+assistant)",
          len(r2a["history"]) == 2
          and r2a["history"][0]["text"] == "BRAND_NEW_QUESTION"
          and all("ORIGINAL_TOPIC" not in t["text"] for t in r2a["history"]))
    check("#2 first-turn returned thread_id == #2", r2a.get("thread_id") == tid2)

    # (2) CONTINUITY: a SECOND turn in #2 sees #2's first turn AS A REPLAYED CONVERSATION TURN — not
    # amnesia. Assert on the history SLICE (the role/content turns), not the whole input, so the
    # telemetry ticker can't make this pass for the wrong reason.
    CAPTURED.clear()
    s.chat("FOLLOWUP_in_two", gid)
    cont_hist = joined(history_slice(CAPTURED[-1]))
    check("CONTINUITY: #2 turn2 conversation-history carries #2 turn1 ('BRAND_NEW_QUESTION')",
          "BRAND_NEW_QUESTION" in cont_hist)
    check("CONTINUITY: #2 turn2 conversation-history STILL excludes #1's content",
          "ORIGINAL_TOPIC" not in cont_hist)

    # (4) NO BACKWARD LEAK: conv #1's persisted turns never carry #2's thread_id.
    in1 = s.store.chats_in_thread(tid1)
    in2 = s.store.chats_in_thread(tid2)
    check("#1's persisted turns all carry tid1, none carry tid2",
          all(t.get("thread_id") == tid1 for t in in1) and len(in1) == 4)   # 2 turns × (user+assistant)
    check("#2's persisted turns all carry tid2",
          all(t.get("thread_id") == tid2 for t in in2) and len(in2) == 4)

    # (6) LIST / REOPEN still works.
    lst = s.list_conversations()
    ids = {r["id"] for r in lst}
    check("list_conversations shows both threads", tid1 in ids and tid2 in ids)
    reopened = s.load_conversation(tid1)
    check("reopen #1 makes it current", s.current_conversation() == tid1)
    check("reopen #1 returns its real history (has ORIGINAL_TOPIC, lacks BRAND_NEW)",
          any("ORIGINAL_TOPIC" in t["text"] for t in reopened["history"])
          and all("BRAND_NEW_QUESTION" not in t["text"] for t in reopened["history"]))

    # reopening #1 then conversing must feed #1's history as REPLAYED TURNS, NOT #2's (the reopen path
    # uses the same fix). Assert on the history slice so the ticker can't confound it.
    CAPTURED.clear()
    s.chat("after_reopen_one", gid)
    reop_hist = joined(history_slice(CAPTURED[-1]))
    check("REOPEN: a turn after reopening #1 feeds #1's turns, not #2's",
          "ORIGINAL_TOPIC" in reop_hist and "BRAND_NEW_QUESTION" not in reop_hist)

    # --- (7) RELOAD-SURVIVAL: a FRESH Suite on the SAME store ---------------------------------
    s2 = fresh_suite(store_dir)
    check("fresh Suite: current pointer is None (in-memory by design)",
          s2.current_conversation() is None)
    lst2 = s2.list_conversations()
    ids2 = {r["id"] for r in lst2}
    check("RELOAD: fresh Suite still lists both threads", tid1 in ids2 and tid2 in ids2)
    reload1 = s2.load_conversation(tid1)
    check("RELOAD: load_conversation(#1) returns #1's turns intact",
          any("ORIGINAL_TOPIC" in t["text"] for t in reload1["history"]))

    # --- (5) LEGACY GLOBAL STREAM (no current thread = back-compat) ---------------------------
    s3 = fresh_suite(os.path.join(tempfile.mkdtemp(prefix="freshstart-legacy-"), "store"))
    check("legacy: no thread current at start", s3.current_conversation() is None)
    CAPTURED.clear()
    s3.chat("LEGACY_first", gid)
    s3.chat("LEGACY_second", gid)
    legacy_in = joined(CAPTURED[-1])
    check("LEGACY: with no thread, the model is fed the GLOBAL stream (sees LEGACY_first)",
          "LEGACY_first" in legacy_in)

    print(f"\nPASS — {PASS} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
