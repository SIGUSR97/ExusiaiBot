def f():
    {}["a"]

try:
    d = {}
    d[1]
except KeyError as e:
    from pprint import pprint as pp
    # pp(dir(e))
    # pp(dir(e.__traceback__))
    # pp(e.__traceback__.tb_frame)
    # pp(dir(e.__traceback__.tb_frame))
    # pp(e.__traceback__.tb_frame.f_lineno)
    print(e.args)

