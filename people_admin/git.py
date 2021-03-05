import os
import typing
import github
from .models import DeltaSet
from .diff import DiffItem

REPO_NAME = "openstates/people"


def _get_repo():
    g = github.Github(os.environ["GITHUB_TOKEN"])
    return g.get_repo(REPO_NAME)


def get_files(
    ids: typing.List[str],
) -> typing.Dict[str, "github.ContentFile.ContentFile"]:
    """ turn list of ids into mapping to files """
    # TODO: needs to be expanded to other directories
    files = {}
    repo = _get_repo()
    all_files = list(repo.get_contents("data/nc/legislature"))
    for person_id in ids:
        uuid = person_id.split("/")[1]
        for file in all_files:
            if uuid in file.name:
                files[person_id] = file
                break
        else:
            raise ValueError(f"could not find {person_id}")
    return files


def patch_file(filename: str, deltas: typing.List[DiffItem]) -> typing.Dict[str, str]:
    """
    returns mapping of filename to contents
    """
    pass


def create_pr(branch: str, message: str, files: typing.Dict[str, str]):
    repo = _get_repo()
    main = repo.get_branch("main")

    updates = [
        github.InputGitTreeElement(path, mode="100644", type="blob", content=content)
        for path, content in files.items()
    ]
    new_tree = repo.create_git_tree(updates, repo.get_git_tree(main.commit.sha))
    new_commit = repo.create_git_commit(message, new_tree, [main.commit.commit])
    repo.create_git_ref(f"refs/heads/{branch}", sha=new_commit.sha)
    repo.create_pull()


def delta_set_to_pr(delta_set: DeltaSet):
    """
    get a list of person IDs mapped to lists of DiffItem and generate a github PR
    """
    person_deltas = {}
    for pd in delta_set.person_deltas.all():
        person_deltas[pd.person_id] = [DiffItem(*d) for d in pd.data_changes]

    files_by_id = get_files(person_deltas.keys())

    new_files = {}
    for person_id in person_deltas:
        filename = files_by_id[person_id]
        new_files[filename] = patch_file(filename, person_deltas[person_id])

    # create_pr(f"automatic/deltas/{state}-{random_chars}", delta_set.name, new_files)
