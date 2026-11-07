
import pytest

from src.ai.localization.annotations import load_center_annotations


def test_load_center_annotations(tmp_path):
    csv_file = tmp_path / "centers.csv"
    csv_file.write_text(
        "Image No,X- Coordinate,Y - Coordinate\n"
        "IDRiD_001,2858,1805\n"
        "IDRiD_002,100,200\n",
        encoding="utf-8",
    )

    result = load_center_annotations(csv_file)

    assert result == {
        "IDRiD_001": (2858, 1805),
        "IDRiD_002": (100, 200),
    }


def test_missing_csv_raises_error(tmp_path):
    missing_file = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_center_annotations(missing_file)


def test_duplicate_image_id_raises_error(tmp_path):
    csv_file = tmp_path / "duplicates.csv"
    csv_file.write_text(
        "Image No,X- Coordinate,Y - Coordinate\n"
        "IDRiD_001,100,200\n"
        "IDRiD_001,300,400\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate annotation"):
        load_center_annotations(csv_file)
