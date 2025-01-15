import logging
import subprocess
import shutil

logger = logging.getLogger(__name__)


def compile_scss() -> None:
    ret_code = subprocess.call([shutil.which("sass"), "scss:static/css", "--style", "compressed"])
    if ret_code != 0:
        logger.error(f"SCSS compilation finished with non-zero return code ({ret_code})")
