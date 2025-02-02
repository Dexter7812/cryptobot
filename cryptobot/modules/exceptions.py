class APITimeoutError(Exception):
    """Výjimka pro timeout při volání API."""
    pass

class APIConnectionError(Exception):
    """Výjimka pro problémy s připojením k API."""
    pass

class OrderExecutionError(Exception):
    """Výjimka při selhání exekuce objednávky."""
    pass
