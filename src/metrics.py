import json
import logging

from src import constants, utils

Metric = dict[str, dict[str, int]]
Metrics = dict[str, Metric]

log = logging.getLogger(__name__)


@utils.locker("metrics")
def plus_one(dictionary: str, file_format: str, etym: str) -> None:
    metrics = read()

    try:
        metrics[dictionary][file_format][etym] += 1
    except KeyError:
        try:
            # The file etym is not yet tracked
            metrics[dictionary][file_format][etym] = 1
        except KeyError:
            try:
                # The file format is not yet tracked
                metrics[dictionary][file_format] = {etym: 1}
            except KeyError:
                # The dictionary is not yet tracked
                metrics[dictionary] = {file_format: {etym: 1}}

    write(metrics)


def read() -> Metrics:
    try:
        content = constants.METRICS.read_text()
    except FileNotFoundError:
        return {}

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        log.exception("The metrics file seems dead! Content: %r", content)
        return {}


def write(metrics: Metrics) -> None:
    constants.METRICS.write_text(
        json.dumps(
            metrics,
            ensure_ascii=False,
            check_circular=False,
            sort_keys=True,
            indent=4,
        )
    )
