"""Core module."""
import subprocess
from typing import List, Optional, Tuple

import pulsectl
from logzero import logger


def get_active_sinks(
    pulse: pulsectl.pulsectl.Pulse
) -> List[pulsectl.pulsectl.PulseSinkInfo]:
    """Returns a list with active sinks. The Real ones."""
    return [i for i in pulse.sink_list() if i.port_active]


def get_inputs() -> List[Tuple[str, int, int]]:
    """Returns list with active inputs."""
    with pulsectl.Pulse("apprec") as pulse:
        return [
            (i.proplist["application.name"], i.sink, i.index)
            for i in pulse.sink_input_list()
            if "application.name" in i.proplist.keys()
        ]


def get_apprec_sink_id(pulse: pulsectl.pulsectl.Pulse) -> Optional[int]:
    """Get sink id of our own combined sink."""
    sinks = pulse.sink_list()
    if sinks:
        for sink in sinks:
            if sink.name == "apprec":
                return sink.index
    return None


def record(audio_format: str, destination: str) -> None:
    """Record audio from sink."""
    cmd: List[str] = ["parec", "--verbose", "--format=s16le", "-d", "apprec.monitor"]
    if audio_format == "wav":
        cmd.extend(["--file-format=wav", destination])
    logger.debug("cmd list: %s", cmd)
    logger.info("Start recording... stop it with CTRL+c")
    subprocess.run(cmd)


def main(
    audio_format: str, destination: str, audio_input: Tuple[str, int, int]
) -> None:
    """Main logic."""
    with pulsectl.Pulse("apprec") as pulse:

        try:

            active_sinks = get_active_sinks(pulse)
            logger.debug("active sinks: %s", active_sinks)

            # create our own combined sink
            rec_sink_module_id = pulse.module_load(
                "module-combine-sink",
                args="sink_name=apprec slaves={}".format(
                    ",".join([i.name for i in active_sinks])
                ),
            )
            rec_sink_id = get_apprec_sink_id(pulse)
            logger.debug("loaded combined module with id: %s", rec_sink_module_id)
            logger.debug("created sink: %s", rec_sink_id)

            # move sink to our combined sink
            pulse.sink_input_move(audio_input[2], rec_sink_id)

            # set default sink
            pulse.sink_default_set(str(active_sinks[0].index))

            # start recording
            record(audio_format, destination)

        except KeyboardInterrupt:
            logger.info("stopped recording")

        except BaseException as exception:
            logger.exception(str(exception))

        finally:
            # remove used combined sink
            try:
                logger.info("Remove sink and module...")
                pulse.module_unload(rec_sink_module_id)
            except BaseException:
                pass

            # move back to original sink
            try:
                logger.info("Move back to normal...")
                pulse.sink_input_move(audio_input[2], audio_input[1])
            except BaseException:
                pass
