import os
import pytest
from people_admin.git import get_files

# these tests are finnicky as they rely upon the outside repo, they will be skipped unless
# the environment key is set
if not os.environ.get("GITHUB_TOKEN"):
    pytest.skip("skipping GitHub tests", allow_module_level=True)


def test_get_files():
    ABE_JONES = "ocd-person/559521af-e5f9-43c3-a75e-de9b242d364f"
    CARL_FORD = "ocd-person/91615553-5509-4625-ab20-7a81896438e0"

    files = get_files([ABE_JONES, CARL_FORD])
    assert files[ABE_JONES].name.startswith("Abe")
    assert files[CARL_FORD].name.startswith("Carl")


def test_get_files_error():
    BAD_ID = "ocd-person/559521af-e5f9-43c3-a75e-000000000000"

    with pytest.raises(ValueError):
        get_files([BAD_ID])
