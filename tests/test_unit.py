import pytest
from code.validators import interval_before_delete


def test_interval():
    with pytest.raises(ValueError):
        interval_before_delete(0, 0, 0, 0)

    with pytest.raises(ValueError):
        interval_before_delete(7, 0, 0, 0)

    with pytest.raises(ValueError):
        interval_before_delete(0, 0, -1, 0)

    with pytest.raises(ValueError):
        interval_before_delete(0, 24, 0, 0)

    assert interval_before_delete(1, 0, 0, 0) == "1 days 0 hours 0 minutes 0 seconds"
    assert interval_before_delete(6, 23, 59, 59) == "6 days 23 hours 59 minutes 59 seconds"
    assert interval_before_delete(0, 0, 0, 1) == "0 days 0 hours 0 minutes 1 seconds"
    assert interval_before_delete(1, 5, 5, 30) == "1 days 5 hours 5 minutes 30 seconds"
    

if __name__ == '__main__':
    pytest.main()
