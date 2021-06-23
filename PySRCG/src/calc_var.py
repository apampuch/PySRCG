from tkinter import BooleanVar, DoubleVar, IntVar, StringVar, Tk


class CalcIntVar(IntVar):
    def __init__(self, *tk_vars):
        super().__init__()
        # THESE TWO NEED TO CORRESPOND TO EACH OTHER THANKS TO INTVARS NOT BEING SERIALIZABLE
        self.vars = []
        self.cb_names = []  # it has to remove by specific strings so we store these here

        def cb(var, index, mode):
            total = 0
            for v in self.vars:
                total += v.get()

            self.set(total)

        self.callback = cb

        for var in tk_vars:
            self.add(var)

        self.callback(None, None, None)

    def add(self, v):
        self.vars.append(v)
        self.cb_names.append(v.trace_add("write", self.callback))  # add and append cbname to list
        self.callback(None, None, None)

    def remove(self, v):
        try:
            # get index of cb name, remove that callback with that name, then delete from vars and cbnames by index
            i = self.vars.index(v)
            v.trace_remove("write", self.cb_names[i])
            self.vars.pop(i)
            self.cb_names.pop(i)
            self.callback(None, None, None)
        except ValueError:
            print("Not present")


if __name__ == "__main__":
    root = Tk()

    i1 = IntVar()
    i2 = IntVar()

    i1.set(3)
    i2.set(4)

    calc = CalcIntVar(i1, i2)

    # should be 7
    print(calc.get())

    i1.set(25)

    # should be 29
    print(calc.get())

    i2.set(-5)

    # should be 20
    print(calc.get())

    i3 = IntVar()
    i3.set(30)

    # should be 50
    calc.add(i3)
    print(calc.get())

    # should be 55
    calc.remove(i2)
    print(calc.get())
