import time


def prevent_429(func, time_to_wait=1, **kwargs):
    """Handles outside requests and waits if there's an error"""
    try:
        time.sleep(time_to_wait)
        return func(**kwargs)

    except Exception as e:
        while True:
            print(e)
            print(f"Error in {func.__name__}")
            time_to_wait = time_to_wait * 2
            print(f"Sleeping for {time_to_wait} seconds")
            time.sleep(time_to_wait)

            return prevent_429(func, time_to_wait, **kwargs)
