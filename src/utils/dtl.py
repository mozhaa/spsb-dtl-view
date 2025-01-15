import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import gspread

from src.env import getenv

from .url import as_embed
from .utils import msg

logger = logging.getLogger(__name__)

JSON = Dict[str, Any]
DATE_FORMAT = r"%Y-%m-%d %H:%M:%S"
TIERS = ["S+", "S", "A", "B", "C", "D", "E"]


class Table:
    def __init__(self, table: List[List[str]]) -> None:
        self.table = table

    def get_start_ij(self) -> Tuple[int, int]:
        for i in range(len(self.table)):
            for j in range(len(self.table[i])):
                elem = self.table[i][j]
                if elem == "S+":
                    return i, j
        raise RuntimeError("Couldn't find table left-top corner")

    def get(self, i: int, j: int) -> Optional[str]:
        if len(self.table) > i and len(self.table[i]) > j:
            return self.table[i][j]
        return None


def load_from_cache() -> JSON:
    with open(getenv("cache_fp"), "r", encoding="utf-8") as file:
        obj = json.load(file)
    return obj


def dump_to_cache(dtl: JSON) -> None:
    logger.info("Saving DTL to cache...")
    with open(getenv("cache_fp"), "w+", encoding="utf-8") as file:
        json.dump(dtl, file)


def fetch_from_spreadsheets() -> JSON:
    logger.info("Fetching DTL from spreadsheets...")
    gc = gspread.api_key(getenv("api_key"))
    sh = gc.open_by_key(getenv("spreadsheet_id"))
    table = Table(sh.sheet1.get("A1:G100"))

    result = {tier: [] for tier in TIERS}
    i, j = table.get_start_ij()
    while table.get(i, j) is not None:
        new_item = {
            "tier": table.get(i, j),
            "nickname": table.get(i, j + 2),
            "video_direct": table.get(i, j + 3),
            "video_embed": as_embed(table.get(i, j + 3)) or "",
        }
        if new_item["tier"] not in TIERS:
            raise RuntimeError(f"Invalid tier: '{new_item["tier"]}'")
        result[new_item["tier"]].append(new_item)
        i += 1

    return {"updated_at": datetime.now().strftime(DATE_FORMAT), "data": result}


def get_dtl() -> JSON:
    dtl = None
    try:
        dtl = load_from_cache()
    except Exception as e:
        logger.info(f"Couldn't parse DTL from cache, fetching from spreadsheets.\nException:\n{msg(e)}")

    if dtl is None or datetime.now() - datetime.strptime(dtl["updated_at"], DATE_FORMAT) > getenv("update_interval"):
        try:
            updated_dtl = fetch_from_spreadsheets()
            dump_to_cache(updated_dtl)
            return updated_dtl
        except Exception as e:
            logger.error(f"Failed to fetch DTL from spreadsheets.\nException:\n{msg(e)}")

    if dtl is None:
        raise RuntimeError("Failed to get DTL both from cache and from spreadsheets")
    return dtl


def update_dtl() -> JSON:
    dump_to_cache(fetch_from_spreadsheets())
