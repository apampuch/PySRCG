from collections import OrderedDict


class CalculableOrderedDict(OrderedDict):
    def __init__(self):
        super().__init__()

    def __getitem__(self, item):
        ret = super().__getitem__(item)

        if callable(ret):
            return ret()
        else:
            return ret


# testing
if __name__ == "__main__":
    def test_func():
        return 3

    def test_func_w_arg(x):
        return x

    cod = CalculableOrderedDict()
    cod["a"] = 1
    cod["b"] = lambda: 2
    cod["c"] = test_func
    cod["d"] = test_func_w_arg

    print(cod["a"])
    print(cod["b"])
    print(cod["c"])
    print(cod["d"])
