def get_logger(level: str):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(threadName)s - %(levelname)s - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "level": level,
                "class": "logging.StreamHandler",
                "formatter": "detailed",
            },
        },
        "loggers": {
            "src": {
                "handlers": ["console"],
                "level": level,
                "propagate": True,
            },
        },
    }
