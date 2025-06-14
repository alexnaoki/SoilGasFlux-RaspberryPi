import time

def log_errors_to_file(file_path):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                with open(file_path, "a") as file:
                    print(time.localtime())
                    t = time.localtime()
                    log_datetime = f'{t[0]}-{t[1]}-{t[2]} {t[3]}:{t[4]}:{t[5]}'
                    file.write(f"[{log_datetime}]\tError in function {func.__name__}: {str(e)}\n")
                    # file.write(f"teste Error in function {func.__name__}: {str(e)}\n")
                raise
        return wrapper
    return decorator

def log_exception_to_file(error_message, file_path):
    try:
        with open(file_path, "a") as file:
            t = time.localtime()
            log_datetime = f'{t[0]}-{t[1]}-{t[2]} {t[3]}:{t[4]}:{t[5]}'
            file.write(f"[{log_datetime}]\t{error_message}\n")
            print(f"Error logged: {error_message}")
    except Exception as e:
        print(f'Failed to log error: {e}')
        print(f'Original error: {error_message}')


### EXAMPLE ###
@log_errors_to_file('error.log')
def my_function():
    a = 20/0
    pass

if __name__ == '__main__':
    my_function()