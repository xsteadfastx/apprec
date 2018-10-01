# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
# pylint: disable=too-many-arguments,unused-argument
from unittest.mock import Mock, call, patch

import pulsectl
import pytest

from apprec import core


@pytest.fixture
def mock_pulse():
    yield Mock(spec=pulsectl.pulsectl.Pulse)


def test_get_active_sinks(mock_pulse):
    mock_sink = Mock()
    mock_pulse.sink_list.return_value = [mock_sink]

    assert core.get_active_sinks(mock_pulse) == [mock_sink]


@patch("apprec.core.pulsectl")
def test_get_inputs(mock_p):
    mock_sink = Mock()
    mock_sink.sink = 0
    mock_sink.index = 1
    mock_sink.proplist = {"application.name": "testname"}
    si = [mock_sink]
    mock_p.Pulse.return_value.__enter__.return_value.sink_input_list.return_value = si

    assert core.get_inputs() == [("testname", 0, 1)]

    mock_sink.proplist = {}

    assert core.get_inputs() == []


def test_get_apprec_sink_id_empty(mock_pulse):
    mock_pulse.sink_list.return_value = []

    assert core.get_apprec_sink_id(mock_pulse) is None


def test_get_apprec_sink_id(mock_pulse):
    mock_sink = Mock()
    mock_sink.name = "apprec"
    mock_sink.index = 0

    mock_pulse.sink_list.return_value = [mock_sink]

    assert core.get_apprec_sink_id(mock_pulse) == 0


@patch("apprec.core.subprocess")
def test_record(mock_subprocess):
    core.record("wav", "foo.wav")

    mock_subprocess.run.assert_called_with(
        [
            "parec",
            "--verbose",
            "--format=s16le",
            "-d",
            "apprec.monitor",
            "--file-format=wav",
            "foo.wav",
        ]
    )


@patch("apprec.core.get_apprec_sink_id")
@patch("apprec.core.record")
@patch("apprec.core.get_active_sinks")
@patch("apprec.core.pulsectl")
def test_main(
    mock_pulsectl, mock_get_active_sinks, mock_record, mock_get_apprec_sink_id
):
    mock_pulse_sink_info = Mock(spec=pulsectl.pulsectl.PulseSinkInfo)
    mock_pulse_sink_info.name = "testsink"
    mock_pulse_sink_info.index = 77
    mock_get_active_sinks.return_value = [mock_pulse_sink_info]
    mock_get_apprec_sink_id.return_value = 99

    mock_pulse = Mock()
    mock_pulse.module_load.return_value = 111
    mock_pulsectl.Pulse.return_value.__enter__.return_value = mock_pulse

    core.main("wav", "/tmp/foo.wav", ("input", 100, 1))

    mock_get_active_sinks.assert_called_with(mock_pulse)

    mock_pulse.module_load.assert_called_with(
        "module-combine-sink", args="sink_name=apprec slaves=testsink"
    )

    mock_get_apprec_sink_id.assert_called_with(mock_pulse)

    assert mock_pulse.sink_input_move.call_args_list == [call(1, 99), call(1, 100)]

    mock_pulse.sink_default_set.assert_called_with("77")

    mock_record.assert_called_with("wav", "/tmp/foo.wav")

    mock_pulse.module_unload.assert_called_with(111)


@pytest.mark.parametrize(
    "exception, info_log_list, exc_log_list",
    [
        (
            KeyboardInterrupt,
            [
                call("stopped recording"),
                call("Remove sink and module..."),
                call("Move back to normal..."),
            ],
            [],
        ),
        (
            KeyError("this is a error"),
            [call("Remove sink and module..."), call("Move back to normal...")],
            [call("'this is a error'")],
        ),
    ],
)
@patch("apprec.core.logger")
@patch("apprec.core.get_active_sinks")
@patch("apprec.core.pulsectl")
def test_main_exceptions(
    mock_pulsectl,
    mock_get_active_sinks,
    mock_logger,
    exception,
    info_log_list,
    exc_log_list,
):
    mock_get_active_sinks.side_effect = exception

    core.main("wav", "/tmp/foo.wav", ("input", 100, 1))

    assert mock_logger.info.call_args_list == info_log_list

    assert mock_logger.exception.call_args_list == exc_log_list


@patch("apprec.core.logger")
@patch("apprec.core.get_apprec_sink_id")
@patch("apprec.core.record")
@patch("apprec.core.get_active_sinks")
@patch("apprec.core.pulsectl")
def test_main_exception_input_move(
    mock_pulsectl,
    mock_get_active_sinks,
    mock_record,
    mock_get_apprec_sink_id,
    mock_logger,
):
    mock_pulse_sink_info = Mock(spec=pulsectl.pulsectl.PulseSinkInfo)
    mock_pulse_sink_info.name = "testsink"
    mock_pulse_sink_info.index = 77
    mock_get_active_sinks.return_value = [mock_pulse_sink_info]
    mock_get_apprec_sink_id.return_value = 99

    mock_pulse = Mock()
    mock_pulse.module_load.return_value = 111
    mock_pulse.sink_input_move.side_effect = [None, KeyError("this is a error")]
    mock_pulsectl.Pulse.return_value.__enter__.return_value = mock_pulse

    core.main("wav", "/tmp/foo.wav", ("input", 100, 1))

    mock_get_active_sinks.assert_called_with(mock_pulse)

    mock_pulse.module_load.assert_called_with(
        "module-combine-sink", args="sink_name=apprec slaves=testsink"
    )

    mock_get_apprec_sink_id.assert_called_with(mock_pulse)

    assert mock_pulse.sink_input_move.call_args_list == [call(1, 99), call(1, 100)]

    mock_pulse.sink_default_set.assert_called_with("77")

    mock_record.assert_called_with("wav", "/tmp/foo.wav")

    mock_pulse.module_unload.assert_called_with(111)
