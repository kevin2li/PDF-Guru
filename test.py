def my_decorator(arg1="Hello", arg2=123):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print("Decorator arguments:", arg1, arg2)
            result = func(*args, **kwargs)
            print("Decorator finished")
            return result
        return wrapper
    return decorator

@my_decorator()
def my_function(a: int = 1, b: int = 2):
    print("Function called")
    print(a+b)

@my_decorator("World")
def my_function2(s: str = "hello"):
    print("Function2 called")
    print(s)

my_function(a=2,b=4)
my_function2()