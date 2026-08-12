# Diagramas Mermaid — CreaBits Tutor (System Design & Prompt Composition)

Fuente Mermaid de las cuatro figuras del `.tex`. Pégalo en cualquier visor Mermaid
(mermaid.live, GitHub, Notion, VS Code) para verlo o exportarlo a PNG/SVG.
Las mismas figuras están implementadas en TikZ dentro de `conference_101719 (1).tex`.

---

## Fig. 1 — Runtime architecture (`fig:arch`)

```mermaid
flowchart LR
    child["Child<br/>(web browser)"]
    spa["React SPA (Vite)<br/>5-screen state machine<br/>typed API client"]

    subgraph BE["FastAPI back end"]
        direction TB
        routes["Routes /api/v1"] --> svc["Services<br/>(tutoring logic)"]
        svc --> repo["Repositories<br/>(data access)"]
        repo --> model["Models<br/>(async SQLAlchemy)"]
    end

    db[("PostgreSQL / SQLite")]

    factory["LLM factory<br/>(by LLM_MODE)"]
    gem["Gemini 2.5 Flash"]
    mock["Mock (development)"]
    orr["OpenRouter"]

    child --> spa
    spa -- "HTTPS / JSON<br/>nginx proxy /api/" --> routes
    model --> db
    svc --> factory
    factory --> gem
    factory --> mock
    factory --> orr
```

---

## Fig. 2 — Prompt composition and reply flow (`fig:prompt`)

```mermaid
flowchart TB
    subgraph SYS["System instruction (assembled per request)"]
        direction TB
        L1["L1 - Static pedagogical base (every turn)<br/>persona Bit; four-phase policy<br/>predict / hint / confirm / respond;<br/>progressive-hint, block, reply-option rules"]
        L2["L2 - Dynamic exercise context (per exercise)<br/>title, instruction, objectives, hints;<br/>PRIVATE: reference solution + key-block ids"]
        L3["L3 - Block catalog (every turn)<br/>47 blocks: id, name, description"]
        L1 --- L2 --- L3
    end

    turn["User turn<br/>rolling transcript (last 14 messages)<br/>+ new child message"]
    llm["LLM (Gemini 2.5 Flash)<br/>native structured output (response_schema)"]
    json["Typed reply<br/>respuesta, fase, bloques_sugeridos,<br/>opciones_respuesta, necesita_aclaracion,<br/>razonamiento_pedagogico"]
    val["Validation<br/>drop block ids absent from catalog;<br/>de-duplicate + cap options at 3"]
    ui["Interface<br/>message + phase badge<br/>+ block cards + reply-option buttons"]

    SYS --> turn --> llm --> json --> val --> ui
```

---

## Fig. 3 — Interaction phases (`fig:phases`)

```mermaid
stateDiagram-v2
    [*] --> respond
    respond --> predict: asks for help
    predict --> hint: tried, stuck
    hint --> hint: escalate (1 -> 2 -> 3)
    predict --> confirm: reasons well
    hint --> confirm: reasons well
    confirm --> respond: block placed / next
    respond --> respond: casual / factual
```

---

## Fig. 4 — Message exchange for one turn (`fig:sequence`)

```mermaid
sequenceDiagram
    autonumber
    participant C as Child
    participant F as Front end
    participant B as Back end
    participant M as Model

    C->>F: tap option / type message
    F->>B: POST /conversations/{id}/messages
    B->>B: persist child message + assemble layered prompt
    B->>M: system instruction + transcript + new message
    M-->>B: structured JSON reply
    B->>B: validate blocks vs catalog + store (phase, tokens)
    B-->>F: reply + phase + block cards + options
    F-->>C: render tutor turn
```
