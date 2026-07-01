# ConceptV Vi — UI Kit

The interface for **Vi**, ConceptV's internal AI framework. Vi powers User Portal, Property Wizard, and Virtual Hubs by reading the entities connected to a project (Brand Kit, Master Info, Files, Analytics, …), figuring out what's missing, asking the user for the gaps, and consolidating the result into a finished asset (brochure, landing page, hub config).

## The canonical Vi screen — Vi Workspace

A three-pane layout that mirrors the brochure-flow architecture diagram in `assets/illustrations/vi_brochure_flow.png`:

| Pane | What it shows |
| --- | --- |
| **Left · Conversation** | The user's chat with Vi. Vi shows its work (entities it's reading, fields it's filling, gaps it's flagging). The composer at the bottom lets the user supply missing inputs. |
| **Centre · Task tree** | Vi's three-layer agent architecture, live. Layer 1 plans the task. Layer 2 spawns clones that analyse and break sub-tasks down. Layer 3 executes and saves to file. Matches `assets/illustrations/vi_layers.jpg`. |
| **Right · Output preview** | The asset being built — brochure, hub, or page. Updates in real time as Vi fills sections. |

Vi's brand mark — a **diamond with line-fill** — appears as the avatar everywhere Vi speaks. The "V<sub style="color:#E0C010">i</sub>" wordmark uses a gold subscript "i".

## Components

| File | What it is |
| --- | --- |
| `ViMark.jsx` | The diamond avatar — at any size, optional pulsing-line-fill animation while thinking |
| `ViStatusPill.jsx` | Small inline pill — "Vi is reading Brand Kit…", "Vi found 2 missing fields" — works inside any surface |
| `ChatPanel.jsx` | The left conversation panel. Renders user + Vi messages, entity-read cards, missing-field prompts, approvals |
| `TaskTree.jsx` | The centre layer visualisation — Layer 1 / 2 / 3 with live task nodes |
| `OutputPreview.jsx` | The right brochure preview |
| `App.jsx` | Composes the three panes inside the ConceptV shell |

## Demo

`index.html` opens **Vi Workspace** mid-task: Vi is building a brochure for the "Tower East" project, has read Brand Kit + Master Info, has identified two missing fields, and is asking the user about pricing.

- Press **Continue** in the chat to send the next user message and watch the task tree advance + the brochure preview fill in.
- Press **Reset** to replay from the start.
