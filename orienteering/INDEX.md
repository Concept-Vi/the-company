---
type: terrain-index
register: descriptive
aliases: ["Orienteering Index"]
tags: [company, orienteering, moc, knowledge-space]
status: unconfirmed
coverage: { files_read: all, files_total: all, last_read: 2026-06-26 }
relates-to: ["[[Company Map]]", "[[orienteering — constitution]]", "[[Vault Conventions]]"]
part-of: ["[[company]]"]
---

# Orienteering Index — the Company's terrain

The region sub-map of `orienteering/` (linked from [[Company Map]], the one vault home — this is **not** a competing home). One `terrain-entry` per thing in the Company's orbit: what it is, where it physically lives, what it connects to, and how much was actually read. Schema + rules: [[orienteering — constitution]] / [[Vault Conventions]]. **Descriptive, not a blueprint.** `status` is `unconfirmed` until Tim confirms a lifecycle.

The table below is **generated from entry frontmatter** (the single source — do not hand-maintain a parallel list).

## company
| Entry | kind | status | size | last_read | path |
|---|---|---|---|---|---|
| [[company]] |  | unconfirmed | 5.6G | 2026-06-26 | `/home/tim/company` |

## external
| Entry | kind | status | size | last_read | path |
|---|---|---|---|---|---|
| [[CosyVoice]] | engine | unconfirmed | 5.3G | 2026-06-26 | `/home/tim/CosyVoice` |
| [[actions-runner]] | engine | unconfirmed | 1.8G | 2026-06-26 | `/home/tim/actions-runner` |
| [[artefacts]] | work | unconfirmed | 108K | 2026-06-26 | `/home/tim/artefacts` |
| [[build-coordination-docs]] | work | unconfirmed | 76K (6 files) | 2026-06-26 | `/home/tim` |
| [[cache-company]] | data | unconfirmed | 1.6G | 2026-06-26 | `/home/tim/.cache/company/substrate-claude-sessions` |
| [[channel-test]] | config | unconfirmed | 8K | 2026-06-26 | `/home/tim/channel-test` |
| [[company-cli]] | engine | unconfirmed | symlink (29 bytes) → in-repo body | 2026-06-26 | `/home/tim/.local/bin/company` |
| [[company-scan]] | work | unconfirmed | 9.4M | 2026-06-26 | `/home/tim/company-scan` |
| [[company-systemd]] | config | unconfirmed | small (unit files) | 2026-06-26 | `/home/tim/.config/systemd/user` |
| [[config-company]] | config | unconfirmed | 20K | 2026-06-26 | `/home/tim/.config/company` |
| [[corpora]] | data | unconfirmed | 93M | 2026-06-26 | `/home/tim/corpora` |
| [[dot-recollection]] | data | unconfirmed | 1.2G | 2026-06-26 | `/home/tim/company/.recollection` |
| [[dot-vi]] | config | unconfirmed | 224K | 2026-06-26 | `/home/tim/.vi` |
| [[foundation]] | data | unconfirmed | 756K | 2026-06-26 | `/home/tim/company/foundation` |
| [[jina-v4-env]] | engine | unconfirmed | 5.0G | 2026-06-26 | `/home/tim/jina-v4-env` |
| [[llama-swap]] | engine | unconfirmed | 8K | 2026-06-26 | `/home/tim/llama-swap` |
| [[mcp-mining]] | work | unconfirmed | 59M | 2026-06-26 | `/home/tim/mcp-mining` |
| [[recollection]] | engine | unconfirmed | 1.1G | 2026-06-26 | `/home/tim/company/recollection` |
| [[vllm-env]] | engine | unconfirmed | 8.4G | 2026-06-26 | `/home/tim/vllm-env` |
| [[vllm-tests]] | engine | unconfirmed | 1.3M | 2026-06-26 | `/home/tim/vllm-tests` |
| [[voice-venvs]] | engine | unconfirmed | 48G | 2026-06-26 | `/home/tim/.voice-venvs` |
| [[voicemode]] | engine | unconfirmed | 2.9G | 2026-06-26 | `/home/tim/.voicemode` |
| [[wizard-run-1]] | work | unconfirmed | 59M | 2026-06-26 | `/home/tim/company/migration-pending/wizard-run-1` |

## connected
| Entry | kind | status | size | last_read | path |
|---|---|---|---|---|---|
| [[counterpart]] | work | unconfirmed | 920M | 2026-06-26 | `/home/tim/repos/counterpart` |
| [[obsidian-overlord]] | engine | unconfirmed | 9.2G | 2026-06-26 | `/home/tim/repos/obsidian-overlord` |
| [[openwebui-venv]] | engine | unconfirmed | 6.8G | 2026-06-26 | `/home/tim/openwebui-venv` |
| [[vi-visual-bridge]] | work | unconfirmed | 1.3G | 2026-06-26 | `/home/tim/vi-visual-bridge` |

## candidate
| Entry | kind | status | size | last_read | path |
|---|---|---|---|---|---|
| [[comfyui-data]] |  | unconfirmed | 36G | 2026-06-26 | `/home/tim/comfyui-data` |
| [[comfyui]] |  | unconfirmed | 636M | 2026-06-26 | `/home/tim/ComfyUI` |
| [[kohya_ss]] |  | unconfirmed | 11G | 2026-06-26 | `/home/tim/kohya_ss` |

## resource
| Entry | kind | status | size | last_read | path |
|---|---|---|---|---|---|
| [[ai-systems-strategic-overview]] | data | unconfirmed | 60K | 2026-06-26 | `/home/tim/ai-systems-strategic-overview` |
| [[cognitive-framework]] | data | unconfirmed | 27M | 2026-06-26 | `/home/tim/.cognitive_framework` |
| [[creations]] | work | unconfirmed | 112K | 2026-06-26 | `/home/tim/creations` |
| [[docs]] | data | unconfirmed | 2.8M | 2026-06-26 | `/home/tim/docs` |
| [[graph-editor]] | work | unconfirmed | 423M | 2026-06-26 | `/home/tim/repos/graph-editor` |
| [[universal-mechanics]] | data | unconfirmed | 89M | 2026-06-26 | `/home/tim/universal-mechanics` |
| [[world-keeper-profile]] | data | unconfirmed | 32K | 2026-06-26 | `/home/tim/world_keeper_profile` |

## Counts by relation
- company: 1
- external: 23
- connected: 4
- candidate: 3
- resource: 7

## Live queries (light up when a renderer attaches; the table above works without one)
```dataview
TABLE relation, kind, status, register, coverage.last_read AS "last read"
FROM "orienteering/entries"
SORT relation ASC, kind ASC
```
