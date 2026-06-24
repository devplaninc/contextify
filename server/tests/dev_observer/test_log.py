import logging

from dev_observer.log import PlainTextEncoder, StructuredMessage, configure_logging


def test_plain_text_encoder_omits_color_by_default():
    text = PlainTextEncoder().encode(
        StructuredMessage("Checking periodic processing", running=0, concurrency=15)
    )

    assert "\033" not in text
    assert text == "Checking periodic processing [running]=0 [concurrency]=15"


def test_configure_logging_defaults_to_info_and_splits_streams(capsys, monkeypatch):
    root_logger = logging.getLogger()
    old_handlers = root_logger.handlers[:]
    old_level = root_logger.level

    try:
        monkeypatch.delenv("LOG_LEVEL", raising=False)
        configure_logging()

        logger = logging.getLogger("dev_observer.processors.periodic")
        logger.debug("debug msg")
        logger.info("info msg")
        logger.error("error msg")

        captured = capsys.readouterr()
    finally:
        root_logger.handlers.clear()
        root_logger.handlers.extend(old_handlers)
        root_logger.setLevel(old_level)

    assert "debug msg" not in captured.out
    assert "debug msg" not in captured.err
    assert "INFO:dev_observer.processors.periodic:info msg" in captured.out
    assert "ERROR:dev_observer.processors.periodic:error msg" in captured.err
    assert "error msg" not in captured.out


def test_uvicorn_logs_use_configured_root_streams(capsys, monkeypatch):
    import uvicorn

    root_logger = logging.getLogger()
    uvicorn_loggers = [
        logging.getLogger("uvicorn"),
        logging.getLogger("uvicorn.error"),
        logging.getLogger("uvicorn.access"),
        logging.getLogger("uvicorn.asgi"),
    ]
    old_root_handlers = root_logger.handlers[:]
    old_root_level = root_logger.level
    old_uvicorn_state = [
        (logger, logger.handlers[:], logger.level, logger.propagate)
        for logger in uvicorn_loggers
    ]

    try:
        monkeypatch.delenv("LOG_LEVEL", raising=False)
        for logger in uvicorn_loggers:
            logger.handlers.clear()
            logger.propagate = True
        configure_logging()

        uvicorn.Config(
            "dev_observer.server.main:app",
            log_level="info",
            log_config=None,
        )

        logger = logging.getLogger("uvicorn.error")
        logger.info("server started")
        logger.error("server failed")

        captured = capsys.readouterr()
    finally:
        root_logger.handlers.clear()
        root_logger.handlers.extend(old_root_handlers)
        root_logger.setLevel(old_root_level)
        for logger, handlers, level, propagate in old_uvicorn_state:
            logger.handlers.clear()
            logger.handlers.extend(handlers)
            logger.setLevel(level)
            logger.propagate = propagate

    assert "INFO:uvicorn.error:server started" in captured.out
    assert "server started" not in captured.err
    assert "ERROR:uvicorn.error:server failed" in captured.err
    assert "server failed" not in captured.out
