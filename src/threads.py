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
    Name must be a subset of a valid filename.
    """
    def __init__(
        self,
        group: None = None,
        target: Callable[..., object] | None = None,
        name: str | None = None,
        args: Iterable[Any] = ...,
        kwargs: Mapping[str, Any] | None = None,
        *,
        daemon: bool | None = None,
        catch_and_log_exceptions: bool = True,
    ) -> None:

        # TODO: validate name as a suitable filename?
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.catch_and_log_exceptions = catch_and_log_exceptions

    def run(self):
        # TODO: have systemd be involved in restarting the app
        if self.catch_and_log_exceptions:
            try:
                super().run()
            except Exception as ex:
                log_traceback_to_file(ex, self.name)
        else:
            super().run()
