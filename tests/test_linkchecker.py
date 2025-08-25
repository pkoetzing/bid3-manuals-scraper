from src import scraper as s
from pathlib import Path


def test_validate_local_site_empty(tmp_path: Path):
    # empty folder should yield no broken links
    res = s.validate_local_site(root=tmp_path)
    assert res == []
