"""Integration tests for the 4 Signature Workflows, XAI Auditor, CLI commands, and FastAPI endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient
from typer.testing import CliRunner

from pismaniye.api.app import app as fastapi_app
from pismaniye.cli.main import app as cli_app
from pismaniye.config import get_settings
from pismaniye.data.repository import reset_repository
from pismaniye.orchestration.graph import PismaniyeOrchestrator

runner = CliRunner()
client = TestClient(fastapi_app)


def test_signature_workflow_a_meet_the_right_expert() -> None:
    repo = reset_repository()
    orch = PismaniyeOrchestrator(repo)
    trace = orch.run_query(
        "I'm interested in Agentic AI, Gemini, and production AI systems. Who should I meet?"
    )
    assert trace.workflow_name == "WORKFLOW_A_MEET_THE_RIGHT_EXPERT"
    matches = trace.structured_payload["matchmaker_agent"]["matches"]
    assert len(matches) >= 2
    top_match = matches[0]
    assert top_match["match_score"] > 0.70
    assert top_match["consent_status"] == "PENDING_REQUESTER_CONSENT"
    assert "private_email" not in top_match["person"]
    assert trace.explanation is not None
    assert len(trace.explanation.scoring_breakdowns) >= 2


def test_signature_workflow_b_my_devfest_day_resolves_conflicts() -> None:
    repo = reset_repository()
    orch = PismaniyeOrchestrator(repo)
    trace = orch.run_query(
        "Create my ideal DevFest agenda. I'm interested in Google Cloud and AI."
    )
    assert trace.workflow_name == "WORKFLOW_B_MY_DEVFEST_DAY"
    evt_payload = trace.structured_payload["event_agent"]
    assert len(evt_payload["agenda"]) >= 5
    # Verify 11:15 parallel track conflict was detected and explained
    assert len(evt_payload["conflicts_resolved"]) >= 1
    assert evt_payload["conflicts_resolved"][0]["time_slot"] == "11:15-12:00"


def test_signature_workflow_c_discover_kocaeli_respects_3_hour_budget() -> None:
    repo = reset_repository()
    orch = PismaniyeOrchestrator(repo)
    trace = orch.run_query(
        "I'm a visiting GDE. I have three free hours. Help me discover Kocaeli."
    )
    assert trace.workflow_name == "WORKFLOW_C_DISCOVER_KOCAELI"
    koc_payload = trace.structured_payload["kocaeli_agent"]
    assert koc_payload["available_hours"] == 3.0
    assert koc_payload["total_planned_minutes_with_return"] <= 180
    assert len(koc_payload["itinerary"]) >= 2
    assert len(koc_payload["alternatives_requiring_more_time"]) >= 1


def test_signature_workflow_d_community_knowledge_learning_path() -> None:
    repo = reset_repository()
    orch = PismaniyeOrchestrator(repo)
    trace = orch.run_query("I want to start learning Agentic AI after DevFest.")
    assert trace.workflow_name == "WORKFLOW_D_COMMUNITY_KNOWLEDGE"
    comm_payload = trace.structured_payload["community_agent"]
    assert len(comm_payload["pathway"]) >= 3
    assert trace.explanation is not None


def test_all_cli_commands_execute_cleanly() -> None:
    reset_repository()

    res_agents = runner.invoke(cli_app, ["agents"])
    assert res_agents.exit_code == 0
    assert "Event Agent" in res_agents.stdout

    res_sched = runner.invoke(cli_app, ["event", "schedule"])
    assert res_sched.exit_code == 0
    assert "Pişmaniye Stage" in res_sched.stdout

    res_disc = runner.invoke(cli_app, ["people", "discover", "--interest", "Agentic AI"])
    assert res_disc.exit_code == 0
    assert "Selin Kaya" in res_disc.stdout

    res_match = runner.invoke(cli_app, ["people", "match", "--interest", "Gemini", "--grant-consent"])
    assert res_match.exit_code == 0
    assert "Explicit consent recorded" in res_match.stdout

    res_koc = runner.invoke(cli_app, ["kocaeli", "explore", "--hours", "3"])
    assert res_koc.exit_code == 0
    assert "Sekapark" in res_koc.stdout

    res_know = runner.invoke(cli_app, ["knowledge", "search", "LangGraph"])
    assert res_know.exit_code == 0
    assert "LangGraph" in res_know.stdout

    res_trace = runner.invoke(cli_app, ["trace", "latest"])
    assert res_trace.exit_code == 0
    assert "Trace Record" in res_trace.stdout

    res_explain = runner.invoke(cli_app, ["explain", "latest"])
    assert res_explain.exit_code == 0
    assert "XAI DECISION AUDIT" in res_explain.stdout

    res_doc = runner.invoke(cli_app, ["doctor"])
    assert res_doc.exit_code == 0
    assert "PASS" in res_doc.stdout


def test_fastapi_web_qr_and_organizer_rbac_endpoints() -> None:
    reset_repository()

    home = client.get("/")
    assert home.status_code == 200
    assert "PISMANIYE" in home.text

    qr = client.get("/api/qr.svg")
    assert qr.status_code == 200
    assert "<svg" in qr.text

    chat = client.post(
        "/api/chat",
        json={"query": "Who should I meet for Agentic AI and Gemini?"},
    )
    assert chat.status_code == 200
    data = chat.json()
    assert "trace" in data
    assert data["trace"]["workflow_name"] == "WORKFLOW_A_MEET_THE_RIGHT_EXPERT"

    # RBAC check: missing token must return 403
    unauth = client.get("/api/organizer/analytics")
    assert unauth.status_code == 403

    # Authorized Organizer request
    token = get_settings().organizer_passcode
    headers = {"X-Organizer-Token": token}
    spk_res = client.post(
        "/api/organizer/speakers",
        headers=headers,
        json={
            "full_name": "Dr. Canan Ersoy",
            "headline": "Verified Cloud AI Speaker",
            "organization": "Gebze Technical University",
            "bio": "Verified speaker added via Organizer Dashboard.",
            "interests": ["Agentic AI", "Vertex AI"],
            "expertise_tags": ["Vertex AI", "Gemini"],
            "technologies": ["Python", "Vertex AI"],
            "verification_status": "VERIFIED_ORGANIZER_DATA",
        },
    )
    assert spk_res.status_code == 200
    assert spk_res.json()["speaker"]["verification_status"] == "VERIFIED_ORGANIZER_DATA"

    # Reset for DevFest Kocaeli 2027
    reset_res = client.post(
        "/api/organizer/reset-edition",
        headers=headers,
        json={
            "new_event_id": "devfest-kocaeli-2027",
            "new_event_name": "DevFest Kocaeli 2027",
            "new_year": 2027,
            "keep_community_knowledge": True,
        },
    )
    assert reset_res.status_code == 200
    assert reset_res.json()["new_event_id"] == "devfest-kocaeli-2027"
    assert reset_res.json()["preserved_kocaeli_places"] >= 4
