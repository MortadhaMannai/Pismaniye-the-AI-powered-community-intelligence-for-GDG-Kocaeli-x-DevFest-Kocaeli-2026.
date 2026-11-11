# Security Policy & Zero-Secret Architecture (`PISMANIYE`)

## 1. Zero-Secret & Credential Guarantees

- **No API Keys in Source Control**: This repository contains **zero** real API keys, Google Cloud service account keys, OAuth tokens, or private SSH keys.
- **Deterministic Offline Default (`local_deterministic`)**: Pismaniye runs 100% deterministically without requiring external API keys.
- **Masked Configuration**: Sensitive settings (`google_api_key`, `organizer_passcode`) are configured with `repr=False` in [`PismaniyeSettings`](pismaniye/config.py) so they are never printed in stack traces or object representations. Also, `organizer_passcode` is generated dynamically at runtime (`secrets.token_urlsafe`) when unset—zero hardcoded tokens exist anywhere in the codebase.
- **Git Ignore Boundaries**: `.env`, `.pismaniye_state/`, and `.venv/` are strictly excluded in [`.gitignore`](.gitignore).

---

## 2. Application & Agentic Security Controls

1. **Opt-In Directory Enforcement**:
   - [`PrivacyGuard.filter_discoverable_people()`](pismaniye/privacy/guardrails.py) excludes any profile where `opt_in_networking=False` or `visibility=PRIVATE` before any agent (`PeopleAgent`, `MatchmakerAgent`) or API endpoint accesses the candidate pool.
2. **PII Schema & Output Redaction**:
   - `private_email` and `private_phone` are marked `exclude=True` on [`PersonProfile`](pismaniye/schemas/domain.py) and stripped by `PrivacyGuard.sanitize_profile()`.
   - [`PrivacyGuard.redact_pii_text()`](pismaniye/privacy/guardrails.py) scrubs accidental email addresses, phone numbers, and cloud credential patterns from all synthesized outputs and user queries.
3. **Constant-Time RBAC Verification**:
   - Organizer endpoints (`/api/organizer/*`) require the `X-Organizer-Token` header verified via `hmac.compare_digest()` to prevent timing side-channel attacks.
4. **HTTP Security Headers & Strict CORS**:
   - FastAPI middleware enforces `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, and `Permissions-Policy`.
   - QR Code generator (`/api/qr.svg`) validates `http://` or `https://` schemes and rejects `javascript:` / `data:` URIs.
5. **Non-Root Container Execution**:
   - [`Dockerfile`](Dockerfile) runs the production server under an unprivileged `pismaniye` system user (`UID 10001`).

---

## 3. Reporting a Vulnerability

If you discover a security or privacy issue, please contact **Mortadha Mannai** (`mannaimortadha898@gmail.com` / [@MortadhaMannai](https://github.com/MortadhaMannai)).
