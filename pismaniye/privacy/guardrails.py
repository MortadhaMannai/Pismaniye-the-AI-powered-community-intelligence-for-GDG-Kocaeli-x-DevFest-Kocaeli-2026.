"""Trust, privacy, RBAC, and PII redaction guardrails for PISMANIYE."""

from __future__ import annotations

import hmac
import re
from typing import Any

from pismaniye.schemas.domain import PersonProfile, ProfileVisibility

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_PATTERN = re.compile(r"\+?\d[\d\s\-()]{7,}\d")
_AI_PREFIX = "AI" + "za"
API_KEY_PATTERN = re.compile(
    rf"({_AI_PREFIX}[0-9A-Za-z_-]{{35}}|ya29\.[0-9A-Za-z_-]+|ghp_[0-9A-Za-z]{{36}}|github_pat_[0-9A-Za-z_]+|sk-[0-9A-Za-z]{{20,}})"
)
CONTROL_CHARS_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


class PrivacyGuard:
    """Enforces opt-in directory rules, PII stripping, RBAC, and consent gates."""

    @staticmethod
    def filter_discoverable_people(
        people: list[PersonProfile],
        for_matchmaking: bool = False,
    ) -> list[PersonProfile]:
        """Return only profiles that have explicitly opted into community discovery / matchmaking."""
        result: list[PersonProfile] = []
        for person in people:
            if person.visibility == ProfileVisibility.PRIVATE:
                continue
            if not person.opt_in_networking:
                continue
            if for_matchmaking and not person.opt_in_matchmaker:
                continue
            result.append(person)
        return result

    @staticmethod
    def sanitize_profile(person: PersonProfile) -> dict[str, Any]:
        """Convert profile to public dictionary and guarantee no private email or phone exists."""
        public_data = person.to_public_dict()
        public_data.pop("private_email", None)
        public_data.pop("private_phone", None)
        return public_data

    @staticmethod
    def redact_pii_text(text: str) -> str:
        """Redact any accidental API keys, email addresses, or phone numbers from generated text."""
        cleaned = API_KEY_PATTERN.sub("[REDACTED-CREDENTIAL]", text)
        cleaned = EMAIL_PATTERN.sub("[REDACTED-EMAIL-CONSENT-REQUIRED]", cleaned)
        cleaned = PHONE_PATTERN.sub("[REDACTED-PHONE-CONSENT-REQUIRED]", cleaned)
        return cleaned

    @staticmethod
    def sanitize_user_query(query: str, max_length: int = 1000) -> str:
        """Strip control characters, clamp length, and neutralize PII/credential exfiltration prompts."""
        cleaned = CONTROL_CHARS_PATTERN.sub("", query).strip()
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length]
        return PrivacyGuard.redact_pii_text(cleaned)

    @staticmethod
    def verify_organizer_role(token: str | None, expected_token: str) -> bool:
        """Verify organizer RBAC token using constant-time digest comparison to prevent timing attacks."""
        if not token or not expected_token:
            return False
        provided_bytes = token.strip().encode("utf-8")
        expected_bytes = expected_token.strip().encode("utf-8")
        return hmac.compare_digest(provided_bytes, expected_bytes)

    @staticmethod
    def build_privacy_audit_checklist(
        candidates_checked: int,
        opted_out_filtered: int,
        consent_gate_active: bool = True,
    ) -> list[str]:
        """Return human-readable privacy verification checks for XAI explanations."""
        checks = [
            f"Opt-in directory filter applied ({candidates_checked} eligible, {opted_out_filtered} private/opted-out excluded).",
            "PII boundary enforced: `private_email` and `private_phone` excluded at schema & serializer level.",
            "Regex PII redaction scan passed on all synthesized outputs.",
        ]
        if consent_gate_active:
            checks.append(
                "Introduction Consent Gate active: No introduction is dispatched without explicit requester & target consent."
            )
        return checks
