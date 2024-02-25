import logging
import os
from logging.handlers import TimedRotatingFileHandler

LOG_PATH: str = os.path.join(os.getcwd(), "logs", "tickers")
LOG_FORMAT = logging.Formatter(
    fmt="\n\n%(asctime)s\n%(levelname)s - %(name)s\n%(filename)s>'%(funcName)s'>%(lineno)d\n%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class DuplicateFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.seen_messages = set()
        self.message_count = 0
        self.clear_threshold = 100  # Clear the set after every 100 messages

    def filter(self, record):
        self.message_count += 1
        if self.message_count >= self.clear_threshold:
            self.seen_messages.clear()
            self.message_count = 0

        # Extract relevant parts for comparison
        message_parts = record.msg.split("\n")
        if len(message_parts) >= 5:
            comparison_msg = " ".join(
                [
                    message_parts[0],  # Bot's symbol nickname
                    message_parts[4],  # Exception message
                    record.filename,  # Filename where the log was generated
                    record.funcName,  # Function name where the log was generated
                    str(record.lineno),  # Line number where the log was generated
                ]
            )
        else:
            comparison_msg = (
                record.msg
            )  # Fallback to the entire message if the format doesn't match

        if comparison_msg in self.seen_messages:
            return False
        self.seen_messages.add(comparison_msg)
        return True


def create_bot_logger(bot_nickname: str) -> logging.Logger:
    """
    Creates and configures a logger for a Discord bot.
    """

    bot_manager_fh = TimedRotatingFileHandler(
        filename=f"{LOG_PATH}/tickers.log",
        when="W1",
        backupCount=0,
    )
    bot_manager_fh.setLevel(level=logging.INFO)
    bot_manager_fh.setFormatter(fmt=LOG_FORMAT)

    bot_manager_error_fh = TimedRotatingFileHandler(
        filename=f"{LOG_PATH}/tickers_error.log",
        when="W1",
        backupCount=0,
    )
    bot_manager_error_fh.setLevel(level=logging.WARNING)
    bot_manager_error_fh.setFormatter(fmt=LOG_FORMAT)
    bot_manager_error_fh.addFilter(DuplicateFilter())

    bot_logger: logging.Logger = logging.getLogger(name=f"bot-{bot_nickname}")
    bot_logger.setLevel(level=logging.INFO)
    bot_logger_fh = TimedRotatingFileHandler(
        filename=f"{LOG_PATH}/individual/{bot_nickname}.log",
        when="W1",
        backupCount=0,
    )
    bot_logger_fh.setFormatter(fmt=LOG_FORMAT)

    bot_logger.addHandler(hdlr=bot_manager_error_fh)
    bot_logger.addHandler(hdlr=bot_manager_fh)
    bot_logger.addHandler(hdlr=bot_logger_fh)

    return bot_logger


def create_controller_logger() -> logging.Logger:
    """
    Creates and configures a logger for bot controller
    """

    controller_logger: logging.Logger = logging.getLogger(name="Controller")
    controller_fh = TimedRotatingFileHandler(
        filename=f"{LOG_PATH}/controller.log",
        when="W1",
        backupCount=0,
    )
    controller_fh.setLevel(level=logging.INFO)
    controller_fh.setFormatter(fmt=LOG_FORMAT)
    controller_logger.addHandler(hdlr=controller_fh)

    return controller_logger
