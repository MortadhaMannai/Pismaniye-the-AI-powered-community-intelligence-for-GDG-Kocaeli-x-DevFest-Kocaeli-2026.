# Deploying PISMANIYE to Google Cloud (Cloud Run, Vertex AI, Firestore & GCS)

Pismaniye uses modular adapters (`pismaniye/adapters/google_cloud.py`) so it runs identically in:
- **`local_deterministic` mode** (zero external credentials required; ideal for live stage demos, CI, and offline development)
- **`google_cloud` / `hybrid` mode** powered by **Google GenAI SDK (`google-genai`)**, **Vertex AI (`text-embedding-004`)**, **Google ADK (`google-adk`)**, **Cloud Firestore**, **Cloud Storage**, and **Google Cloud Run**.

---

## 1. Prerequisites

```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="europe-west1"
gcloud config set project "$PROJECT_ID"

gcloud services enable \
  run.googleapis.com \
  aiplatform.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

---

## 2. Create Cloud Storage Bucket & Firestore Database

```bash
# Create GCS bucket for Organizer-Managed Knowledge Base documents
gcloud storage buckets create "gs://${PROJECT_ID}-pismaniye-knowledge" --location="$REGION"

# Create Firestore database in Native mode (if not already created)
gcloud firestore databases create --location="$REGION"
```

---

## 3. Deploy to Google Cloud Run

```bash
git clone https://github.com/MortadhaMannai/Pismaniye-the-AI-powered-community-intelligence-for-GDG-Kocaeli-x-DevFest-Kocaeli-2026..git
cd Pismaniye-the-AI-powered-community-intelligence-for-GDG-Kocaeli-x-DevFest-Kocaeli-2026.

gcloud run deploy pismaniye-concierge \
  --source . \
  --region "$REGION" \
  --allow-unauthenticated \
  --set-env-vars="PISMANIYE_EVENT_ID=devfest-kocaeli-2026" \
  --set-env-vars="PISMANIYE_MODE=google_cloud" \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
  --set-env-vars="GOOGLE_CLOUD_LOCATION=${REGION}" \
  --set-env-vars="PISMANIYE_GEMINI_MODEL=gemini-2.5-flash" \
  --set-env-vars="PISMANIYE_EMBEDDING_MODEL=text-embedding-004" \
  --set-env-vars="PISMANIYE_GCS_BUCKET_NAME=${PROJECT_ID}-pismaniye-knowledge"
```

---

## 4. Reusing for DevFest Kocaeli 2027 and Future GDG Kocaeli Events

Organizers can transition Pismaniye to future editions without redeploying code:
1. Open the **Organizer Dashboard** (`/0` -> **🛠️ Organizer Dashboard**) or call `POST /api/organizer/reset-edition` with header `X-Organizer-Token`.
2. Specify `new_event_id: "devfest-kocaeli-2027"` and `keep_community_knowledge: true`.
3. Event-specific sessions and temporary introductions are cleared while preserving verified Kocaeli local guides, community learning paths, and study jam archives.
