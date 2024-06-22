# pylint: disable=missing-module-docstring
import os.path
import tempfile
import unittest
from pathlib import Path
from typing import Callable
from typing import Union
from unittest.mock import patch

from click.testing import CliRunner

import tomlchef
from tomlchef._cli import _Cli


class TestCli(unittest.TestCase):  # pylint: disable=missing-class-docstring
    # Just a random hash that will be unique in all CLI messages
    TEST_APP_PACKAGE_NAME = "a097c208"

    TEST_APP_PROGRAM_NAME = "My Test App"

    TEST_APP_VERSION = "0.3.1"

    TOMLCHEF_VERSION = "1.2.0"

    HELP_MESSAGE = (f"Usage: {TEST_APP_PACKAGE_NAME} " +
                    """[OPTIONS] COMMAND [ARGS]...

Options:
  -v, --version  Show the version and exit.
  -h, --help     Show this message and exit.

Commands:
  exec    Build a job from a recipe and execute it.
  recipe  Generate a recipe for a Job.
""")

    VERSION_MESSAGE = (f"{TEST_APP_PACKAGE_NAME} version {TEST_APP_VERSION} "
                       f"(TOMLChef {TOMLCHEF_VERSION})\n")

    @staticmethod
    def _invalid_command_message(command):
        return (f"Usage: {TestCli.TEST_APP_PACKAGE_NAME} " +
                f"""[OPTIONS] COMMAND [ARGS]...
Try '{TestCli.TEST_APP_PACKAGE_NAME} -h' for help.

Error: No such command '{command}'.
""")

    @staticmethod
    def _invalid_option_message(option) -> str:
        return (f"Usage: {TestCli.TEST_APP_PACKAGE_NAME} " +
                f"""[OPTIONS] COMMAND [ARGS]...
Try '{TestCli.TEST_APP_PACKAGE_NAME} -h' for help.

Error: No such option: {option}
""")

    @patch("tomlchef._cli._Cli._is_valid_package_name", return_value=True)
    def setUp(self, _):
        self.cli = _Cli(self.TEST_APP_PACKAGE_NAME, self.TEST_APP_VERSION)
        tomlchef.__version__ = self.TOMLCHEF_VERSION

    def test_no_arg_prints_help(self):
        result = CliRunner().invoke(self.cli.cli, [])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(self.HELP_MESSAGE, result.output)

    def test_short_help(self):
        result = CliRunner().invoke(self.cli.cli, ["-h"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(self.HELP_MESSAGE, result.output)

    def test_long_help(self):
        result = CliRunner().invoke(self.cli.cli, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(self.HELP_MESSAGE, result.output)

    def test_invalid_args(self):
        result = CliRunner().invoke(self.cli.cli, ["--asdf"])
        self.assertEqual(2, result.exit_code)
        self.assertEqual(self._invalid_option_message("--asdf"), result.output)

        result = CliRunner().invoke(self.cli.cli, ["-z"])
        self.assertEqual(2, result.exit_code)
        self.assertEqual(self._invalid_option_message("-z"), result.output)

        result = CliRunner().invoke(self.cli.cli, ["asdf"])
        self.assertEqual(2, result.exit_code)
        self.assertEqual(self._invalid_command_message("asdf"), result.output)

    def test_short_version(self):
        result = CliRunner().invoke(self.cli.cli, ["-v"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(self.VERSION_MESSAGE, result.output)

    def test_long_version(self):
        result = CliRunner().invoke(self.cli.cli, ["--version"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(self.VERSION_MESSAGE, result.output)

    @patch("tomlchef._cli._Cli._is_valid_package_name", return_value=True)
    def test_version_with_program_name(self, _):
        self.cli = _Cli(self.TEST_APP_PACKAGE_NAME, self.TEST_APP_VERSION,
                        self.TEST_APP_PROGRAM_NAME)
        result = CliRunner().invoke(self.cli.cli, ["--version"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(self.VERSION_MESSAGE.replace(
            self.TEST_APP_PACKAGE_NAME, self.TEST_APP_PROGRAM_NAME),
            result.output)

    @patch("tomlchef._cli._Cli._is_valid_package_name", return_value=False)
    def test_invalid_package_name(self, _):
        self.assertRaises(
            ValueError,
            lambda: _Cli(self.TEST_APP_PACKAGE_NAME, self.TEST_APP_VERSION))

    @patch("tomlchef._cli._Cli._is_valid_package_name", return_value=True)
    def test_version_footer(self, _):
        self.cli = _Cli(self.TEST_APP_PACKAGE_NAME, self.TEST_APP_VERSION,
                        footer="Copyright (c) Developers")
        result = CliRunner().invoke(self.cli.cli, ["--version"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(self.VERSION_MESSAGE + "Copyright (c) Developers\n",
                         result.output)

    def test_recipe(self):
        result = CliRunner().invoke(self.cli.cli, ["recipe", "AJobClass"])
        self.assertEqual("", result.output)
        self.assertEqual(0, result.exit_code)

    @patch("tomlchef._cli._JobParamType.convert",
           lambda self, value, param, ctx: self.fail(
               f"{value} is not a valid job name"))
    def test_recipe_invalid_job_name(self):
        result = CliRunner().invoke(self.cli.cli, ["recipe", "AJobClass"])
        self.assertEqual(f"Usage: {self.TEST_APP_PACKAGE_NAME} recipe " +
                         f"""[OPTIONS] JOB
Try '{self.TEST_APP_PACKAGE_NAME} recipe -h' for help.

Error: Invalid value for 'JOB': AJobClass is not a valid job name
""", result.output)
        self.assertEqual(2, result.exit_code)

    def test_recipe_no_class_given(self):
        result = CliRunner().invoke(self.cli.cli, ["recipe"])
        self.assertEqual(f"Usage: {self.TEST_APP_PACKAGE_NAME} " +
                         f"""recipe [OPTIONS] JOB
Try '{self.TEST_APP_PACKAGE_NAME} recipe -h' for help.

Error: Missing argument 'JOB'.
""", result.output)
        self.assertEqual(2, result.exit_code)

    def test_recipe_output_dir_short(self):
        d = tempfile.mkdtemp(dir=Path(__file__).parent)
        result = CliRunner().invoke(
            self.cli.cli, ["recipe", "AJobClass", "-o", d])
        os.rmdir(d)

        self.assertEqual("", result.output)
        self.assertEqual(0, result.exit_code)

    def test_recipe_output_dir(self):
        d = tempfile.mkdtemp(dir=Path(__file__).parent)
        result = CliRunner().invoke(
            self.cli.cli,
            ["recipe", "AJobClass", "--output-dir", d])
        os.rmdir(d)

        self.assertEqual("", result.output)
        self.assertEqual(0, result.exit_code)

    def test_recipe_output_nonexistent_dir(self):
        d = os.path.realpath(tempfile.mkdtemp(dir=Path(__file__).parent))
        os.rmdir(d)
        result = CliRunner().invoke(
            self.cli.cli, ["recipe", "AJobClass", "--output-dir", d])
        self.assertEqual(f"Usage: {self.TEST_APP_PACKAGE_NAME} " +
                         f"""recipe [OPTIONS] JOB
Try '{self.TEST_APP_PACKAGE_NAME} recipe -h' for help.

Error: Invalid value for '-o' / '--output-dir': Directory {d!r} """ +
                         "does not exist.\n", result.output)
        self.assertEqual(2, result.exit_code)

    def test_recipe_output_file_instead_of_dir(self):
        result, f = self._exec_with_file(
            lambda ff: CliRunner().invoke(
                self.cli.cli, ["recipe", "AJobClass", "--output-dir", ff]),
            suffix=None)
        self.assertEqual(f"Usage: {self.TEST_APP_PACKAGE_NAME} " +
                         f"""recipe [OPTIONS] JOB
Try '{self.TEST_APP_PACKAGE_NAME} recipe -h' for help.

Error: Invalid value for '-o' / '--output-dir': Directory {f!r} is a file.
""", result.output)
        self.assertEqual(2, result.exit_code)

    def test_exec(self):
        result, _ = self._exec_with_file(
            lambda f: CliRunner().invoke(self.cli.cli, ["exec", f]),
            suffix=".toml")

        self.assertEqual("", result.output)
        self.assertEqual(0, result.exit_code)

    @staticmethod
    def _exec_with_file(action: Callable, suffix: Union[str, None]):
        fd, f = tempfile.mkstemp(dir=Path(__file__).parent, suffix=suffix)
        f = os.path.realpath(f)
        result = action(f)
        os.close(fd)
        os.remove(f)
        return result, f

    def test_exec_invalid_toml_recipe(self):
        with tempfile.NamedTemporaryFile(
                suffix=".toml", dir=Path(__file__).parent,
                delete=False) as f:
            f.write(str.encode("5"))
            f.flush()
            f_name = os.path.realpath(f.name)
        result = CliRunner().invoke(self.cli.cli, ["exec", f_name])
        os.remove(f_name)

        self.assertEqual(f"Usage: {self.TEST_APP_PACKAGE_NAME} exec " +
                         f"""[OPTIONS] RECIPE
Try '{self.TEST_APP_PACKAGE_NAME} exec -h' for help.

Error: Invalid value for 'RECIPE': {f_name} is not a valid TOML file.
""", result.output)
        self.assertEqual(2, result.exit_code)

    def test_exec_invalid_recipe(self):
        result, f = self._exec_with_file(
            lambda ff: CliRunner().invoke(self.cli.cli, ["exec", ff]),
            suffix=".json")

        self.assertEqual(f"Usage: {self.TEST_APP_PACKAGE_NAME} exec " +
                         f"""[OPTIONS] RECIPE
Try '{self.TEST_APP_PACKAGE_NAME} exec -h' for help.

Error: Invalid value for 'RECIPE': {f} is not a valid TOML file.
""", result.output)
        self.assertEqual(2, result.exit_code)

    def test_exec_no_recipe_given(self):
        result = CliRunner().invoke(self.cli.cli, ["exec"])
        self.assertEqual(f"Usage: {self.TEST_APP_PACKAGE_NAME} exec " +
                         f"""[OPTIONS] RECIPE
Try '{self.TEST_APP_PACKAGE_NAME} exec -h' for help.

Error: Missing argument 'RECIPE'.
""", result.output)
        self.assertEqual(2, result.exit_code)

    def test_exec_dir_without_job_file(self):
        d = os.path.realpath(tempfile.mkdtemp(dir=Path(__file__).parent))
        result = CliRunner().invoke(self.cli.cli, ["exec", d])
        os.rmdir(d)

        self.assertEqual(f"Usage: {self.TEST_APP_PACKAGE_NAME} exec " +
                         f"""[OPTIONS] RECIPE
Try '{self.TEST_APP_PACKAGE_NAME} exec -h' for help.

Error: Invalid value for 'RECIPE': {d} is not a valid Job directory.
""", result.output)
        self.assertEqual(2, result.exit_code)

    @patch("tomlchef._cli.Path.is_file", lambda x: False)
    @patch("tomlchef._cli.Path.is_dir", lambda x: False)
    def test_exec_not_file_or_dir(self):
        d = os.path.realpath(tempfile.mkdtemp(dir=Path(__file__).parent))
        result = CliRunner().invoke(self.cli.cli, ["exec", d])
        os.rmdir(d)

        self.assertEqual(f"Usage: {self.TEST_APP_PACKAGE_NAME} exec " +
                         f"""[OPTIONS] RECIPE
Try '{self.TEST_APP_PACKAGE_NAME} exec -h' for help.

Error: Invalid value for 'RECIPE': {d} is neither a file nor a directory.
""", result.output)
        self.assertEqual(2, result.exit_code)
