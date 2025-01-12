import logging

import uvicorn

from spsb_dtl_view.env import getenv

from .app import app

if __name__ == "__main__":
    logging.basicConfig(
        filename=getenv("log_fp"),
        filemode="a+",
        level=logging.INFO,
        format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
    console.setFormatter(formatter)
    logging.getLogger("root").addHandler(console)

    uvicorn.run(app, host=getenv("host"), port=getenv("port"))
