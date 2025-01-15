def msg(e: Exception) -> str:
    return getattr(e, "msg", None) or getattr(e, "message", str(e))
