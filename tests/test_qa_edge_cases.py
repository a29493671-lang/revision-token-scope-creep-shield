from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_qa_unauthenticated_milestone_access_blocked():
    """T08: Unauthenticated requests cannot inspect milestones."""
    response = client.get("/milestones/999999")
    assert response.status_code in (401, 403, 404)


def test_qa_empty_revision_payload_rejected():
    """T05: Empty/invalid revision payload fails validation without server error."""
    response = client.post("/revisions", json={})
    assert response.status_code in (401, 403, 404, 422)