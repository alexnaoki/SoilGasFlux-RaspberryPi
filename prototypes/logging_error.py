import time
import components.rtc as rtc

# Global RTC object to be set from main.py
_rtc_clock = None

def set_rtc_clock(clock_rtc):
    """Set the RTC clock object for logging"""
    global _rtc_clock
    _rtc_clock = clock_rtc

def get_rtc_datetime():
    """Get formatted datetime string from RTC or fallback to system time"""
    try:
        if _rtc_clock is not None:
            rtc_time = _rtc_clock.datetime()
            return f'{rtc_time.year}-{rtc_time.month:02d}-{rtc_time.day:02d} {rtc_time.hour:02d}:{rtc_time.minute:02d}:{rtc_time.second:02d}'
        else:
            # Fallback to system time
            t = time.localtime()
            return f'{t[0]}-{t[1]:02d}-{t[2]:02d} {t[3]:02d}:{t[4]:02d}:{t[5]:02d}'
    except Exception:
        # Ultimate fallback to system time if RTC fails
        t = time.localtime()
        return f'{t[0]}-{t[1]:02d}-{t[2]:02d} {t[3]:02d}:{t[4]:02d}:{t[5]:02d}'

def log_errors_to_file(file_path):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                try:
                    with open(file_path, "a") as file:
                        log_datetime = get_rtc_datetime()
                        file.write(f"[{log_datetime}]\tERROR\t{func.__name__}\t{type(e).__name__}: {e}\n")
                except Exception:
                    pass
                print(f"Error logged: {func.__name__}: {e}")
                raise
        return wrapper
    return decorator

def log_exception_to_file(error_message, file_path="/sd/error.log",
                         level="ERROR", source=None):
    """
    Log an error message to a file with RTC timestamp, severity level,
    and optional source tag.
    """
    try:
        with open(file_path, "a") as file:
            log_datetime = get_rtc_datetime()
            src = f"\t{source}" if source else ""
            file.write(f"[{log_datetime}]\t{level}{src}\t{error_message}\n")
            print(f"{level}: {error_message}")
    except Exception as e:
        # If logging itself fails, print to console
        print(f"Failed to log error: {e}")
        print(f"Original error: {error_message}")

def logging_error(error_message, file_path="/sd/error.log"):
    """
    Alias for log_exception_to_file for compatibility
    """
    log_exception_to_file(error_message, file_path)


### EXAMPLE ###
@log_errors_to_file('error.log')
def my_function():
    a = 20/0
    pass

if __name__ == '__main__':
    my_function()