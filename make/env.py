import argparse
import json
import subprocess
from typing import Any, Optional

__all__ = ["main", "run"]


def env_create(env: str, python: Optional[str]) -> subprocess.CompletedProcess:  # type: ignore[type-arg]
    args: list[str]
    args = [
        "conda",
        "create",
        "--name",
        env,
        "--yes",
        "--channel",
        "conda-forge",
        "--override-channels",
    ]
    if python is not None:
        args.append("python=" + python)
    return subprocess.run(
        args,
        check=True,
        capture_output=True,
        text=True,
    )


def env_list() -> list[str]:
    ans: list[str]
    data: Any
    result: subprocess.CompletedProcess  # type: ignore[type-arg]
    try:
        result = subprocess.run(
            ["conda", "env", "list", "--json"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    data = json.loads(result.stdout)
    ans = list()
    for details in data["envs_details"].values():
        ans.append(str(details["name"]))
    return ans


def env_remove(env: str) -> subprocess.CompletedProcess:  # type: ignore[type-arg]
    args: list[str]
    args = ["conda", "env", "remove", "-y", "-n", env]
    return subprocess.run(args, check=True)


def main(args: Optional[list[str]] = None, /) -> None:
    kwargs: dict[str, Any]
    parser: argparse.ArgumentParser
    parser = argparse.ArgumentParser(fromfile_prefix_chars="@")
    # parser.add_argument("--errfile", default="-")
    # parser.add_argument("--outfile", default="-")
    parser.add_argument("--python")
    parser.add_argument("--recreate", action="store_true")
    parser.add_argument("envs", default=[], nargs="*")
    kwargs = vars(parser.parse_args(args))
    run(*kwargs.pop("envs"), **kwargs)


def run(
    *envs: str, python: Optional[str] = None, recreate: bool = False
) -> None:
    env: str
    envs_: list[str]
    envs_ = env_list()
    for env in envs:
        if env in envs_ and not recreate:
            continue
        if env in envs_:
            env_remove(env)
        env_create(env, python=python)


if __name__ == "__main__":
    main()
