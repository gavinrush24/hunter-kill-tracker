def diamond_rate_text(kills, diamonds):
    """Return the diamond rate as display text, e.g. '1 every 50.00'."""
    if diamonds == 0:
        return "None yet"
    return f"1 every {kills / diamonds:.2f}"