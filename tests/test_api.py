
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db


TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("FREELANCER_INVITE_CODE", "test-invite-code")

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


def create_users(client):
    client_response = client.post(
        "/auth/register",
        json={
            "name": "Demo Client",
            "email": "client@example.com",
            "password": "clientpass123"
        }
    )
    assert client_response.status_code == 201

    freelancer_response = client.post(
        "/auth/register-freelancer",
        json={
            "name": "Demo Freelancer",
            "email": "freelancer@example.com",
            "password": "freelancerpass123",
            "invite_code": "test-invite-code"
        }
    )
    assert freelancer_response.status_code == 201

    client_login = client.post(
        "/auth/login",
        data={
            "username": "client@example.com",
            "password": "clientpass123"
        }
    )
    assert client_login.status_code == 200

    freelancer_login = client.post(
        "/auth/login",
        data={
            "username": "freelancer@example.com",
            "password": "freelancerpass123"
        }
    )
    assert freelancer_login.status_code == 200

    return {
        "client": client_login.json()["access_token"],
        "freelancer": freelancer_login.json()["access_token"]
    }


def create_project(client, tokens):
    response = client.post(
        "/projects/",
        headers={
            "Authorization": f"Bearer {tokens['freelancer']}"
        },
        json={
            "title": "Website Development",
            "description": "Build a business website",
            "client_email": "client@example.com"
        }
    )

    assert response.status_code == 200
    return response.json()["project"]["id"]


def create_milestone(client, tokens, project_id):
    response = client.post(
        f"/projects/{project_id}/milestones/",
        headers={
            "Authorization": f"Bearer {tokens['freelancer']}"
        },
        json={
            "title": "Homepage Design",
            "description": "Complete the homepage"
        }
    )

    assert response.status_code == 200
    return response.json()["milestone"]["id"]


def submit_four_revisions(client, tokens, project_id, milestone_id):
    revision_id = None

    for number in range(1, 5):
        response = client.post(
            f"/projects/{project_id}/milestones/{milestone_id}/revisions/",
            headers={
                "Authorization": f"Bearer {tokens['client']}"
            },
            json={
                "request_description": f"Revision {number}"
            }
        )

        assert response.status_code == 200
        revision_id = response.json()["revision"]["id"]

    return revision_id


def create_quote(client, tokens, project_id, revision_id):
    return client.post(
        f"/projects/{project_id}/quotes/{revision_id}",
        headers={
            "Authorization": f"Bearer {tokens['freelancer']}"
        },
        json={
            "amount": 1500,
            "currency": "INR",
            "description": "Additional design work"
        }
    )


def test_home_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200


def test_user_registration_and_authentication(client):
    tokens = create_users(client)

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {tokens['client']}"
        }
    )

    assert response.status_code == 200
    assert response.json()["role"] == "CLIENT"


def test_invalid_freelancer_invite_code(client):
    response = client.post(
        "/auth/register-freelancer",
        json={
            "name": "Another Freelancer",
            "email": "another@example.com",
            "password": "password123",
            "invite_code": "wrong-code"
        }
    )

    assert response.status_code == 403


def test_unauthenticated_project_access(client):
    response = client.get("/projects/")
    assert response.status_code == 401


def test_project_creation(client):
    tokens = create_users(client)
    project_id = create_project(client, tokens)

    assert project_id > 0


def test_client_cannot_create_project(client):
    tokens = create_users(client)

    response = client.post(
        "/projects/",
        headers={
            "Authorization": f"Bearer {tokens['client']}"
        },
        json={
            "title": "Unauthorized Project",
            "description": "Should not be created",
            "client_email": "client@example.com"
        }
    )

    assert response.status_code == 403


def test_milestone_starts_with_three_tokens(client):
    tokens = create_users(client)
    project_id = create_project(client, tokens)
    milestone_id = create_milestone(client, tokens, project_id)

    response = client.get(
        f"/projects/{project_id}/milestones/",
        headers={
            "Authorization": f"Bearer {tokens['freelancer']}"
        }
    )

    assert response.status_code == 200
    milestone = response.json()["milestones"][0]
    assert milestone["id"] == milestone_id
    assert milestone["tokens_total"] == 3
    assert milestone["tokens_remaining"] == 3


def test_three_free_revisions_and_fourth_addon(client):
    tokens = create_users(client)
    project_id = create_project(client, tokens)
    milestone_id = create_milestone(client, tokens, project_id)

    for number in range(1, 4):
        response = client.post(
            f"/projects/{project_id}/milestones/{milestone_id}/revisions/",
            headers={
                "Authorization": f"Bearer {tokens['client']}"
            },
            json={
                "request_description": f"Revision {number}"
            }
        )

        assert response.status_code == 200
        assert response.json()["revision"]["revision_type"] == "FREE_TOKEN"
        assert response.json()["tokens_remaining"] == 3 - number

    fourth = client.post(
        f"/projects/{project_id}/milestones/{milestone_id}/revisions/",
        headers={
            "Authorization": f"Bearer {tokens['client']}"
        },
        json={
            "request_description": "Additional revision"
        }
    )

    assert fourth.status_code == 200
    assert fourth.json()["revision"]["revision_type"] == "ADD_ON"
    assert fourth.json()["revision"]["status"] == "QUOTE_REQUIRED"
    assert fourth.json()["tokens_remaining"] == 0


def test_freelancer_cannot_submit_revision(client):
    tokens = create_users(client)
    project_id = create_project(client, tokens)
    milestone_id = create_milestone(client, tokens, project_id)

    response = client.post(
        f"/projects/{project_id}/milestones/{milestone_id}/revisions/",
        headers={
            "Authorization": f"Bearer {tokens['freelancer']}"
        },
        json={
            "request_description": "Unauthorized revision"
        }
    )

    assert response.status_code == 403


def test_addon_quote_workflow(client):
    tokens = create_users(client)
    project_id = create_project(client, tokens)
    milestone_id = create_milestone(client, tokens, project_id)

    revision_id = submit_four_revisions(
        client, tokens, project_id, milestone_id
    )

    quote_response = create_quote(
        client, tokens, project_id, revision_id
    )

    assert quote_response.status_code == 200
    assert quote_response.json()["quote"]["status"] == "PENDING"

    quote_id = quote_response.json()["quote"]["id"]

    update_response = client.patch(
        f"/projects/{project_id}/quotes/{quote_id}/status",
        headers={
            "Authorization": f"Bearer {tokens['client']}"
        },
        json={"status": "ACCEPTED"}
    )

    assert update_response.status_code == 200
    assert update_response.json()["quote"]["status"] == "ACCEPTED"


def test_quote_can_be_rejected(client):
    tokens = create_users(client)
    project_id = create_project(client, tokens)
    milestone_id = create_milestone(client, tokens, project_id)

    revision_id = submit_four_revisions(
        client, tokens, project_id, milestone_id
    )

    quote_response = create_quote(
        client, tokens, project_id, revision_id
    )
    quote_id = quote_response.json()["quote"]["id"]

    rejected = client.patch(
        f"/projects/{project_id}/quotes/{quote_id}/status",
        headers={
            "Authorization": f"Bearer {tokens['client']}"
        },
        json={"status": "REJECTED"}
    )

    assert rejected.status_code == 200
    assert rejected.json()["quote"]["status"] == "REJECTED"


def test_duplicate_quote_is_rejected(client):
    tokens = create_users(client)
    project_id = create_project(client, tokens)
    milestone_id = create_milestone(client, tokens, project_id)

    revision_id = submit_four_revisions(
        client, tokens, project_id, milestone_id
    )

    first = create_quote(client, tokens, project_id, revision_id)
    second = create_quote(client, tokens, project_id, revision_id)

    assert first.status_code == 200
    assert second.status_code == 400


def test_cannot_create_quote_for_free_revision(client):
    tokens = create_users(client)
    project_id = create_project(client, tokens)
    milestone_id = create_milestone(client, tokens, project_id)

    revision = client.post(
        f"/projects/{project_id}/milestones/{milestone_id}/revisions/",
        headers={
            "Authorization": f"Bearer {tokens['client']}"
        },
        json={"request_description": "Free revision"}
    )

    revision_id = revision.json()["revision"]["id"]

    quote_response = create_quote(
        client, tokens, project_id, revision_id
    )

    assert quote_response.status_code == 400


def test_activity_tracking(client):
    tokens = create_users(client)
    project_id = create_project(client, tokens)
    milestone_id = create_milestone(client, tokens, project_id)

    submit_four_revisions(client, tokens, project_id, milestone_id)

    response = client.get(
        f"/projects/{project_id}/activity/",
        headers={
            "Authorization": f"Bearer {tokens['freelancer']}"
        }
    )

    assert response.status_code == 200

    actions = [
        item["action"]
        for item in response.json()["activities"]
    ]

    assert "PROJECT_CREATED" in actions
    assert "MILESTONE_CREATED" in actions
    assert "REVISION_REQUESTED" in actions


def test_invalid_project_returns_404(client):
    tokens = create_users(client)

    response = client.get(
        "/projects/99999",
        headers={
            "Authorization": f"Bearer {tokens['client']}"
        }
    )

    assert response.status_code == 404


def test_project_listing(client):
    tokens = create_users(client)
    create_project(client, tokens)

    response = client.get(
        "/projects/",
        headers={
            "Authorization": f"Bearer {tokens['freelancer']}"
        }
    )

    assert response.status_code == 200
    assert response.json()["total_projects"] == 1


def test_revision_notification_privacy_and_read_status(client):
    tokens = create_users(client)
    project_id = create_project(client, tokens)
    milestone_id = create_milestone(client, tokens, project_id)

    revision_response = client.post(
        f"/projects/{project_id}/milestones/{milestone_id}/revisions/",
        headers={
            "Authorization": f"Bearer {tokens['client']}"
        },
        json={"request_description": "Update the homepage"}
    )
    assert revision_response.status_code == 200

    freelancer_notifications = client.get(
        "/notifications/",
        headers={
            "Authorization": f"Bearer {tokens['freelancer']}"
        }
    )

    assert freelancer_notifications.status_code == 200
    data = freelancer_notifications.json()
    assert data["total_notifications"] == 1
    assert data["unread_notifications"] == 1

    notification_id = data["notifications"][0]["id"]

    client_notifications = client.get(
        "/notifications/",
        headers={
            "Authorization": f"Bearer {tokens['client']}"
        }
    )

    assert client_notifications.status_code == 200
    assert client_notifications.json()["total_notifications"] == 0

    unauthorized_read = client.patch(
        f"/notifications/{notification_id}/read",
        headers={
            "Authorization": f"Bearer {tokens['client']}"
        }
    )
    assert unauthorized_read.status_code == 404

    mark_read = client.patch(
        f"/notifications/{notification_id}/read",
        headers={
            "Authorization": f"Bearer {tokens['freelancer']}"
        }
    )

    assert mark_read.status_code == 200
    assert mark_read.json()["is_read"] is True

    updated_notifications = client.get(
        "/notifications/",
        headers={
            "Authorization": f"Bearer {tokens['freelancer']}"
        }
    )

    assert updated_notifications.json()["unread_notifications"] == 0


def test_quote_notifications(client):
    tokens = create_users(client)
    project_id = create_project(client, tokens)
    milestone_id = create_milestone(client, tokens, project_id)

    revision_id = submit_four_revisions(
        client, tokens, project_id, milestone_id
    )

    quote_response = create_quote(
        client, tokens, project_id, revision_id
    )
    assert quote_response.status_code == 200

    client_notifications = client.get(
        "/notifications/",
        headers={
            "Authorization": f"Bearer {tokens['client']}"
        }
    )

    assert client_notifications.status_code == 200
    client_data = client_notifications.json()
    assert client_data["total_notifications"] == 1
    assert "add-on quote" in (
        client_data["notifications"][0]["message"].lower()
    )

    quote_id = quote_response.json()["quote"]["id"]

    accepted = client.patch(
        f"/projects/{project_id}/quotes/{quote_id}/status",
        headers={
            "Authorization": f"Bearer {tokens['client']}"
        },
        json={"status": "ACCEPTED"}
    )

    assert accepted.status_code == 200

    freelancer_notifications = client.get(
        "/notifications/",
        headers={
            "Authorization": f"Bearer {tokens['freelancer']}"
        }
    )

    assert freelancer_notifications.status_code == 200
    freelancer_data = freelancer_notifications.json()

    # Four revision notifications plus one quote-status notification.
    assert freelancer_data["total_notifications"] == 5

    messages = [
        item["message"].lower()
        for item in freelancer_data["notifications"]
    ]
    assert any("accepted" in message for message in messages)


def test_notifications_require_authentication(client):
    response = client.get("/notifications/")
    assert response.status_code == 401

    response = client.patch("/notifications/1/read")
    assert response.status_code == 401
