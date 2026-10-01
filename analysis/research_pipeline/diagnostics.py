"""Persist every fit outcome, including warnings emitted before failure/interruption."""

import json
import os
import time
import warnings
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def record_fit(out: Path, **metadata):
    started = time.perf_counter()
    record = {**metadata, "status": "complete", "warnings": []}
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            yield record
        except BaseException as error:
            record.update(
                status=(
                    "interrupted"
                    if isinstance(error, (KeyboardInterrupt, SystemExit))
                    else "failed"
                ),
                error=str(error),
                error_type=type(error).__name__,
            )
            raise
        finally:
            record["elapsed_seconds"] = time.perf_counter() - started
            record["warnings"] = [str(w.message) for w in caught]
            with (out / "fit_log.jsonl").open("a") as stream:
                stream.write(json.dumps(record, allow_nan=False) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
