import logging
from pathlib import PurePosixPath
from typing import Optional
from urllib.parse import parse_qs, urlparse, urlunparse

from .utils import msg

logger = logging.getLogger(__name__)


def pure_netloc(netloc: str) -> str:
    if netloc.startswith("www."):
        return netloc[4:]
    return netloc


def as_embed(url: str) -> Optional[str]:
    parsed_url = urlparse(url)
    netloc = pure_netloc(parsed_url.netloc)

    try:
        if netloc in ["youtube.com", "youtu.be"]:
            path = PurePosixPath(parsed_url.path)
            if netloc == "youtube.com":
                if len(path.parts) > 1:
                    if path.parts[1] == "shorts":
                        video_id = path.parts[2]
                    elif path.parts[1] == "watch":
                        video_id = parse_qs(parsed_url.query)["v"][0]
                    else:
                        raise RuntimeError(f"Unknown path.parts[0]={path.parts[1]}")
                else:
                    raise RuntimeError("Empty path in youtube url")
            else:
                video_id = path.parts[1]
            return f"https://www.youtube.com/embed/{video_id}"
        elif netloc == "drive.google.com":
            return urlunparse(parsed_url._replace(path=parsed_url.path.replace("/view", "/preview")))
        else:
            raise RuntimeError(f"Unknown netloc={netloc}")
    except Exception as e:
        logger.warning(f"Failed to convert '{url}' to embed.\nException: {msg(e)}")
