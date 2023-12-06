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

### EXAMPLE ###
@log_errors_to_file('error.log')
def my_function():
    a = 20/0
    pass

if __name__ == '__main__':
    my_function()