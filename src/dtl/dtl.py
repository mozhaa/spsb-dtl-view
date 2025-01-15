import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import List, Optional, Tuple, Dict

import gspread

from src.env import getenv

logger = logging.getLogger(__name__)

DATE_FORMAT = r"%Y-%m-%d %H:%M:%S"
TIERS = ["S+", "S", "A", "B", "C", "D", "E"]


@dataclass
class DTLItem:
    tier: str
    position: int
    nickname: str
    videolink: str


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


class DTL:
    @property
    def items_by_tiers(self) -> Dict[str, List[DTLItem]]:
        result = {tier: [] for tier in TIERS}
        for item in self.items:
            result[item.tier].append(item)
            if len(result[item.tier]) != item.position:
                logging.warning(
                    f"DTL data is incorrect! Tier members must go in order of their tier positions ({item})"
                )
        return result

    @property
    def items(self) -> List[DTLItem]:
        items, updated_at = None, None
        try:
            items, updated_at = self._read_from_cache()
        except Exception as e:
            logger.info(f"Couldn't parse DTL from cache, fetching from spreadsheets. Exception:\n{e}")

        if updated_at is None or datetime.now() - updated_at > getenv("update_interval"):
            try:
                new_items = self._read_from_sheet()
                self._save_to_cache(new_items)
                return new_items
            except Exception as e:
                logger.error(f"Failed to fetch DTL from spreadsheets. Exception:\n{e}")

        if items is None:
            raise RuntimeError("Failed to get DTL both from cache and from spreadsheets")
        return items

    def update(self) -> None:
        self._save_to_cache(self._read_from_sheet())

    def _read_from_cache(self) -> Tuple[List[DTLItem], datetime]:
        with open(getenv("cache_fp"), "r", encoding="utf-8") as file:
            obj = json.load(file)
        return [DTLItem(**item) for item in obj["items"]], datetime.strptime(obj["updated_at"], DATE_FORMAT)

    def _save_to_cache(self, items: List[DTLItem]) -> None:
        logger.info("Saving DTL to cache...")
        obj = {"updated_at": datetime.now().strftime(DATE_FORMAT), "items": list(map(asdict, items))}
        with open(getenv("cache_fp"), "w+", encoding="utf-8") as file:
            json.dump(obj, file)

    def _read_from_sheet(self) -> List[DTLItem]:
        logger.info("Fetching DTL from spreadsheets...")
        gc = gspread.api_key(getenv("api_key"))
        sh = gc.open_by_key(getenv("spreadsheet_id"))
        table = Table(sh.sheet1.get("A1:G100"))

        items = []
        i, j = table.get_start_ij()
        while table.get(i, j) is not None:
            items.append(
                DTLItem(
                    tier=table.get(i, j),
                    position=int(table.get(i, j + 1)),
                    nickname=table.get(i, j + 2),
                    videolink=table.get(i, j + 3),
                )
            )
            if items[-1].tier not in TIERS:
                raise RuntimeError(f"Invalid tier: '{items[-1].tier}'")
            i += 1

        return items
