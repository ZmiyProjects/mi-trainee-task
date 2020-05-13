def interval_before_delete(days: int, hours: int, minutes: int, seconds: int) -> str:
    """
    :param days: Дни до удаления, в диапозоне от 0 до 6
    :param hours: Часы до удаления, в диапозоне от 0 до 23
    :param minutes: Минуты до удаления, в диапозоне от 0 до 59
    :param seconds: Секунды до удаления, в диапозоне от 0 до 59
    :return:
    """
    if all(i == 0 for i in [days, hours, minutes, seconds]):
        raise ValueError
    if not 0 <= days <= 6:
        raise ValueError
    if not 0 <= hours <= 23:
        raise ValueError
    if not 0 <= minutes <= 59:
        raise ValueError
    if not 0 <= seconds <= 59:
        raise ValueError
    return f"{days} days {hours} hours {minutes} minutes {seconds} seconds"