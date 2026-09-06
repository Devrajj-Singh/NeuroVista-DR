from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.main import app


PROJECT_ROOT = Path(__file__).resolve().parents[2]

TEST_IMAGE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "aptos"
    / "aptos2019-blindness-detection"
    / "train_images"
    / "000c1434d8d7.png"
)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "neurovista-dr-api"
    assert data["model_loaded"] is True


def test_analyze_valid_fundus_image(client):
    with TEST_IMAGE.open("rb") as image_file:
        response = client.post(
            "/api/v1/analyze",
            files={
                "image": (
                    TEST_IMAGE.name,
                    image_file,
                    "image/png",
                )
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"

    prediction = data["prediction"]

    assert 0 <= prediction["icdr_grade"] <= 4
    assert isinstance(prediction["class_name"], str)
    assert 0.0 <= prediction["confidence"] <= 1.0

    assert prediction["referable_dr"] == (
        prediction["icdr_grade"] >= 2
    )


def test_probabilities_are_valid(client):
    with TEST_IMAGE.open("rb") as image_file:
        response = client.post(
            "/api/v1/analyze",
            files={
                "image": (
                    TEST_IMAGE.name,
                    image_file,
                    "image/png",
                )
            },
        )

    assert response.status_code == 200

    probabilities = response.json()["probabilities"]

    assert set(probabilities.keys()) == {"0", "1", "2", "3", "4"}

    assert all(
        0.0 <= value <= 1.0
        for value in probabilities.values()
    )

    assert abs(sum(probabilities.values()) - 1.0) < 1e-6


def test_non_image_upload_is_rejected(client):
    response = client.post(
        "/api/v1/analyze",
        files={
            "image": (
                "test.txt",
                b"this is not an image",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Uploaded file must be an image."
    )


def test_invalid_image_is_rejected(client):
    response = client.post(
        "/api/v1/analyze",
        files={
            "image": (
                "invalid.png",
                b"not actually an image",
                "image/png",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Uploaded file is not a valid image."
    )


def test_empty_image_is_rejected(client):
    response = client.post(
        "/api/v1/analyze",
        files={
            "image": (
                "empty.png",
                b"",
                "image/png",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Uploaded image is empty."
    )