import argparse
import tomllib
from collections.abc import Iterable
from typing import Any, Optional

__all__ = ["main", "run"]


def get_from_file(
    *,
    infile: str,
    keys: Iterable[str],
) -> Any:
    data: dict[str, Any]
    stream: Any
    x: str
    y: int | str
    if infile == "-":
        data = tomllib.loads(input())
    else:
        with open(infile, "rb") as stream:
            data = tomllib.load(stream)
    for x in keys:
        try:
            y = str(x) if isinstance(data, dict) else int(x)
            data = data[y]
        except Exception:
            return None
    return data


def main(args: Optional[Iterable[str]] = None, /) -> None:
    parser: argparse.ArgumentParser
    space: argparse.Namespace
    parser = argparse.ArgumentParser(fromfile_prefix_chars="@")
    parser.add_argument(
        "--infile",
        action="append",
        default=[],
        dest="infiles",
    )
    parser.add_argument(
        "--key",
        action="append",
        default=[],
        dest="keys",
    )
    parser.add_argument(
        "--default",
    )
    parser.add_argument(
        "--outstring",
        default="%s\n",
    )
    parser.add_argument(
        "--outfile",
        default="-",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
    )
    space = parser.parse_args(args)
    run(**vars(space))


def run(
    *,
    infiles: Iterable[str] = (),
    keys: Iterable[str] = (),
    default: object = None,
    outstring: str = "%s\n",
    outfile: str = "-",
    overwrite: bool = False,
) -> None:
    ans: Any
    stream: Any
    ans = None
    for infile in infiles:
        ans = get_from_file(
            infile=infile,
            keys=keys,
        )
        if ans is not None:
            break
    if ans is not None:
        try:
            ans = outstring % ans
        except Exception:
            ans = None
    if ans is None:
        ans = default
    if ans is None:
        return
    if outfile == "-":
        print(ans, end="")
        return
    with open(outfile, "w" if overwrite else "wb") as stream:
        print(ans, end="", file=stream)
