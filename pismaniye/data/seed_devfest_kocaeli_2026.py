"""Clearly labeled fictional sample dataset for DevFest Kocaeli 2026 & GDG Kocaeli.

IMPORTANT NOTICE:
All speakers, GDEs, organizers, attendees, session times, and venue rooms in this file
are FICTIONAL SAMPLE DATA (`VerificationStatus.SYNTHETIC_SAMPLE`) created to demonstrate
Pismaniye's multi-agent architecture until GDG Kocaeli organizers import verified records.
"""

from __future__ import annotations

from pismaniye.schemas.domain import (
    CommunityResource,
    EventEditionConfig,
    EventSession,
    KnowledgeDocument,
    KocaeliPlace,
    PersonProfile,
    ProfileVisibility,
    RoleType,
    SessionFormat,
    VenueInfo,
    VerificationStatus,
)


def get_seed_edition_config(event_id: str = "devfest-kocaeli-2026") -> EventEditionConfig:
    return EventEditionConfig(
        event_id=event_id,
        event_name="DevFest Kocaeli 2026 (Sample Edition)",
        edition_year=2026,
        community_name="GDG Kocaeli",
        tagline="Unraveling People. Connecting Possibilities.",
        date_display="Saturday, November 2026 • Sample Demonstration Schedule (Unverified)",
        is_sample_data=True,
    )


def get_seed_venue(event_id: str = "devfest-kocaeli-2026") -> VenueInfo:
    return VenueInfo(
        event_id=event_id,
        venue_name="[SAMPLE VENUE] Kocaeli Congress & Innovation Center (Fictional Demo Layout)",
        city="Kocaeli (İzmit)",
        address_note=(
            "SAMPLE LOGISTICS DATA — Placeholder waterfront tramway corridor in İzmit, Kocaeli. "
            "Organizers must update exact street address in the Organizer Dashboard before publishing."
        ),
        rooms=[
            "Main Hall — Pişmaniye Stage (Keynotes & Flagship AI Track)",
            "Hall B — Gulf Cloud & Platform Track",
            "Workshop Lab 1 — Hands-On Gemini & ADK Codelab Room",
            "Community Lounge — GDE Office Hours & Matchmaker Corner",
        ],
        wifi_ssid="GDG-Kocaeli-2026-SampleNet",
        accessibility_notes=[
            "Step-free elevator access to all stages and Workshop Lab 1 (Sample layout).",
            "Live captions enabled on Main Hall screens.",
            "Quiet room available adjacent to Community Lounge.",
        ],
        transport_notes=[
            "Accessible via Akçaray Tramway (Sample stop: Congress Center) and İzmit intercity bus shuttle.",
            "YHT High-Speed Train connects Istanbul Söğütlüçeşme / Pendik to İzmit Central Station (~45–60 min).",
        ],
        emergency_and_code_of_conduct=(
            "GDG Kocaeli enforces a strict Harassment-Free Community Code of Conduct. "
            "All networking introductions require mutual opt-in and explicit consent."
        ),
        verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
    )


def get_seed_people() -> list[PersonProfile]:
    """Return fictional sample speakers, GDEs, organizers, and opt-in/private attendees."""
    return [
        PersonProfile(
            id="spk-selin-kaya-sample",
            full_name="Dr. Selin Kaya [Sample GDE]",
            role=RoleType.GDE,
            headline="Google Developer Expert in Cloud AI & Multi-Agent Architectures (Fictional Sample)",
            organization="Anatolia AI Labs (Sample)",
            gde_category="Google Cloud & Machine Learning",
            country="Türkiye",
            bio=(
                "[SYNTHETIC SAMPLE BIO] Fictional Google Developer Expert specializing in Agentic AI, "
                "Gemini 2.5 production systems, LangGraph state machines, and Google ADK orchestration "
                "on Cloud Run and Vertex AI. Frequent mentor for developer communities across Marmara."
            ),
            interests=["Agentic AI", "Gemini", "production AI systems", "LangGraph", "Google ADK", "Evaluation"],
            expertise_tags=["Agentic AI", "Gemini", "Google Cloud", "LangGraph", "Google ADK", "Vertex AI", "RAG"],
            technologies=["Gemini", "Google ADK", "LangGraph", "Vertex AI", "Cloud Run", "OpenTelemetry", "Python"],
            looking_for=[
                "Engineers building production AI systems",
                "Contributors to open-source agent evaluation benchmarks",
                "GDG study jam facilitators",
            ],
            can_mentor_on=[
                "Designing deterministic + LLM hybrid multi-agent workflows",
                "Production observability and OpenTelemetry tracing for Gemini agents",
                "Becoming a Google Developer Expert (GDE)",
            ],
            speaking_session_ids=["sess-keynote-agentic", "sess-workshop-adk"],
            languages=["Turkish", "English"],
            visibility=ProfileVisibility.PUBLIC,
            opt_in_networking=True,
            opt_in_matchmaker=True,
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
            private_email="selin.sample.private@example.invalid",
            private_phone="+90-555-010-0001",
        ),
        PersonProfile(
            id="spk-lukas-weber-sample",
            full_name="Lukas Weber [Sample International Speaker]",
            role=RoleType.GDE,
            headline="Principal Distributed Systems & Vertex AI Architect (Fictional Sample GDE)",
            organization="RhineCloud Systems Munich (Sample)",
            gde_category="Google Cloud",
            country="Germany",
            bio=(
                "[SYNTHETIC SAMPLE BIO] Fictional visiting international GDE from Munich focusing on "
                "high-throughput production AI systems, Firestore vector & operational state, Cloud Run "
                "autoscaling, and zero-trust guardrails for enterprise Gemini deployments."
            ),
            interests=["production AI systems", "Google Cloud", "Gemini", "SRE", "Cloud Run", "Firestore"],
            expertise_tags=["Google Cloud", "production AI systems", "Cloud Run", "Vertex AI", "Firestore", "SRE"],
            technologies=["Google Cloud", "Cloud Run", "Firestore", "Vertex AI", "Terraform", "Go", "Python"],
            looking_for=[
                "Local architects scaling Cloud Run & Vertex AI workloads",
                "Recommendations for discovering Kocaeli culture and local cuisine",
            ],
            can_mentor_on=[
                "Production AI latency budgets, caching, and SLO design on Google Cloud",
                "Multi-region Cloud Run + Firestore architectures",
            ],
            speaking_session_ids=["sess-prod-ai-cloudrun", "sess-panel-gde"],
            languages=["English", "German"],
            visibility=ProfileVisibility.PUBLIC,
            opt_in_networking=True,
            opt_in_matchmaker=True,
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
            private_email="lukas.sample.private@example.invalid",
            private_phone="+49-151-010-0002",
        ),
        PersonProfile(
            id="spk-emre-demir-sample",
            full_name="Emre Demir [Sample Speaker]",
            role=RoleType.SPEAKER,
            headline="Staff AI Platform Engineer & RAG Systems Lead (Fictional Sample)",
            organization="Kocaeli FinTech Collective (Sample)",
            gde_category=None,
            country="Türkiye",
            bio=(
                "[SYNTHETIC SAMPLE BIO] Fictional Staff Engineer based in Kocaeli building grounded RAG "
                "pipelines, Explainable AI (XAI) auditing tools, and hybrid search over Turkish and English "
                "technical corpora using Vertex AI Embeddings and LangGraph."
            ),
            interests=["Agentic AI", "RAG", "Explainable AI", "LangGraph", "Gemini", "production AI systems"],
            expertise_tags=["RAG", "Explainable AI", "LangGraph", "Vertex AI Embeddings", "Agentic AI", "Python"],
            technologies=["LangGraph", "Vertex AI", "Gemini", "FastAPI", "Pydantic", "OpenTelemetry"],
            looking_for=[
                "Developers interested in RAG evaluation and citation grounding",
                "Local Kocaeli engineers for monthly AI Architecture study jams",
            ],
            can_mentor_on=[
                "Hybrid vector + lexical RAG chunking strategies",
                "Building XAI decision provenance for regulated AI systems",
            ],
            speaking_session_ids=["sess-hybrid-rag-xai"],
            languages=["Turkish", "English"],
            visibility=ProfileVisibility.PUBLIC,
            opt_in_networking=True,
            opt_in_matchmaker=True,
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
            private_email="emre.sample.private@example.invalid",
            private_phone="+90-555-010-0003",
        ),
        PersonProfile(
            id="org-zeynep-yildiz-sample",
            full_name="Zeynep Yıldız [Sample GDG Organizer]",
            role=RoleType.ORGANIZER,
            headline="GDG Kocaeli Lead Organizer & Developer Ecosystem Builder (Fictional Sample)",
            organization="GDG Kocaeli (Sample Persona)",
            gde_category=None,
            country="Türkiye",
            bio=(
                "[SYNTHETIC SAMPLE BIO] Fictional Lead Organizer persona for GDG Kocaeli. Coordinates "
                "DevFest Kocaeli, Women Techmakers initiatives, Build with AI study jams, and university "
                "developer bridges across Kocaeli University and Gebze Technical University ecosystems."
            ),
            interests=["Community Building", "Agentic AI", "Google Cloud", "Mentorship", "Open Source", "Kocaeli Ecosystem"],
            expertise_tags=["Community Leadership", "Developer Relations", "Google Cloud", "Study Jams", "Public Speaking"],
            technologies=["Google Cloud", "Gemini", "Firebase", "Flutter", "Python"],
            looking_for=[
                "First-time speakers for upcoming GDG Kocaeli meetups",
                "Volunteers and mentors for Post-DevFest Agentic AI Study Jams",
                "Visiting GDEs interested in mentoring local student clubs",
            ],
            can_mentor_on=[
                "Submitting your first CFP to GDG Kocaeli",
                "Navigating the Kocaeli technopark and university developer ecosystem",
            ],
            speaking_session_ids=["sess-opening-welcome", "sess-panel-gde"],
            languages=["Turkish", "English"],
            visibility=ProfileVisibility.PUBLIC,
            opt_in_networking=True,
            opt_in_matchmaker=True,
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
            private_email="zeynep.sample.private@example.invalid",
            private_phone="+90-555-010-0004",
        ),
        PersonProfile(
            id="spk-arda-cetinkaya-sample",
            full_name="Arda Çetinkaya [Sample Speaker]",
            role=RoleType.SPEAKER,
            headline="Mobile & On-Device Gemini Nano Engineer (Fictional Sample)",
            organization="Marmara Mobility Studio (Sample)",
            gde_category="Android & Flutter",
            country="Türkiye",
            bio=(
                "[SYNTHETIC SAMPLE BIO] Fictional mobile architect integrating multimodal Gemini capabilities "
                "into offline-capable field apps and Flutter experiences."
            ),
            interests=["Flutter", "Android", "Gemini", "On-Device AI", "Mobile UX"],
            expertise_tags=["Flutter", "Android", "Gemini", "Firebase", "Kotlin"],
            technologies=["Flutter", "Kotlin", "Gemini", "Firebase", "Firestore"],
            looking_for=["Backend AI engineers to collaborate on mobile agent interfaces"],
            can_mentor_on=["Streaming agent events to mobile-first interfaces"],
            speaking_session_ids=["sess-mobile-gemini"],
            languages=["Turkish", "English"],
            visibility=ProfileVisibility.PUBLIC,
            opt_in_networking=True,
            opt_in_matchmaker=True,
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
            private_email="arda.sample.private@example.invalid",
            private_phone="+90-555-010-0005",
        ),
        PersonProfile(
            id="att-deniz-aksoy-sample",
            full_name="Deniz Aksoy [Sample Opt-In Attendee]",
            role=RoleType.ATTENDEE,
            headline="Senior Backend Engineer Exploring Agentic AI (Fictional Opt-In Attendee)",
            organization="İzmit Logistics Tech (Sample)",
            gde_category=None,
            country="Türkiye",
            bio=(
                "[SYNTHETIC SAMPLE BIO] Fictional attendee who explicitly opted into the community "
                "directory to connect with peers working on Gemini, LangGraph, and Cloud Run."
            ),
            interests=["Agentic AI", "Gemini", "Python", "Google Cloud", "production AI systems"],
            expertise_tags=["Python", "FastAPI", "PostgreSQL", "Cloud Run", "Docker"],
            technologies=["Python", "FastAPI", "Cloud Run", "Gemini", "LangGraph"],
            looking_for=["Co-learners for the Post-DevFest Agentic AI Study Jam", "GDE mentorship on Vertex AI"],
            can_mentor_on=["FastAPI microservices and containerization"],
            speaking_session_ids=[],
            languages=["Turkish", "English"],
            visibility=ProfileVisibility.OPT_IN_COMMUNITY,
            opt_in_networking=True,
            opt_in_matchmaker=True,
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
            private_email="deniz.sample.private@example.invalid",
            private_phone="+90-555-010-0006",
        ),
        PersonProfile(
            id="att-private-opted-out-sample",
            full_name="Gizli Katılımcı [Sample Opted-Out Private Attendee]",
            role=RoleType.ATTENDEE,
            headline="Stealth Architect (Opted Out of Directory)",
            organization="Private Corp",
            gde_category=None,
            country="Türkiye",
            bio="This attendee has NOT opted into networking. Must never appear in People or Matchmaker results.",
            interests=["Agentic AI", "Gemini", "production AI systems"],
            expertise_tags=["Agentic AI", "Gemini", "Google Cloud"],
            technologies=["Gemini", "Vertex AI"],
            looking_for=[],
            can_mentor_on=[],
            speaking_session_ids=[],
            languages=["Turkish"],
            visibility=ProfileVisibility.PRIVATE,
            opt_in_networking=False,
            opt_in_matchmaker=False,
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
            private_email="never.expose@example.invalid",
            private_phone="+90-555-999-9999",
        ),
    ]


def get_seed_sessions(event_id: str = "devfest-kocaeli-2026") -> list[EventSession]:
    """Return fictional sample DevFest Kocaeli 2026 schedule including parallel tracks to test conflict resolution."""
    return [
        EventSession(
            id="sess-opening-welcome",
            event_id=event_id,
            title="[Sample] Opening Remarks: Unraveling People, Connecting Possibilities in Kocaeli",
            track="Main Stage",
            format=SessionFormat.KEYNOTE,
            level="All Levels",
            start_time="09:30",
            end_time="10:00",
            room="Main Hall — Pişmaniye Stage",
            speaker_ids=["org-zeynep-yildiz-sample"],
            speaker_names=["Zeynep Yıldız [Sample GDG Organizer]"],
            tags=["Community", "GDG Kocaeli", "DevFest", "Keynote"],
            abstract=(
                "[SYNTHETIC SAMPLE SESSION] Welcome to DevFest Kocaeli 2026! Discover how GDG Kocaeli weaves "
                "together local engineering talent, university innovators, and international Google Developer Experts."
            ),
            key_takeaways=[
                "Overview of the Kocaeli developer ecosystem and 2026–2027 community roadmap",
                "How to use the Pismaniye Multi-Agent Concierge responsibly with opt-in networking",
            ],
            prerequisites=[],
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
        ),
        EventSession(
            id="sess-keynote-agentic",
            event_id=event_id,
            title="[Sample Keynote] Architecting Stateful Agentic AI with Gemini, Google ADK & LangGraph",
            track="AI & Agents",
            format=SessionFormat.KEYNOTE,
            level="Intermediate",
            start_time="10:15",
            end_time="11:00",
            room="Main Hall — Pişmaniye Stage",
            speaker_ids=["spk-selin-kaya-sample"],
            speaker_names=["Dr. Selin Kaya [Sample GDE]"],
            tags=["Agentic AI", "Gemini", "Google ADK", "LangGraph", "Google Cloud", "AI"],
            abstract=(
                "[SYNTHETIC SAMPLE SESSION] Deep dive into designing multi-agent platforms that go beyond brittle "
                "prompt chains. Learn how to combine Google GenAI SDK, Google ADK, and LangGraph explicit state "
                "graphs with OpenTelemetry tracing and deterministic testing."
            ),
            key_takeaways=[
                "Explicit state transitions with LangGraph and Google ADK",
                "Observability and explainability (XAI) for multi-agent decisions",
                "Patterns for deterministic offline fallback during live demos",
            ],
            prerequisites=["Basic Python familiarity"],
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
        ),
        EventSession(
            id="sess-prod-ai-cloudrun",
            event_id=event_id,
            title="[Sample Talk] Scaling Production AI Systems on Google Cloud: Cloud Run, Vertex AI & Firestore",
            track="Google Cloud & Platform",
            format=SessionFormat.TECHNICAL_TALK,
            level="Advanced",
            start_time="11:15",
            end_time="12:00",
            room="Hall B — Gulf Cloud & Platform Track",
            speaker_ids=["spk-lukas-weber-sample"],
            speaker_names=["Lukas Weber [Sample International Speaker]"],
            tags=["Google Cloud", "production AI systems", "Cloud Run", "Vertex AI", "Firestore", "AI"],
            abstract=(
                "[SYNTHETIC SAMPLE SESSION] How do you take an AI prototype to production on Google Cloud? "
                "This talk covers latency budgets, Vertex AI embedding pipelines, Firestore state persistence, "
                "and zero-downtime revisions on Cloud Run."
            ),
            key_takeaways=[
                "Production SLOs and tail-latency control for Gemini endpoints",
                "Firestore schema patterns for agent memory and audit trails",
                "Automated CI/CD deployment to Cloud Run",
            ],
            prerequisites=["Cloud architecture fundamentals"],
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
        ),
        EventSession(
            id="sess-mobile-gemini",
            event_id=event_id,
            title="[Sample Talk] Multimodal Mobile Experiences with Flutter & Gemini",
            track="Mobile & Web",
            format=SessionFormat.TECHNICAL_TALK,
            level="Intermediate",
            start_time="11:15",
            end_time="12:00",
            room="Main Hall — Pişmaniye Stage",
            speaker_ids=["spk-arda-cetinkaya-sample"],
            speaker_names=["Arda Çetinkaya [Sample Speaker]"],
            tags=["Flutter", "Mobile", "Gemini", "Android"],
            abstract=(
                "[SYNTHETIC SAMPLE SESSION] Runs in parallel with Hall B at 11:15. Explores building responsive "
                "mobile UIs powered by Gemini multimodal prompts and Firebase."
            ),
            key_takeaways=[
                "Streaming structured JSON outputs to mobile clients",
                "Offline-first UX resilience patterns",
            ],
            prerequisites=["Flutter or Android basics"],
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
        ),
        EventSession(
            id="sess-hybrid-rag-xai",
            event_id=event_id,
            title="[Sample Talk] Grounded Hybrid RAG & Explainable AI (XAI) with Vertex AI Embeddings",
            track="AI & Agents",
            format=SessionFormat.TECHNICAL_TALK,
            level="Intermediate",
            start_time="13:15",
            end_time="14:00",
            room="Main Hall — Pişmaniye Stage",
            speaker_ids=["spk-emre-demir-sample"],
            speaker_names=["Emre Demir [Sample Speaker]"],
            tags=["RAG", "AI", "Vertex AI", "Explainable AI", "Google Cloud", "LangGraph"],
            abstract=(
                "[SYNTHETIC SAMPLE SESSION] Hallucinations erode community trust. Learn how to build a hybrid "
                "vector + lexical retrieval engine backed by Vertex AI `text-embedding-004`, complete with "
                "source citations, epistemic uncertainty scoring, and an XAI Auditor."
            ),
            key_takeaways=[
                "Chunking and metadata enrichment for technical documentation",
                "Distinguishing verified data from synthesized suggestions",
                "Implementing `pismaniye explain <decision_id>` provenance auditing",
            ],
            prerequisites=["Python & vector search basics"],
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
        ),
        EventSession(
            id="sess-workshop-adk",
            event_id=event_id,
            title="[Sample Workshop] Hands-On Lab: Building Your First Multi-Agent Workflow with Gemini & LangGraph",
            track="Workshops",
            format=SessionFormat.WORKSHOP,
            level="Beginner to Intermediate",
            start_time="14:15",
            end_time="15:45",
            room="Workshop Lab 1 — Hands-On Gemini & ADK Codelab Room",
            speaker_ids=["spk-selin-kaya-sample", "spk-emre-demir-sample"],
            speaker_names=["Dr. Selin Kaya [Sample GDE]", "Emre Demir [Sample Speaker]"],
            tags=["Agentic AI", "Gemini", "LangGraph", "Google ADK", "Google Cloud", "AI", "Workshop"],
            abstract=(
                "[SYNTHETIC SAMPLE WORKSHOP] Bring your laptop for a 90-minute guided codelab! You will build "
                "a tool-calling agent, wire it into a stateful LangGraph workflow, inspect OpenTelemetry spans, "
                "and deploy it to Google Cloud Run."
            ),
            key_takeaways=[
                "Complete working multi-agent starter repository",
                "Step-by-step path to join the GDG Kocaeli Post-DevFest Agentic AI Study Jam",
            ],
            prerequisites=["Python 3.11+ installed"],
            capacity=60,
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
        ),
        EventSession(
            id="sess-panel-gde",
            event_id=event_id,
            title="[Sample Panel] GDE & Community Fireside: From Local Meetups to Global Technical Leadership",
            track="Community & Career",
            format=SessionFormat.PANEL,
            level="All Levels",
            start_time="16:00",
            end_time="16:45",
            room="Community Lounge — GDE Office Hours & Matchmaker Corner",
            speaker_ids=["spk-lukas-weber-sample", "spk-selin-kaya-sample", "org-zeynep-yildiz-sample"],
            speaker_names=[
                "Lukas Weber [Sample International Speaker]",
                "Dr. Selin Kaya [Sample GDE]",
                "Zeynep Yıldız [Sample GDG Organizer]",
            ],
            tags=["GDE", "Community", "Career", "Google Cloud", "AI", "Networking"],
            abstract=(
                "[SYNTHETIC SAMPLE PANEL] Interactive Q&A and structured matchmaking session with visiting GDEs "
                "and GDG Kocaeli organizers on open-source contributions, production AI careers, and community growth."
            ),
            key_takeaways=[
                "How to contribute talks, codelabs, and mentorship to GDG Kocaeli",
                "Consent-first networking in the Community Lounge",
            ],
            prerequisites=[],
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
        ),
    ]


def get_seed_kocaeli_places() -> list[KocaeliPlace]:
    """Return cultural, culinary, and landmark places in Kocaeli with time budgets."""
    return [
        KocaeliPlace(
            id="koc-sekapark-waterfront",
            name="Sekapark Coastal Promenade & Industrial Heritage Park",
            category="Waterfront & Culture",
            summary=(
                "Expansive waterfront park along the Gulf of İzmit transformed from Türkiye's historic "
                "SEKA paper mill into a vibrant cultural, science, and seaside promenade."
            ),
            cultural_context=(
                "Symbolizes Kocaeli's evolution from classic industrial manufacturing to public green space, "
                "science centers, and community gathering spots overlooking the Marmara sea."
            ),
            recommended_duration_minutes=60,
            travel_time_from_venue_minutes=10,
            opening_hours="07:00-23:00 (Sample verified window — outdoor promenade open daily)",
            tags=["waterfront", "walking", "sea view", "photography", "short visit", "coffee"],
            visitor_tip="Ideal first stop for a 2–3 hour window; walk along the pier and enjoy Turkish tea by the Gulf.",
            best_for=["Visiting speakers", "1-3 hour window", "Sunset walk", "Networking stroll"],
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
        ),
        KocaeliPlace(
            id="koc-izmit-clock-tower",
            name="Historic İzmit Clock Tower (Saat Kulesi) & Kasr-ı Hümayun Quarter",
            category="Landmark & History",
            summary=(
                "Iconic 1901 neoclassical Ottoman clock tower perched on the historic hill overlooking central "
                "İzmit and the Gulf, adjacent to the Sultan Abdülaziz Hunting Pavilion (Kasr-ı Hümayun)."
            ),
            cultural_context=(
                "The quintessential architectural emblem of İzmit (ancient Nicomedia), offering panoramic "
                "views of the Gulf of İzmit and historic timber mansions."
            ),
            recommended_duration_minutes=45,
            travel_time_from_venue_minutes=15,
            opening_hours="09:00-18:00 (Exterior viewpoint accessible until 22:00 — Sample hours)",
            tags=["history", "landmark", "architecture", "panorama", "short visit"],
            visitor_tip="Pair with a visit to a nearby heritage confectionery to see Pişmaniye hand-pulled.",
            best_for=["Visiting GDEs", "History enthusiasts", "1-3 hour window"],
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
        ),
        KocaeliPlace(
            id="koc-pismaniye-artisan-tasting",
            name="Traditional İzmit Pişmaniye Confectionery & Tea Experience",
            category="Gastronomy & Heritage",
            summary=(
                "Experience the namesake of our platform: freshly spun, warm İzmit Pişmaniye (floss halva) "
                "crafted from roasted wheat flour, butter, and pulled sugar threads, served with Simit & tea."
            ),
            cultural_context=(
                "Pişmaniye is Kocaeli's protected geographical indication delicacy—historically spun by "
                "artisans in a circle, uniting people around a shared table."
            ),
            recommended_duration_minutes=35,
            travel_time_from_venue_minutes=12,
            opening_hours="08:30-21:30 (Sample artisan shop window)",
            tags=["food", "dessert", "pismaniye", "culinary", "gifts", "short visit"],
            visitor_tip="Ask for freshly pulled warm Pişmaniye or chocolate-coated gift tins to bring home after DevFest.",
            best_for=["All visitors", "Quick cultural immersion", "1-3 hour window"],
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
        ),
        KocaeliPlace(
            id="koc-gayret-ship-museum",
            name="TCG Gayret Naval Museum Ship & Submarine Coastline",
            category="Museum & Engineering",
            summary=(
                "Historic Gearing-class destroyer preserved as an interactive maritime museum right on the "
                "İzmit waterfront promenade between central İzmit and Sekapark."
            ),
            cultural_context=(
                "A favorite stop for engineers visiting Kocaeli—step aboard the bridge, engine rooms, and "
                "communications decks right along the coast."
            ),
            recommended_duration_minutes=50,
            travel_time_from_venue_minutes=12,
            opening_hours="09:00-17:00 (Closed Mondays — Sample schedule; verify before visit)",
            tags=["museum", "engineering", "maritime", "waterfront"],
            visitor_tip="Located right between Sekapark and the city center, making it easy to combine in a 3-hour loop.",
            best_for=["Engineers", "Daytime 2-4 hour window"],
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
        ),
        KocaeliPlace(
            id="koc-ormanya-kartepe",
            name="Ormanya Natural Life Park & Kartepe Highland Foothills",
            category="Nature & Half-Day Excursion",
            summary=(
                "Lush forest sanctuary and mountain foothills east of İzmit between Sapanca Lake and the "
                "Gulf of İzmit."
            ),
            cultural_context=(
                "Showcases Kocaeli's dramatic geography where alpine forests meet the Marmara coast."
            ),
            recommended_duration_minutes=150,
            travel_time_from_venue_minutes=35,
            opening_hours="09:00-18:00 (Sample schedule)",
            tags=["nature", "forest", "half-day", "hiking"],
            visitor_tip="Requires at least 4+ free hours due to 35-minute each-way intercity transit.",
            best_for=["4-6 hour window", "Full afternoon or post-event Sunday"],
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
        ),
    ]


def get_seed_community_resources() -> list[CommunityResource]:
    """Return GDG Kocaeli learning paths, past meetup resources, and contribution guides."""
    return [
        CommunityResource(
            id="res-agentic-ai-pathway",
            title="GDG Kocaeli Post-DevFest Pathway: Foundations of Agentic AI & Gemini",
            category="Learning Path",
            topic_tags=["Agentic AI", "Gemini", "Google ADK", "LangGraph", "Python"],
            difficulty="Beginner to Intermediate",
            summary=(
                "[SAMPLE RESOURCE] Structured 4-week self-paced & cohort learning track covering Gemini 2.5 "
                "tool calling, Google Agent Development Kit (ADK), LangGraph state machines, and RAG grounding."
            ),
            url="https://developers.google.com/learn (Sample GDG Kocaeli Curated Track)",
            estimated_hours=12.0,
            related_session_ids=["sess-keynote-agentic", "sess-workshop-adk", "sess-hybrid-rag-xai"],
            how_to_contribute="Join the bi-weekly GDG Kocaeli Build with AI Study Jam as a peer reviewer or lab buddy.",
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
        ),
        CommunityResource(
            id="res-study-jam-cohort",
            title="GDG Kocaeli 'Build with AI' Monthly Study Jam & Architecture Clinic",
            category="Study Jam",
            topic_tags=["Agentic AI", "Google Cloud", "Vertex AI", "Cloud Run", "Community"],
            difficulty="All Levels",
            summary=(
                "[SAMPLE COMMUNITY ACTIVITY] Hands-on monthly weekend workshop hosted by GDG Kocaeli mentors "
                "where attendees build, trace, and deploy open-source agentic workflows."
            ),
            url="https://gdg.community.dev/ (Search GDG Kocaeli — Sample Link)",
            estimated_hours=3.0,
            related_session_ids=["sess-workshop-adk", "sess-prod-ai-cloudrun"],
            how_to_contribute="Submit a 10-minute lightning demo of what you built after DevFest!",
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
        ),
        CommunityResource(
            id="res-past-meetup-rag-archive",
            title="Archive: GDG Kocaeli Cloud & AI Meetup — Production RAG & Evaluation Patterns",
            category="Past Meetup",
            topic_tags=["RAG", "Explainable AI", "Vertex AI", "Agentic AI", "Evaluation"],
            difficulty="Intermediate",
            summary=(
                "[SAMPLE ARCHIVE] Slides, code notebooks, and evaluation checklists from GDG Kocaeli's "
                "previous technical meetup on grounded retrieval and OpenTelemetry tracing."
            ),
            url="https://github.com/gdg-kocaeli-sample/rag-observability-notebooks (Sample Repo)",
            estimated_hours=2.5,
            related_session_ids=["sess-hybrid-rag-xai"],
            how_to_contribute="Open a pull request adding Turkish or English evaluation test cases.",
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
        ),
        CommunityResource(
            id="res-cfp-speaker-incubator",
            title="GDG Kocaeli Speaker Incubator & Open Source Maintainer Program",
            category="CFP / Contribution",
            topic_tags=["Community", "Public Speaking", "Mentorship", "Agentic AI", "Google Cloud"],
            difficulty="All Levels",
            summary=(
                "[SAMPLE PROGRAM] Want to give your first technical talk or help evolve Pismaniye for "
                "DevFest Kocaeli 2027? Pair with an experienced speaker or GDE for slide & code review."
            ),
            url="https://gdg.community.dev/ (GDG Kocaeli CFP & Volunteer Portal — Sample)",
            estimated_hours=4.0,
            related_session_ids=["sess-panel-gde", "sess-opening-welcome"],
            how_to_contribute="Propose a lightning talk, mentor student developers, or contribute a new tool to Pismaniye.",
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
        ),
    ]


def get_seed_knowledge_documents(event_id: str = "devfest-kocaeli-2026") -> list[KnowledgeDocument]:
    """Synthesize comprehensive organizer-managed Knowledge Base documents across all 10 required categories."""
    docs: list[KnowledgeDocument] = []

    # 1 & 2. Speaker & GDE profiles
    for person in get_seed_people():
        if not person.opt_in_networking or person.visibility == ProfileVisibility.PRIVATE:
            continue
        doc_type = "gde_profile" if person.role == RoleType.GDE else "speaker_bio"
        docs.append(
            KnowledgeDocument(
                id=f"doc-{person.id}",
                event_id=event_id,
                title=f"{person.full_name} — {person.headline}",
                doc_type=doc_type,
                content=(
                    f"[SAMPLE DATA] Name: {person.full_name}\n"
                    f"Role: {person.role.value} | Organization: {person.organization} ({person.country})\n"
                    f"GDE Category: {person.gde_category or 'N/A'}\n"
                    f"Biography: {person.bio}\n"
                    f"Expertise & Technologies: {', '.join(person.expertise_tags + person.technologies)}\n"
                    f"Interests: {', '.join(person.interests)}\n"
                    f"Can Mentor On: {'; '.join(person.can_mentor_on)}\n"
                    f"Looking For: {'; '.join(person.looking_for)}"
                ),
                source_uri=f"pismaniye://directory/{person.id}",
                tags=list(set(person.interests + person.expertise_tags + person.technologies)),
                metadata={"person_id": person.id, "role": person.role.value},
                verification_status=person.verification_status,
            )
        )

    # 3, 4, 5. Sessions, Schedules, Workshops
    for sess in get_seed_sessions(event_id):
        doc_type = "workshop" if sess.format == SessionFormat.WORKSHOP else "session"
        docs.append(
            KnowledgeDocument(
                id=f"doc-{sess.id}",
                event_id=event_id,
                title=f"{sess.title} ({sess.start_time}–{sess.end_time}, {sess.room})",
                doc_type=doc_type,
                content=(
                    f"[SAMPLE SESSION] Title: {sess.title}\n"
                    f"Track: {sess.track} | Format: {sess.format.value} | Level: {sess.level}\n"
                    f"Schedule: {sess.start_time} to {sess.end_time} in {sess.room}\n"
                    f"Speakers: {', '.join(sess.speaker_names)}\n"
                    f"Abstract: {sess.abstract}\n"
                    f"Key Takeaways: {'; '.join(sess.key_takeaways)}\n"
                    f"Tags: {', '.join(sess.tags)}"
                ),
                source_uri=f"pismaniye://schedule/{sess.id}",
                tags=sess.tags + [sess.track, sess.format.value],
                metadata={"session_id": sess.id, "start_time": sess.start_time, "end_time": sess.end_time},
                verification_status=sess.verification_status,
            )
        )

    # 6. Venue information
    venue = get_seed_venue(event_id)
    docs.append(
        KnowledgeDocument(
            id="doc-venue-logistics",
            event_id=event_id,
            title=f"Venue & Logistics Guide — {venue.venue_name}",
            doc_type="venue",
            content=(
                f"Venue: {venue.venue_name} ({venue.city})\n"
                f"Address Note: {venue.address_note}\n"
                f"Stages & Rooms: {'; '.join(venue.rooms)}\n"
                f"Accessibility: {'; '.join(venue.accessibility_notes)}\n"
                f"Transport: {'; '.join(venue.transport_notes)}\n"
                f"Code of Conduct & Safety: {venue.emergency_and_code_of_conduct}"
            ),
            source_uri="pismaniye://venue/devfest-kocaeli-2026",
            tags=["venue", "logistics", "accessibility", "transport", "Kocaeli", "schedule"],
            verification_status=venue.verification_status,
        )
    )

    # 7. Local Kocaeli information
    for place in get_seed_kocaeli_places():
        docs.append(
            KnowledgeDocument(
                id=f"doc-{place.id}",
                event_id=event_id,
                title=f"Discover Kocaeli: {place.name} ({place.category})",
                doc_type="kocaeli",
                content=(
                    f"Place: {place.name} ({place.category})\n"
                    f"Summary: {place.summary}\n"
                    f"Cultural Context: {place.cultural_context}\n"
                    f"Recommended Duration: {place.recommended_duration_minutes} minutes | "
                    f"Transit from Venue: ~{place.travel_time_from_venue_minutes} minutes each way\n"
                    f"Opening Hours: {place.opening_hours}\n"
                    f"Visitor Tip: {place.visitor_tip}"
                ),
                source_uri=f"pismaniye://kocaeli/{place.id}",
                tags=place.tags + ["Kocaeli", "İzmit", place.category],
                metadata={
                    "place_id": place.id,
                    "duration_min": place.recommended_time if hasattr(place, "recommended_time") else place.recommended_duration_minutes,
                },
                verification_status=place.verification_status,
            )
        )

    # 8, 9, 10. Community documentation, past event resources, and learning materials
    for res in get_seed_community_resources():
        dtype = (
            "past_event"
            if res.category == "Past Meetup"
            else ("learning" if res.category in ("Learning Path", "Study Jam") else "community")
        )
        docs.append(
            KnowledgeDocument(
                id=f"doc-{res.id}",
                event_id=event_id,
                title=f"{res.title} ({res.category})",
                doc_type=dtype,
                content=(
                    f"Resource: {res.title}\n"
                    f"Category: {res.category} | Difficulty: {res.difficulty} | Est. Time: {res.estimated_hours}h\n"
                    f"Summary: {res.summary}\n"
                    f"Topics: {', '.join(res.topic_tags)}\n"
                    f"How to Contribute to GDG Kocaeli: {res.how_to_contribute or 'Join our community channels.'}\n"
                    f"Link: {res.url}"
                ),
                source_uri=res.url,
                tags=res.topic_tags + [res.category, "GDG Kocaeli"],
                metadata={"resource_id": res.id},
                verification_status=res.verification_status,
            )
        )

    # Additional Technical Architecture Reference Document for LangGraph / ADK / Gemini queries
    docs.append(
        KnowledgeDocument(
            id="doc-tech-langgraph-adk-blueprint",
            event_id=event_id,
            title="Technical Reference: Building Stateful Agents with LangGraph, Google ADK & Gemini",
            doc_type="learning",
            content=(
                "[SAMPLE TECHNICAL GUIDE] In DevFest Kocaeli 2026's AI track, we explore how LangGraph and "
                "Google Agent Development Kit (ADK) complement each other. LangGraph provides explicit cyclic "
                "and acyclic StateGraph orchestration with typed state checkpoints, while Google GenAI SDK "
                "(`google-genai`) and Vertex AI provide Gemini 2.5 reasoning and `text-embedding-004` semantic "
                "vectors. OpenTelemetry spans record every tool invocation and RAG chunk citation."
            ),
            source_uri="pismaniye://knowledge/langgraph-adk-blueprint",
            tags=["LangGraph", "Google ADK", "Gemini", "Agentic AI", "Vertex AI", "OpenTelemetry", "RAG"],
            verification_status=VerificationStatus.SYNTHETIC_SAMPLE,
        )
    )

    return docs
