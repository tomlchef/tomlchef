"""Generic CLI, adopted by programs built with TOMLChef.

This module is intended for internal use only.
"""
import importlib
from pathlib import Path
from typing import Union

import click
import toml
from click import ParamType
from toml import TomlDecodeError

import tomlchef
from tomlchef.job import Job


class _Cli:  # pylint: disable=missing-class-docstring
    CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

    def __init__(self, package_name: str, package_version: str,
                 program_name: Union[str, None] = None,
                 footer: Union[str, None] = None):
        """
        Construct the commandline interface.

        :param package_name: Name of the package. Must be a valid name
            registered to ``importlib`` (usually by installing via ``pip``).
        :param package_version: Version of the package.
        :param program_name: Stylized package name (e.g., NumPy instead of
            numpy) to show in the CLI.
        :param footer: Text to show below the version information (such as
        copyright notices or legal disclaimers).
        """
        if not _Cli._is_valid_package_name(package_name):
            raise ValueError(f"Unknown package: {package_name}")

        self.package_name = package_name
        self.package_version = package_version
        self.program_name = (
            program_name if program_name is not None else package_name)
        self.footer = footer

        message = (f"%(prog)s version %(version)s "
                   f"(TOMLChef {tomlchef.__version__})")
        if self.footer is not None:
            message += f"\n{self.footer}"

        @click.group(name=package_name, context_settings=self.CONTEXT_SETTINGS)
        @click.version_option(
            self.package_version, "--version", "-v",
            package_name=self.package_name,
            message=message,
            prog_name=self.program_name)
        def _cli() -> None:
            pass

        @_cli.command()
        @click.argument("job", required=True, type=_JobParamType())
        @click.option("-o", "--output-dir", required=False,
                      type=click.Path(
                          exists=True, file_okay=False, dir_okay=True,
                          resolve_path=True, path_type=Path),
                      help="Directory to write the recipe to")
        def recipe(job: Job,  # pylint: disable=unused-argument
                   output_dir: Path  # pylint: disable=unused-argument
                   ) -> None:
            """
            Generate a recipe for a Job.
            :param job: Name of the Job.
            :param output_dir: Optional directory to save the recipe to.
            """
            pass  # TODO

        @_cli.command(name="exec")
        @click.argument("recipe", required=True,
                        type=_Recipe(
                            exists=True, dir_okay=True, file_okay=True,
                            resolve_path=True, path_type=Path))
        def execute(recipe: dict  # pylint: disable=unused-argument
                    ) -> None:
            """
            Build a job from a recipe and execute it.

            RECIPE must be a path to a valid recipe in TOML format, or to a
            directory containing an existing Job.
            """
            pass  # TODO

        self.cli = _cli

    @staticmethod
    def _is_valid_package_name(package_name: str) -> bool:
        try:
            importlib.import_module(package_name)
            return True
        except ImportError:
            return False


class _JobParamType(ParamType):  # pylint: disable=missing-class-docstring

    def convert(self, value, param, ctx) -> Job:
        if issubclass(type(value), Job):
            return value.__class__
        try:
            return value  # TODO
        except ValueError:
            self.fail(f"{value} is not a valid job name.",
                      param, ctx)  # pytype: disable=bad-return-type


class _Recipe(click.Path):  # pylint: disable=missing-class-docstring
    def convert(self, value, param, ctx) -> dict:
        value = Path(super().convert(value, param, ctx))

        def _parse_toml(path: Path) -> dict:
            try:
                return toml.load(path)
            except TomlDecodeError:
                self.fail(
                    f"{value} is not a valid TOML file.",
                    param, ctx)  # pytype: disable=bad-return-type

        if value.is_file():
            if value.suffix == ".toml":
                return _parse_toml(value)
            self.fail(
                f"{value} is not a valid TOML file.", param, ctx)
        elif value.is_dir():
            candidates = [x for x in value.iterdir() if x.suffix == ".toml"]
            if len(candidates) == 1:
                return _parse_toml(candidates[0])
            else:
                self.fail(
                    f"{value} is not a valid Job directory.",
                    param, ctx)  # pytype: disable=bad-return-type
        else:
            self.fail(
                f"{value} is neither a file nor a directory.",
                param, ctx)  # pytype: disable=bad-return-type
