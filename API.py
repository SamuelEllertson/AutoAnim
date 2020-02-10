
class EndLoopException(StopIteration):
    pass

def endloop():
    raise EndLoopException("endloop called")

current_context = None

def get_current_context():
    global current_context

    return current_context

def set_current_context(wrapped_func):
    global current_context

    print("current context is ", wrapped_func)

    current_context = wrapped_func

def wait(time):
    get_current_context().time += time

def time():
    return get_current_context().time

funcs_to_ignore = set()

def ignore(func):
    funcs_to_ignore.add(func)
    return func

def ignored():
    return funcs_to_ignore

funcs_need_eval = set()

def get_waiting_funcs():
    return funcs_need_eval

class Loopable():
    def __init__(self, func):
        self.func = func
        self.time = 0
        self.needs_eval = False

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __hash__(self):
        return hash(self.func)

    def __repr__(self):
        return f"Loopable(time={self.time}, func={self.func!r})"

    def once(self, *args, **kwargs):
        self.__call__(*args, **kwargs)
        return self

    def twice(self, *args, **kwargs):
        self.__call__(*args, **kwargs)
        self.__call__(*args, **kwargs)
        return self

    def loop(self, num, args=tuple(), kwargs=dict()):
        try:
            for _ in range(num):
                self.func(*args, **kwargs)
        except EndLoopException:
            pass

        return self

    def loop_background(self, num=None, args=tuple(), kwargs=dict()):
        self.time = current_context.time
        self.num = num
        self.args = args
        self.kwargs = kwargs
        self.needs_eval = True

        funcs_need_eval.add(self)

        return self

    def stop(self, target=None):

        if not self.needs_eval:
            return
        self.needs_eval = False

        global current_context

        #target_end_time = current_context.time
        #temp, current_context = current_context, self

        target_end_time = target or time()
        previous_context = get_current_context()
        set_current_context(self)

        print("target_end_time ", target_end_time)
        print("loopable time: ", time())

        cycles = 0
        try:
            while time() < target_end_time:

                if self.num is not None and cycles >= self.num:
                    break

                self.func(*self.args, **self.kwargs)

                cycles += 1

        except EndLoopException:
            pass
        finally:
            true_end_time = time()

            print("loopable time: ", time())
            set_current_context(previous_context)

        return true_end_time - target_end_time

from TemporalDict import TemporalDict

class Model:

    class OptionAdder:
        def __init__(self, model, option):
            self.model = model
            self.option = option

        def __getattr__(self, value):
            self.model.add_option({self.option: value})

        def __getitem__(self, value):
            return getattr(self, value)

    def __init__(self):
        self.temporal_dict = TemporalDict()

    def __getattr__(self, value):
        return self.OptionAdder(self, value)

    def __getitem__(self, value):
        return getattr(self, value)

    def add_option(self, option):

        print(f"setting {option!r} at time {time()}")

        self.temporal_dict.add_entry(option, time())

    def finish(self):
        self.add_option({})


_model = Model()

def get_model():
    return _model