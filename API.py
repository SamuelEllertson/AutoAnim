
current_context = None

def wait(time):
    current_context.time += time

def time():
    return current_context.time

funcs_to_ignore = set()

def ignore(func):
    funcs_to_ignore.add(func)
    return func

def ignored():
    return funcs_to_ignore

def set_current_context(wrapped_func):
    global current_context

    current_context = wrapped_func

funcs_need_eval = set()

def get_waiting_funcs():
    return funcs_need_eval

class FuncWrapper():
    def __init__(self, func):
        self.func = func
        self.time = 0
        self.needs_eval = False

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __hash__(self):
        return hash(self.func)

    def loop(self, num, args=tuple(), kwargs=dict()):
        for _ in range(num):
            self.func(*args, **kwargs)

    def loop_background(self, num=None, args=tuple(), kwargs=dict()):
        self.time = current_context.time
        self.num = num
        self.args = args
        self.kwargs = kwargs
        self.needs_eval = True

        funcs_need_eval.add(self)

    def stop(self):

        if not self.needs_eval:
            return
        self.needs_eval = False

        global current_context
        end_time = current_context.time
        temp, current_context = current_context, self

        cycles = 0
        while time() < end_time:
            if self.num is not None and cycles >= self.num:
                break

            self.func(*self.args, **self.kwargs)

            cycles += 1

        current_context = temp

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
        self.selected_option = None

    def __getattr__(self, value):
        return self.OptionAdder(self, value)

    def __getitem__(self, value):
        return getattr(self, value)

    def add_option(self, option):
        self.temporal_dict.add_entry(option, time())

    def finish(self):
        self.add_option({})

    def __iter__(self):
        return iter(self.temporal_dict)

'''
@func_Wrapper
def blink():
    #close eyes
    _.eyes.close
    #print(f"closed eyes at {time()}")
    wait(5)
    #open eyes
    _.eyes.open
    #print(f"opened eyes at {time()}")
    wait(5)

@func_Wrapper
def breathe():
    blink.loop_background()
    
    #inhale
    _.lungs.full
    #print(f"inhale at {time()}")
    wait(10)

    #exhale
    _.lungs.normal
    #print(f"exhale at {time()}")
    wait(10)

    blink.stop()


@func_Wrapper
def main():
    breathe.loop_background()
    wait(40)
    breathe.stop()

current_context = main

main()
_.finish()

for state in _:
    print(state)
'''

