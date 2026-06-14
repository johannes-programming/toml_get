from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Self
from unittest.mock import patch

from toml_get import main, run

__all__ = ["Test_0"]


class Test_0(unittest.TestCase):
    def make_toml_file(
        self: Self, directory: Path, name: str, contents: str
    ) -> Path:
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
        return path

    def capture_run_stdout(self: Self, **kwargs: object) -> str:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            run(**kwargs)  # type: ignore[arg-type]
        return buffer.getvalue()

    def test_run_reads_top_level_key_from_file(self: Self) -> None:
        with TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            config = self.make_toml_file(
                tmpdir,
                "config.toml",
                'name = "toml-get"\n',
            )

            output = self.capture_run_stdout(
                infiles=[str(config)],
                keys=["name"],
            )

        self.assertEqual(output, "toml-get\n")

    def test_run_reads_nested_key_and_list_index_from_file(self: Self) -> None:
        with TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            config = self.make_toml_file(
                tmpdir,
                "nested/settings.toml",
                """
                [server]
                host = "localhost"
                ports = [8000, 8001, 8002]
                """,
            )

            output = self.capture_run_stdout(
                infiles=[str(config)],
                keys=["server", "ports", "1"],
                outstring="port=%s\n",
            )

        self.assertEqual(output, "port=8001\n")

    def test_run_uses_default_when_key_is_missing(self: Self) -> None:
        with TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            config = self.make_toml_file(
                tmpdir,
                "config.toml",
                'name = "toml-get"\n',
            )

            output = self.capture_run_stdout(
                infiles=[str(config)],
                keys=["missing"],
                default="fallback\n",
            )

        self.assertEqual(output, "fallback\n")

    def test_run_tries_later_files_after_missing_key_in_first_file(
        self: Self,
    ) -> None:
        with TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            first = self.make_toml_file(
                tmpdir,
                "first.toml",
                'other = "not it"\n',
            )
            second = self.make_toml_file(
                tmpdir,
                "second.toml",
                'name = "from second"\n',
            )

            output = self.capture_run_stdout(
                infiles=[str(first), str(second)],
                keys=["name"],
            )

        self.assertEqual(output, "from second\n")

    def test_run_writes_to_output_file_when_overwrite_is_true(
        self: Self,
    ) -> None:
        with TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            config = self.make_toml_file(
                tmpdir,
                "config.toml",
                'name = "toml-get"\n',
            )
            output_file = tmpdir / "out/result.txt"
            output_file.parent.mkdir(parents=True, exist_ok=True)

            run(
                infiles=[str(config)],
                keys=["name"],
                outfile=str(output_file),
                overwrite=True,
            )

            self.assertEqual(
                output_file.read_text(encoding="utf-8"), "toml-get\n"
            )

    def test_run_reads_from_stdin_marker(self: Self) -> None:
        with patch(
            "builtins.input",
            return_value='[project]\nname = "stdin project"\n',
        ):
            output = self.capture_run_stdout(
                infiles=["-"],
                keys=["project", "name"],
            )

        self.assertEqual(output, "stdin project\n")

    def test_run_emits_nothing_without_value_or_default(self: Self) -> None:
        with TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            config = self.make_toml_file(
                tmpdir,
                "config.toml",
                'name = "toml-get"\n',
            )

            output = self.capture_run_stdout(
                infiles=[str(config)],
                keys=["missing"],
            )

        self.assertEqual(output, "")

    def test_run_uses_default_when_outstring_formatting_fails(
        self: Self,
    ) -> None:
        with TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            config = self.make_toml_file(
                tmpdir,
                "config.toml",
                'name = "toml-get"\n',
            )

            output = self.capture_run_stdout(
                infiles=[str(config)],
                keys=["name"],
                outstring="%(missing)s\n",
                default="format fallback\n",
            )

        self.assertEqual(output, "format fallback\n")

    def test_main_parses_arguments_and_prints_value(self: Self) -> None:
        with TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            config = self.make_toml_file(
                tmpdir,
                "pyproject.toml",
                """
                [project]
                name = "toml_get"
                version = "1.0.14"
                """,
            )
            buffer = io.StringIO()

            with redirect_stdout(buffer):
                main(
                    [
                        "--infile",
                        str(config),
                        "--key",
                        "project",
                        "--key",
                        "version",
                        "--outstring",
                        "version=%s\n",
                    ]
                )

        self.assertEqual(buffer.getvalue(), "version=1.0.14\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
