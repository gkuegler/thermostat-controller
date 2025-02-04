import traceback
import os
import datetime
from collections.abc import Callable
from threading import Thread
from typing import Any, Iterable, Mapping


def log_traceback_to_file(ex: Exception, name):
    src_dir = os.path.dirname(os.path.realpath(__file__))
    t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    s = f"----- start '{name}' exception traceback -----\n"
    s += f"Time: {t}\n"
    s += "".join(traceback.format_exception(ex))
    s += f"----- end '{name}' exception traceback -------\n"

    with open(os.path.join(src_dir, f'traceback-{name}.log'), 'at') as f:
        f.write(s)


class ThreadWithExceptionLogging(Thread):
    """
    Name is used as part of a filename.
    """
    def __init__(self,
                 group: None = None,
                 target: Callable[..., object] | None = None,
                 name: str | None = None,
                 args: Iterable[Any] = ...,
                 kwargs: Mapping[str, Any] | None = None,
                 *,
                 daemon: bool | None = None) -> None:
        # TODO: validate name as a suitable filename
        super().__init__(group, target, name, args, kwargs, daemon=daemon)

    def run(self):
        try:
            super().run()
        except Exception as ex:
            log_traceback_to_file(ex, self.name)
