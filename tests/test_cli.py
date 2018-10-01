# pylint: disable=missing-docstring,too-many-arguments,redefined-outer-name
# pylint: disable=unused-argument
from unittest.mock import call, patch

import pytest
from click.testing import CliRunner

from apprec import cli


@pytest.fixture
def runner():
    yield CliRunner()


@patch("apprec.cli.click.echo")
def test_banner(mock_echo):
    cli.banner()
    assert len(mock_echo.call_args_list) == 7


@pytest.mark.parametrize(
    "inputs,exit_code,echos",
    [
        ([], 1, [call("No inputs right now.")]),
        ([("Firefox", 0)], 0, [call("0: Firefox")]),
    ],
)
@patch("apprec.cli.banner")
@patch("apprec.cli.click.prompt")
@patch("apprec.cli.click.echo")
@patch("apprec.cli.core.get_inputs")
@patch("apprec.cli.core.main")
def test_main(
    mock_main,
    mock_get_inputs,
    mock_echo,
    mock_prompt,
    mock_banner,
    runner,
    inputs,
    exit_code,
    echos,
):
    mock_get_inputs.return_value = inputs
    mock_prompt.return_value = 0

    result = runner.invoke(cli.main, ["--audio-format", "wav", "/tmp/foobar"])

    mock_banner.assert_called_with()
    assert mock_echo.call_args_list == echos
    assert result.exit_code == exit_code
