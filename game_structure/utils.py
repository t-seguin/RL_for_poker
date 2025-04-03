def convert_amount_in_bb(amount: float, bb: float) -> float:
    """Convert an amount in big blinds"""
    if amount == -1:
        return -1
    else:
        return amount / bb
