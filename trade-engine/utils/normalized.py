def normalized(symbol: str) -> str:
    """
    Normalize trading symbol to uppercase and validate length.

    Args:
        symbol: Trading symbol to normalize
    """
    if len(symbol) < 1 or len(symbol) > 20:
        raise ValueError("Symbol length must be between 1 and 20 characters.")

    return symbol.upper()
