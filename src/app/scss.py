import logging
import subprocess

logger = logging.getLogger(__name__)


def compile_scss() -> None:
    ret_code = subprocess.call(["sass", "scss:static/css", "--style", "compressed"], shell=True)
    if ret_code != 0:
        logger.error(f"SCSS compilation finished with non-zero return code ({ret_code})")
