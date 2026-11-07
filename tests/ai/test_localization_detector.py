
from src.ai.localization.detector import validate_center


def test_valid_center():
    assert validate_center((100, 200), 500, 600) is True


def test_center_outside_image():
    assert validate_center((500, 200), 500, 600) is False


def test_missing_center():
    assert validate_center(None, 500, 600) is False


def test_invalid_image_dimensions():
    assert validate_center((10, 10), 0, 600) is False

import numpy as np

from src.ai.localization.detector import localize_centers


def test_localize_centers_returns_expected_keys():
    image = np.zeros((100, 100, 3), dtype=np.uint8)

    result = localize_centers(image)

    assert "optic_disc" in result
    assert "fovea" in result