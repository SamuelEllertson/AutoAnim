from TemporalDict import TemporalDict

class EndLoopException(StopIteration):
    pass

def endloop():
    raise EndLoopException

current_context = None

def get_current_context():
    global current_context
    return current_context

def set_current_context(wrapped_func):
    global current_context
    current_context = wrapped_func

def wait(time):
    get_current_context().time += time

def time():
    return get_current_context().time

waiting_funcs = set()

def get_waiting_funcs():
    global waiting_funcs
    return frozenset(waiting_funcs)

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
        self.func(*args, **kwargs)
        return self

    def twice(self, *args, **kwargs):
        self.func(*args, **kwargs)
        self.func(*args, **kwargs)
        return self

    def loop(self, num, args=tuple(), kwargs=dict()):
        try:
            for _ in range(num):
                self.func(*args, **kwargs)
        except EndLoopException:
            pass

        return self

    def loop_background(self, num=None, start_time=None, args=tuple(), kwargs=dict()):
        self.time = start_time or time()
        self.num = num
        self.args = args
        self.kwargs = kwargs

        waiting_funcs.add(self)

        return self

    def replace(self, loopable, num=None, target=None, args=tuple(), kwargs=dict()):
        true_target = target or time()

        self.stop(target=true_target, should_wait=False)

        loopable.loop_background(num, start_time=self.time, args=args, kwargs=kwargs)

        return loopable

    def stop(self, target=None, should_wait=True):

        if self not in waiting_funcs:
            return
        else:
            waiting_funcs.remove(self)

        target_end_time = target or time()

        #swap out the context
        previous_context = get_current_context()
        set_current_context(self)

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
            set_current_context(previous_context)

        overtime = true_end_time - target_end_time

        if should_wait:
            wait(overtime)
            return 0

        return overtime

class Model:

    def __init__(self, args):
        self.args = args
        self.temporal_dict = TemporalDict(args)
        self.aliases = {} # mapping from (setting, option) -> set((setting, option),...)

    def add_option(self, setting, option, recursively_handled=None):
        recursively_handled = recursively_handled or set()

        option_pair = (setting, option)

        if option_pair in recursively_handled:
            return
        else:
            recursively_handled.add(option_pair)

        self.temporal_dict.add_entry(setting, option, time())

        for aliased_setting, aliased_option in self.aliases.get(option_pair, []):
            self.add_option(aliased_setting, aliased_option, recursively_handled=recursively_handled)

    def add_alias(self, trigger_setting, trigger_option, aliased_setting, aliased_option):
        trigger_option_pair = (trigger_setting, trigger_option)
        aliased_option_pair = (aliased_setting, aliased_option)

        self.aliases.setdefault(trigger_option_pair, set()).add(aliased_option_pair)

    def finish(self):
        self.add_option(None, None)

_model = None

def init_api(args):
    global _model
    _model = Model(args)

def get_model():
    global _model
    return _model

def set_state(setting, option):
    get_model().add_option(setting, option)

def add_alias(trigger_setting, trigger_option, aliased_setting, aliased_option):
    get_model().add_alias(trigger_setting, trigger_option, aliased_setting, aliased_option)