import os
import base64
import pytest
from people_admin.git import get_files, patch_file, get_pr_status
from people_admin.models import PullStatus

# these tests are finnicky as they rely upon the outside repo, they will be skipped unless
# the environment key is set
if not os.environ.get("GITHUB_TOKEN"):
    pytest.skip("skipping GitHub tests", allow_module_level=True)

ABE_JONES = "ocd-person/559521af-e5f9-43c3-a75e-de9b242d364f"
CARL_FORD = "ocd-person/91615553-5509-4625-ab20-7a81896438e0"


def test_get_files():
    files = get_files([ABE_JONES, CARL_FORD], states=["nc"])
    assert files[ABE_JONES].name.startswith("Abe")
    assert files[CARL_FORD].name.startswith("Carl")


def test_get_files_error():
    BAD_ID = "ocd-person/559521af-e5f9-43c3-a75e-000000000000"

    with pytest.raises(ValueError):
        get_files([BAD_ID], states=["nc"])


def test_patch_file_noop():
    file = get_files([ABE_JONES], states=["nc"])[ABE_JONES]
    original_content = base64.b64decode(file.content).decode()
    new_content = patch_file(file, [])
    # useful for diff, won't be printed if equal
    print(original_content, "\n=====\n", new_content)
    assert original_content == new_content


def test_patch_file_set_key():
    file = get_files([ABE_JONES], states=["nc"])[ABE_JONES]
    new_content = patch_file(file, [["set", "special_key", "added!"]])
    assert "special_key: added!" in new_content


def test_pr_status():
    # test two old PRs, no easy way to test that open status works here
    assert get_pr_status(44) == PullStatus.MERGED
    assert get_pr_status(46) == PullStatus.REJECTED
