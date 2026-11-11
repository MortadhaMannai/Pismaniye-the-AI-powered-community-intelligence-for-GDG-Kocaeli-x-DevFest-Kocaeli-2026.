# PISMANIYE — System Architecture & Agentic Engineering Blueprint

> **Author & Principal Architect:** [Mortadha Mannai (@MortadhaMannai)](https://github.com/MortadhaMannai)
> **Community:** GDG Kocaeli & DevFest Kocaeli 2026
> **Tagline:** *"Unraveling People. Connecting Possibilities."*

---

## 1. High-Level Multi-Agent System Architecture

```mermaid
flowchart TD
    subgraph Clients["Dual User Interfaces"]
        CLI["Cinematic CLI (Typer + Rich Live + Textual TUI)"]
        WEB["Mobile-First Web App & Organizer Dashboard (SPA + QR)"]
    end

    subgraph Gateway["Shared Application & Telemetry Layer"]
        FASTAPI["FastAPI REST + QR + RBAC Server (`pismaniye/api/app.py`)"]
        OTEL["OpenTelemetry Span Tracer & Live Event Bus (`pismaniye/adapters/telemetry.py`)"]
    end

    subgraph Orchestrator["Stateful Multi-Agent Orchestrator (`pismaniye/orchestration/graph.py`)"]
        SUP["◈ Supervisor Router Node"]
        EA["◆ Event Agent"]
        PA["● People Agent"]
        MA["♾ Matchmaker Agent"]
        KA["▲ Knowledge Agent"]
        KOC["✦ Kocaeli Agent"]
        CA["⬢ Community Agent"]
        XAI["⚖ XAI Auditor Node"]
        SYN["✦ Grounded Synthesizer Node"]
    end

    subgraph TrustAndData["Trust, Privacy, RAG & Cloud Adapters"]
        PRIV["🛡 PrivacyGuard (Opt-In Filter + PII Redaction + Consent Gate)"]
        RAG["📚 HybridRAGEngine (Dense Cosine + Lexical/Tag Scoring)"]
        GENAI["Google GenAI SDK / Vertex AI / Deterministic Local Engine"]
        REPO["PismaniyeRepository (Firestore / GCS / Local JSON State)"]
    end

    CLI --> Orchestrator
    CLI --> FASTAPI
    WEB --> FASTAPI
    FASTAPI --> Orchestrator
    Orchestrator --> OTEL
    SUP --> EA & PA & MA & KA & KOC & CA
    EA & PA & MA & KA & KOC & CA --> XAI
    XAI --> SYN
    EA & PA & MA & KA & KOC & CA --> PRIV
    PRIV --> RAG
    PRIV --> REPO
    RAG --> GENAI
    SYN --> GENAI
```

---

## 2. LangGraph Stateful Execution Graph (`StateGraph`)

Pismaniye uses an explicit `langgraph.graph.StateGraph` (`OrchestrationGraphState`) where the `Supervisor Router` classifies user intent and dynamically sequences the required specialist nodes before mandatory verification by the `XAI Auditor`:

```mermaid
stateDiagram-v2
    [*] --> supervisor_node
    supervisor_node --> people_agent_node: Workflow A (Meet Expert)
    people_agent_node --> matchmaker_agent_node: Score Compatibility & Stage Consent
    matchmaker_agent_node --> knowledge_agent_node: Retrieve Grounded Bios & Talks

    supervisor_node --> event_agent_node: Workflow B (My DevFest Day)
    event_agent_node --> knowledge_agent_node: Resolve Conflicts & Cite Sessions

    supervisor_node --> kocaeli_agent_node: Workflow C (Discover Kocaeli)
    kocaeli_agent_node --> knowledge_agent_node: Time-Budget + Transit Verification

    supervisor_node --> community_agent_node: Workflow D (Community Knowledge)
    community_agent_node --> event_agent_node: Map Talks to Learning Stages

    knowledge_agent_node --> xai_auditor_node: Audit Citations, Factors & Privacy
    xai_auditor_node --> synthesize_node: Emit DecisionExplanation & Redact PII
    synthesize_node --> [*]
```

---

## 3. Sequence Diagrams of the 4 Signature Agentic Workflows

### Workflow A — Meet the Right Expert (Consent-Gated Matchmaking)
```mermaid
sequenceDiagram
    actor User as Attendee / Speaker
    participant Sup as ◈ Supervisor
    participant PPL as ● People Agent
    participant MM as ♾ Matchmaker Agent
    participant RAG as ▲ Knowledge Agent
    participant XAI as ⚖ XAI Auditor
    participant Repo as 🛡 Privacy & Repository

    User->>Sup: "I'm interested in Agentic AI, Gemini, and production AI systems. Who should I meet?"
    Sup->>PPL: Route to People Agent (interests=["Agentic AI", "Gemini", "production AI systems"])
    PPL->>Repo: list_discoverable_people() (Excludes PRIVATE & opted-out profiles)
    Repo-->>PPL: Opt-in profiles sanitized (No email/phone)
    PPL->>MM: Pass candidate pool
    MM->>MM: Score (0.40*overlap + 0.35*complementarity + 0.25*mentorship)
    MM->>Repo: create_introduction_request(status=PENDING_REQUESTER_CONSENT)
    MM->>RAG: Retrieve speaker talk abstracts & bio chunks
    RAG->>XAI: Pass steps, tool calls, citations & factor breakdowns
    XAI->>Repo: Persist TraceRecord (`trc-*`) & DecisionExplanation (`dec-*`)
    XAI-->>User: Ranked matches + Why Meet + Icebreaker + Explicit Consent Prompt
```

### Workflow B — My DevFest Day (Conflict-Free Schedule Builder)
```mermaid
sequenceDiagram
    actor User as Attendee
    participant Sup as ◈ Supervisor
    participant EVT as ◆ Event Agent
    participant RAG as ▲ Knowledge Agent
    participant XAI as ⚖ XAI Auditor

    User->>Sup: "Create my ideal DevFest agenda. I'm interested in Google Cloud and AI."
    Sup->>EVT: Route to Event Agent
    EVT->>EVT: Score all sessions by topic alignment & format weight
    EVT->>EVT: Group by time slot & detect 11:15-12:00 parallel track conflict
    EVT->>EVT: Select higher-scoring session & document conflict resolution reason
    EVT->>RAG: Retrieve grounded session abstracts & venue room logistics
    RAG->>XAI: Audit scoring breakdowns & provenance chain
    XAI-->>User: Conflict-free chronological agenda + selection rationale
```

### Workflow C — Discover Kocaeli (Time-Boxed Local Concierge)
```mermaid
sequenceDiagram
    actor User as Visiting GDE / Speaker
    participant Sup as ◈ Supervisor
    participant KOC as ✦ Kocaeli Agent
    participant RAG as ▲ Knowledge Agent
    participant XAI as ⚖ XAI Auditor

    User->>Sup: "I'm a visiting GDE. I have three free hours. Help me discover Kocaeli."
    Sup->>KOC: Route to Kocaeli Agent (hours=3.0 -> 180 min budget)
    KOC->>KOC: Reserve 15m venue return buffer (165m usable window)
    KOC->>KOC: Evaluate transit_minutes + visit_duration_minutes & opening hours
    KOC->>KOC: Select Sekapark (70m) + İzmit Clock Tower (60m) = 145m total; defer Ormanya (220m)
    KOC->>RAG: Cite local cultural & heritage documents
    RAG->>XAI: Audit time-budget fit & verification status
    XAI-->>User: Practical 3-hour itinerary + deferred longer excursions
```

### Workflow D — Community Knowledge (Post-DevFest Learning Path)
```mermaid
sequenceDiagram
    actor User as Developer
    participant Sup as ◈ Supervisor
    participant COM as ⬢ Community Agent
    participant EVT as ◆ Event Agent
    participant RAG as ▲ Knowledge Agent
    participant XAI as ⚖ XAI Auditor

    User->>Sup: "I want to start learning Agentic AI after DevFest."
    Sup->>COM: Route to Community Agent
    COM->>COM: Assemble 4-stage pathway (Foundations -> Study Jam -> RAG Archive -> CFP Incubator)
    COM->>EVT: Cross-reference related DevFest sessions & workshops
    EVT->>RAG: Retrieve verified resource URLs & contribution guides
    RAG->>XAI: Audit learning path citations & provenance
    XAI-->>User: Structured multi-stage learning roadmap + GDG Kocaeli contribution steps
```

---

## 4. Trust, Privacy & Data Provenance Architecture

```mermaid
flowchart LR
    subgraph Input["Raw Profile / Document"]
        RAW["PersonProfile (includes private_email, private_phone, opt_in_networking)"]
    end

    subgraph Guard["PrivacyGuard (`pismaniye/privacy/guardrails.py`)"]
        OPT["1. Opt-In & Visibility Check (`opt_in_networking == True` & `visibility != PRIVATE`)"]
        SER["2. Schema Exclusion (`exclude={'private_email', 'private_phone'}`)"]
        REG["3. Output Regex PII Redactor (`[REDACTED-EMAIL-CONSENT-REQUIRED]`)"]
        CON["4. Consent Gate (`PENDING_REQUESTER_CONSENT` -> `APPROVED_AND_LOGGED`)"]
    end

    subgraph Audit["XAI & Immutable Audit Log"]
        BADGE["Verification Badge (`SYNTHETIC_SAMPLE` | `VERIFIED_ORGANIZER_DATA` | `GENERATED_SUGGESTION`)"]
        LOG["AuditLogEntry + Right-to-Erasure (`DELETE /api/privacy/profile/{id}`)"]
    end

    RAW --> OPT --> SER --> REG --> CON --> BADGE --> LOG
```
