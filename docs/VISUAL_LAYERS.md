# DDFramework — layer visuals

This page collects **diagrams** for the engine stack: five layers, kernel
boundary, data/control paths, and governance. Use it before structural
changes.

**Visio:** this repository does not ship `.vsdx` (binary format). You can:

1. **Import SVG** — open [`images/ddf-layers-stack.svg`](./images/ddf-layers-stack.svg) in Visio (**Insert → Pictures** from file) or **Inkscape**, then ungroup/edit.
2. **Copy Mermaid** — paste into [Mermaid Live Editor](https://mermaid.live), export **SVG** or **PNG**, then import into Visio.
3. **GitHub / VS Code** — render this Markdown natively where Mermaid is enabled.

**Mechanical names:** see [`../GLOSSARY_ENGINE_NAMES.md`](../GLOSSARY_ENGINE_NAMES.md).

---

## 1. Five engine layers (what “is” DDFramework)

Per [`DDFRAMEWORK.md`](../DDFRAMEWORK.md): Phantom, Constellation, GHOST,
Hyperion, Ledger — together they *are* the engine.

```mermaid
flowchart TB
  subgraph engine["DDFramework engine"]
    C["Constellation\n(CONSTELLATION.md + constellation.toml)\nconstitutional law"]
    P["Phantom\n(phantom-core / phantom)\nritual executor — sole writer → main ledger"]
    G["GHOST\n(ghost-observer)\nread-only advisor — writer → advisory stream only"]
    H["Hyperion\n(hyperion-net)\ntransport skeleton"]
    L["Ledger\nledger/events.jsonl + advisories/stream.jsonl\ntruth substrate"]
  end
  C -.->|binds| P
  C -.->|binds| G
  P -->|append| L
  G -->|append advisories| L
  H -.->|carries ritual traffic only| P
```

**Write boundaries (critical):**

- **Main ledger** (`ledger/events.jsonl`): **Phantom only**.
- **Advisory stream** (`advisories/stream.jsonl`): **GHOST only**.
- **Hyperion:** transport only; no sovereign ritual side effects alone.

---

## 2. Kernel boundary (Application Era → `ddf-core` → internals)

```mermaid
flowchart TB
  subgraph apps["Application Era v5.0.0+"]
    A1[Shrike Monitor]
    A2[Phantom Orchestrator]
    A3[Other DRKNRTH apps]
  end
  subgraph kernel["ddf-core — stable kernel API"]
    K1["ddf Rust crate + ddf binary"]
    K2["ddf_py Python package"]
    K3["simulation/ Phase 6 stubs"]
  end
  subgraph internal["Engine internals — refactorable"]
    I1[phantom-core]
    I2[ghost-observer]
    I3[hyperion-net]
    I4["ledger/ + advisories/"]
    I5[doctrine.toml + constellation.toml]
  end
  apps -->|depends on| kernel
  kernel -->|dispatches / re-exports| internal
```

---

## 3. Nested stack (operator mental model from ARCHITECTURE)

GHOST “wraps” the fabric; fabric wraps Phantom — **read path** from
outside in; **writes** still follow Phantom/GHOST rules above.

```mermaid
flowchart TB
  GHOST["GHOST — observer, rules R001–R007\nwrites: advisories only"]
  HYP["Hyperion — routing / continuity\nno sovereign writes"]
  PH["Phantom — rituals + invariants\nwrites: main ledger"]
  OP["Operator / CLI / CI"]
  GHOST --> HYP
  HYP --> PH
  PH -->|"append events"| LEDGER[("Main ledger\nread-only for GHOST")]
  GHOST -->|"read tail"| LEDGER
  GHOST -->|"append"| ADV[("Advisory stream")]
  OP -->|"invoke rituals"| PH
  OP -->|"invoke advise"| GHOST
```

---

## 4. Control flow vs data flow (one ritual)

```mermaid
sequenceDiagram
  participant O as Operator
  participant D as ddf / phantom CLI
  participant P as Phantom ritual executor
  participant L as Main ledger file
  participant G as GHOST advisor
  participant A as Advisory stream
  O->>D: verify / amend / …
  D->>P: subprocess or in-process
  P->>P: I6 doctrine hash check
  P->>L: pre-write intent entry I7
  P->>P: side effect e.g. checks
  P->>L: result entry
  Note over G,A: async / separate invocation
  O->>G: advise
  G->>L: read-only
  G->>A: append advisory
```

---

## 5. ASCII — five layers + kernel (print / email friendly)

```
                    ┌─────────────────────────────┐
                    │   Applications (v5+)      │
                    │   depend on ddf API only  │
                    └──────────────┬────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │  ddf-core (kernel)        │
                    │  ddf bin / ddf crate /    │
                    │  ddf_py                    │
                    └──────────────┬────────────┘
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
┌────────▼────────┐       ┌─────────▼─────────┐       ┌────────▼────────┐
│  Constellation  │       │     Phantom      │       │     GHOST       │
│  constitution   │       │  ritual executor │       │  read-only     │
│  (prose + TOML) │       │  main ledger ✎  │       │  advisor ✎ adv  │
└────────┬────────┘       └─────────┬─────────┘       └────────┬────────┘
         │                          │                          │
         │                 ┌────────▼────────┐                 │
         │                 │    Hyperion     │                 │
         │                 │  transport C/R  │                 │
         │                 └────────┬────────┘                 │
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    │
                    ┌───────────────▼────────────────┐
                    │  Ledger (truth substrate)      │
                    │  events.jsonl | stream.jsonl   │
                    └────────────────────────────────┘

  ✎ = sole append authority for that file family (I1, I7, I8)
```

---

## 6. Stocks and flows (Meadows, simplified)

```mermaid
flowchart LR
  subgraph stocks["Stocks (slow-changing state)"]
    S1[Doctrine + constellation]
    S2[Ritual registry ceremonies]
    S3[Main ledger head]
    S4[Advisory stream head]
    S5[Source tree + blobs]
  end
  subgraph flows["Flows"]
    F1[operator intent]
    F2[ritual execution]
    F3[advisor run]
  end
  F1 --> F2
  F2 --> S3
  F3 --> S4
  S1 --> F2
  S2 --> F2
  S3 --> F3
```

---

## Files in this visual pack

| File | Purpose |
|------|---------|
| This Markdown | Mermaid + ASCII; version with repo |
| [`images/ddf-layers-stack.svg`](./images/ddf-layers-stack.svg) | Single-page stack; import into Visio / slides |

If you want a second SVG (sequence-style or governance-only), open an
issue or extend this folder under the same linking rule from
[`README.md`](../README.md).
