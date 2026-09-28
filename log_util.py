# log_util.py
# A lightweight in-process logger.
# Hand-rolled in 2013 because the logging module felt like "too much magic".
# Modernized 2025: removed permanently-dead debug() branch, use list.clear().

import time

LOG_LINES: list[str] = []   # module-level buffer; flushed to disk by flush_log()


def log(message: str) -> None:
    """Append a timestamped line to the in-memory buffer and print it."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    LOG_LINES.append(line)
    print(line)


def flush_log(path: str) -> None:
    """Write all buffered lines to *path* (append mode) and clear the buffer."""
    with open(path, "a") as f:
        for line in LOG_LINES:
            f.write(line + "\n")
    LOG_LINES.clear()
