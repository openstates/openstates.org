import os
import typing
import base64
import github
import yaml
import yamlordereddictloader
from utils.common import jid_to_abbr
from .models import DeltaSet, PullStatus
from .diff import DiffItem, apply_diffs

REPO_NAME = "openstates/people"
_repo = None


def load_yaml(file_obj):
    return yaml.load(file_obj, Loader=yamlordereddictloader.SafeLoader)


def dump_yaml(obj):
    return yaml.dump(
        obj, default_flow_style=False, Dumper=yamlordereddictloader.SafeDumper
    )


def _get_repo():
    global _repo
    if not _repo:
        g = github.Github(os.environ["GITHUB_TOKEN"])
        _repo = g.get_repo(REPO_NAME)
    return _repo


def get_files(
    ids: typing.List[str], states: typing.List[str],
) -> typing.Dict[str, "github.ContentFile.ContentFile"]:
    """ turn list of ids into mapping to files """
    # TODO: needs to be expanded to other directories
    files = {}
    repo = _get_repo()
    all_files = []
    for state in states:
        all_files.extend(list(repo.get_contents(f"data/{state}/legislature")))
    for person_id in ids:
        uuid = person_id.split("/")[1]
        for file in all_files:
            if uuid in file.name:
                files[person_id] = file
                break
        else:
            raise ValueError(f"could not find {person_id}")
    return files


def patch_file(
    file: github.ContentFile.ContentFile, deltas: typing.List[DiffItem]
) -> typing.Dict[str, str]:
    """
    returns mapping of filename to contents
    """
    content = base64.b64decode(file.content)
    data = load_yaml(content)
    data = apply_diffs(data, deltas)
    return dump_yaml(data)


def create_pr(branch: str, message: str, files: typing.Dict[str, str]):
    repo = _get_repo()
    main = repo.get_branch("main")

    # check for branch already existing
    try:
        ref = repo.get_git_ref(f"heads/{branch}")
    except github.GithubException:
        ref = None

    updates = [
        github.InputGitTreeElement(path, mode="100644", type="blob", content=content)
        for path, content in files.items()
    ]
    new_tree = repo.create_git_tree(updates, repo.get_git_tree(main.commit.sha))
    new_commit = repo.create_git_commit(message, new_tree, [main.commit.commit])
    if not ref:
        repo.create_git_ref(f"refs/heads/{branch}", sha=new_commit.sha)
    else:
        ref.edit(sha=new_commit.sha, force=True)
    try:
        pr = repo.create_pull(title=message, body=message, base="main", head=branch)
        return pr.url
    except github.GithubException:
        pass


def delta_set_to_pr(delta_set: DeltaSet):
    """
    get a list of person IDs mapped to lists of DiffItem and generate a github PR
    """
    person_deltas = {}
    states = set()
    for pd in delta_set.person_deltas.all():
        person_deltas[pd.person_id] = pd.data_changes
        states.add(jid_to_abbr(pd.person.current_jurisdiction_id))

    files_by_id = get_files(person_deltas.keys(), states=states)

    new_files = {}
    for person_id in person_deltas:
        file = files_by_id[person_id]
        new_files[file.path] = patch_file(file, person_deltas[person_id])

    url = create_pr(f"people_admin_deltas/{delta_set.id}", delta_set.name, new_files)
    return url


def get_pr_status(pr_id: int) -> PullStatus:
    repo = _get_repo()
    pull = repo.get_pull(pr_id)
    if pull.merged:
        return PullStatus.MERGED
    elif pull.state == "closed":
        return PullStatus.REJECTED
    else:
        return PullStatus.CREATED
