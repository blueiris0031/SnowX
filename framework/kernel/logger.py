import logging
from logging.handlers import RotatingFileHandler

from .config import KernelConfig
from ..kernel.path import get_log_path
from ..utils.singleton import configured_singleton


@configured_singleton
class LoggerManager:
    @staticmethod
    def _check_level(level: int | str | None, default: int = logging.NOTSET) -> int:
        if isinstance(level, int):
            return level
        if level is None:
            return default
        return logging.getLevelNamesMapping().get(level, None) or default

    def _set_default_level(self, level: int | str) -> None:
        self._default_level = self._check_level(level)

    @property
    def default_level(self) -> int:
        return self._default_level

    def _set_default_formatter(self, fmt: str) -> None:
        self._default_formatter = logging.Formatter(fmt)

    @property
    def default_formatter(self) -> logging.Formatter:
        return self._default_formatter

    def _set_handler_level(self, t_handler: logging.Handler, level: int | str | None = None) -> None:
        t_handler.setLevel(self._check_level(level))

    def _set_handler_formatter(self, t_handler: logging.Handler, formatter: logging.Formatter | None = None) -> None:
        if formatter is None:
            t_handler.setFormatter(self.default_formatter)
        else:
            t_handler.setFormatter(formatter)

    def _set_handler(
            self,
            t_handler: logging.Handler,
            level: int | str | None = None,
            formatter: logging.Formatter | None = None,
    ) -> None:
        self._set_handler_level(t_handler, level)
        self._set_handler_formatter(t_handler, formatter)

    def _new_stream_handler(
            self,
            level: int | str | None = None,
            formatter: logging.Formatter | None = None,
    ) -> logging.StreamHandler:
        new_handler = logging.StreamHandler()
        self._set_handler(new_handler, level, formatter)
        return new_handler

    def _set_default_stream_handler(self) -> None:
        self._default_stream_handler = self._new_stream_handler()

    @property
    def default_stream_handler(self) -> logging.StreamHandler:
        return self._default_stream_handler

    def _new_file_handler(
            self,
            name: str,
            level: int | str | None = None,
            formatter: logging.Formatter | None = None,
    ) -> logging.handlers.RotatingFileHandler:
        new_handler = logging.handlers.RotatingFileHandler(
            get_log_path(name) / "log.txt",
            maxBytes=self._filelog_maxbytes,
            backupCount=self._filelog_count,
            encoding="utf-8",
            delay=True,
            mode="a",
        )
        self._set_handler(new_handler, level, formatter)
        return new_handler

    def __init__(self):
        config_manager = KernelConfig()

        self._set_default_level(config_manager.get_config("LOGGER_LEVEL", "WARNING"))
        self._set_default_formatter(config_manager.get_config("LOG_FORMAT", "[%(levelname)s] %(asctime)s [%(name)s<%(filename)s:%(lineno)d>] - %(message)s"))
        self._set_default_stream_handler()

        self._enable_consolelog = config_manager.get_config("ENABLE_CONSOLELOG", True)
        self._enable_filelog = config_manager.get_config("ENABLE_FILELOG", False)
        self._filelog_maxbytes = config_manager.get_config("FILELOG_MAXBYTES", 3 * 1024 * 1024)
        self._filelog_count = config_manager.get_config("FILELOG_COUNT", 5)

        self._file_handler_map: dict[str, logging.handlers.RotatingFileHandler] = {}
        self._root_logger_map: dict[str, logging.Logger] = {}

    def _get_stream_handler(
            self,
            level: int | str | None = None,
            formatter: logging.Formatter | None = None,
    ) -> logging.Handler:
        if level is None and formatter is None:
            return self.default_stream_handler

        return self._new_stream_handler(level, formatter)

    def _get_file_handler(
            self,
            name: str,
            level: int | str | None = None,
            formatter: logging.Formatter | None = None,
    ) -> logging.handlers.RotatingFileHandler:
        if name in self._file_handler_map:
           return self._file_handler_map[name]

        return self._file_handler_map.setdefault(name, self._new_file_handler(name, level, formatter))

    def _set_logger(
            self,
            name: str,
            t_logger: logging.Logger,
            level: int | str | None = None,
            add_stream_handler: bool = True,
            stream_handler_level: int | str | None = None,
            stream_handler_formatter: logging.Formatter | None = None,
            add_file_handler: bool = False,
            file_handler_level: int | str | None = None,
            file_handler_formatter: logging.Formatter | None = None,
    ) -> None:
        t_logger.setLevel(self._check_level(level, self.default_level))

        t_logger.handlers.clear()
        if add_stream_handler:
            t_logger.addHandler(self._get_stream_handler(stream_handler_level, stream_handler_formatter))
        if add_file_handler:
            t_logger.addHandler(self._get_file_handler(name, file_handler_level, file_handler_formatter))

    def _new_logger(self, name: str, *args, **kwargs) -> logging.Logger:
        new_logger = logging.getLogger(name)
        self._set_logger(name, new_logger, *args, **kwargs)
        return new_logger

    def _get_root_logger(self, name: str, *args, **kwargs) -> logging.Logger:
        if name in self._root_logger_map:
            return self._root_logger_map[name]

        new_logger = self._new_logger(name, *args, **kwargs)
        return self._root_logger_map.setdefault(name, new_logger)

    def _get_sub_logger(self, name: str, level: int | str | None = None) -> logging.Logger:
        return self._new_logger(name, level, add_stream_handler=False)

    def add_root_logger(
            self,
            name: str,
            level: int | str | None = None,
            add_stream_handler: bool | None = None,
            stream_handler_level: int | str | None = None,
            stream_handler_formatter: logging.Formatter | None = None,
            add_file_handler: bool | None = None,
            file_handler_level: int | str | None = None,
            file_handler_formatter: logging.Formatter | None = None,
    ) -> None:
        """
        Add a root logger.
        :param name: Logger name
        :param level: Logger level
        :param add_stream_handler: Whether to add a stream handler. If this parameter is None, use the configured value.
        :param stream_handler_level: Stream handler level.
        :param stream_handler_formatter: Stream handler formatter.
        :param add_file_handler: Whether to add a file handler. If this parameter is None, use the configured value.
        :param file_handler_level: File handler level.
        :param file_handler_formatter: File handler formatter.
        :return: None
        """
        if "." in name:
            raise ValueError("Root logger name must not contain '.'")

        self._get_root_logger(
            name,
            level,
            self._enable_consolelog if add_stream_handler is None else add_stream_handler,
            stream_handler_level,
            stream_handler_formatter,
            self._enable_filelog if add_file_handler is None else add_file_handler,
            file_handler_level,
            file_handler_formatter,
        )

    def get_logger(self, name: str, level: int | str | None = None) -> logging.Logger:
        """
        Get an automatically configured logger.
        :param name: Logger name.
        :param level: Logger level.
        :return: Logger object.
        """
        if not name:
            raise ValueError("Logger name must not be empty")

        name_list = name.split(".", maxsplit=1)
        self.add_root_logger(name_list[0], level)

        if len(name_list) == 1:
            return self._get_root_logger(name, level)

        return self._get_sub_logger(name)


__all__ = [
    "LoggerManager",
]
