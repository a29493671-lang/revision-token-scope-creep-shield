
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base
from backend.app.models import User, Project, Milestone, RevisionRequest, Quote
from backend.app.services.token_service import create_revision_request


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    Base.metadata.create_all(bind=engine)

    TestingSession = sessionmaker(
        bind=engine,
        expire_on_commit=False
    )

    session = TestingSession()

    client = User(
        name="Test Client",
        email="testclient@example.com",
        role="client"
    )

    freelancer = User(
        name="Test Freelancer",
        email="testfreelancer@example.com",
        role="freelancer"
    )

    session.add_all([client, freelancer])
    session.commit()

    project = Project(
        title="Test Project",
        description="Project for testing",
        client_id=client.id,
        freelancer_id=freelancer.id
    )

    session.add(project)
    session.commit()

    milestone = Milestone(
        project_id=project.id,
        title="Test Milestone",
        remaining_revision_tokens=3
    )

    session.add(milestone)
    session.commit()

    milestone_id = milestone.id
    client_id = client.id

    yield session, milestone_id, client_id

    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_three_free_revisions_and_fourth_paid(db):
    session, milestone_id, client_id = db

    first = create_revision_request(
        session, milestone_id, client_id, "First revision"
    )
    assert first["request_type"] == "free"
    assert first["remaining_tokens"] == 2

    second = create_revision_request(
        session, milestone_id, client_id, "Second revision"
    )
    assert second["request_type"] == "free"
    assert second["remaining_tokens"] == 1

    third = create_revision_request(
        session, milestone_id, client_id, "Third revision"
    )
    assert third["request_type"] == "free"
    assert third["remaining_tokens"] == 0

    fourth = create_revision_request(
        session,
        milestone_id,
        client_id,
        "Fourth revision",
        quote_amount=1500.00
    )

    assert fourth["request_type"] == "paid"
    assert fourth["remaining_tokens"] == 0
    assert fourth["quote_status"] == "pending"

    requests = session.query(RevisionRequest).all()
    quotes = session.query(Quote).all()
    milestone = session.get(Milestone, milestone_id)

    assert len(requests) == 4
    assert len(quotes) == 1
    assert milestone.remaining_revision_tokens == 0
    assert float(quotes[0].amount) == 1500.00


def test_invalid_paid_request_does_not_create_records(db):
    session, milestone_id, client_id = db

    # Use all three free tokens
    for number in range(1, 4):
        create_revision_request(
            session,
            milestone_id,
            client_id,
            f"Free revision {number}"
        )

    # Fourth request without a quote amount should fail
    with pytest.raises(
        ValueError,
        match="A valid quote amount is required"
    ):
        create_revision_request(
            session,
            milestone_id,
            client_id,
            "Invalid paid revision"
        )

    # Verify no incomplete records were created
    requests = session.query(RevisionRequest).all()
    quotes = session.query(Quote).all()
    milestone = session.get(Milestone, milestone_id)

    assert len(requests) == 3
    assert len(quotes) == 0
    assert milestone.remaining_revision_tokens == 0
