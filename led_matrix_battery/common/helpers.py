def percentage_to_value(percent, max_value=255):
    """
    Convert a percentage value to an actual value between 0 and `max_value`.

    Parameters:
        percent (float):
            The percentage value to convert.

        max_value (int, optional):
            The maximum value to which the percentage should be converted. Defaults to 255.

    Returns:
        int:
            The converted value between 0 and `max_value`.
    """
    if not isinstance(percent, (int, float)):
        raise TypeError(f'percent must be of type int or float, not {type(percent)}')

    if percent < 0 or percent > 100:
        raise ValueError(f'percent must be between 0 and 100, not {percent}')

    return int(round(percent * max_value / 100))
