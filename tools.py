from random import choice

class EmptySequenceError(BaseException):
    pass

class AnimTools:
    '''Helper class with common tools for animating scenes'''

    class Sequence:
        def __init__(self, parent, name):
            self.parent = parent
            self.name = name
            self.pre_actions = []
            self.run_preactions = False
            self.actions = []
            self.looper = self.make_looper()

        def __call__(self, *args, **kwargs):
            self.once(*args, **kwargs)

        def __repr__(self):
            return f"Sequence('{self.name}')"

        def replace(self, sequence_name, *args, **kwargs):
            self.looper.replace(self.parent.sequence(sequence_name), *args, **kwargs)
            return self.parent.sequence(sequence_name)

        def make_looper(self):

            @Loopable
            def looper():
                if len(self.actions) == 0:
                    raise EmptySequenceError(f"sequence '{self.name}' is empty. Did you mistype the name?")

                if self.run_preactions:
                    self.run_preactions = False

                    for action in self.pre_actions:
                        action()

                for action in self.actions:
                    action()

            return looper

        def use_pre_actions(self, value):
            self.run_preactions = value
            return self

        def add_pre_action(self, action):
            self.pre_actions.append(action)
            return self

        def add_action(self, action):
            self.actions.append(action)
            return self

        def random(self, *args, **kwargs):
            self.actions.append(self.parent.random(*args, **kwargs))
            return self

        def cycle(self, *args, **kwargs):
            self.actions.append(self.parent.cycle(*args, **kwargs))
            return self

        def pulse(self, *args, **kwargs):
            self.actions.append(self.parent.pulse(*args, **kwargs))
            return self

        def transition(self, *args, **kwargs):
            self.actions.append(self.parent.transition(*args, **kwargs))
            return self

        def full_transition(self, *args, **kwargs):
            self.actions.append(self.parent.full_transition(*args, **kwargs))
            return self

        def reverse_transition(self, *args, **kwargs):
            self.actions.append(self.parent.reverse_transition(*args, **kwargs))
            return self

        def wait(self, time):
            self.actions.append(lambda: wait(time))
            return self

        def set(self, *args, **kwargs):
            self.actions.append(lambda: self.parent.set(*args, **kwargs))
            return self

        def run_sequence(self, sequence_name):
            self.actions.append(self.parent.sequence(sequence_name))
            return self

        def loop(self, *args, **kwargs):
            return self.looper.loop(*args, **kwargs)

        def loop_background(self, *args, **kwargs):
            return self.looper.loop_background(*args, **kwargs)

        def stop(self, *args, **kwargs):
            return self.looper.stop(*args, **kwargs)

        def once(self, *args, **kwargs):
            return self.looper.once(*args, **kwargs)

        def twice(self, *args, **kwargs):
            return self.looper.twice(*args, **kwargs)

    def __init__(self, settings: dict):
        '''Creates an Animtools instance
        
        Arguments:
            settings {dict} -- a dictionary of setting:options pairs representing all the settings available in your scene
        '''

        self.settings = settings
        self.loopers = []
        self.sequences = {}

    @property
    def model(self):
        '''A convienience property to access the model for primarily internal use
        
        Returns:
            Model -- The scenes Model object
        '''
        return get_model()

    def smart_range(self, From, To):
        '''range function that is inclusive on both sides and also automatically decreases when To < From'''

        if To > From:
            yield from range(From, To + 1)
        else:
            yield from range(From, To - 1, -1)

    def init_with_first(self):
        '''Sets each setting of the scene with the first option provided to AnimTools'''

        for setting, options in self.settings.items():
            self.model[setting][options[0]]

        return self

    def random(self, setting):

        @Loopable
        def random_selector():
            option = choice(self.settings[setting])

            set_state(setting, option)

        self.loopers.append(random_selector)

        return random_selector

    def cycle(self, setting, frame_time, down_time=0):

        @Loopable
        def cycler():
            for option in self.settings[setting]:
                self.model[setting][option]
                wait(frame_time)

            wait(down_time)

        self.loopers.append(cycler)

        return cycler

    def pulse(self, setting, frame_time, hold_time=0, down_time=0):

        @Loopable
        def pulser():
            for option in self.settings[setting]:
                self.model[setting][option]
                wait(frame_time)

            wait(hold_time)

            for option in self.settings[setting][-2:0:-1]:
                self.model[setting][option]
                wait(frame_time)

            wait(down_time)
        
        self.loopers.append(pulser)

        return pulser

    def transition(self, setting, From, To, frame_time):

        settings = self.settings[setting]

        from_index = From if isinstance(From, int) else settings.index(From)
        to_index = To if isinstance(To, int) else settings.index(To)

        @Loopable
        def transitioner():

            for index in self.smart_range(from_index, to_index):
                setting_value = settings[index]

                self.model[setting][setting_value]

                wait(frame_time)

        self.loopers.append(transitioner)

        return transitioner

    def full_transition(self, setting, frame_time):
        From = 0
        To = len(self.settings[setting]) - 1

        return self.transition(setting, From, To, frame_time)

    def reverse_transition(self, setting, frame_time):
        From = len(self.settings[setting]) - 1
        To = 0

        return self.transition(setting, From, To, frame_time)

    def loop_sequences_in_background(self, *sequences):

        for sequence_name in sequences:
            self.sequences[sequence_name].loop_background()

        return self

    def stop_and_wait_for(self, *sequences):
        target = time()

        wait(max(self.sequences[sequence_name].stop(target=target, should_wait=False) for sequence_name in sequences))

        return self

    def replace_sequences(self, sequence_mapping):
        target = time()

        for from_sequence, to_sequence in sequence_mapping.items():
            self.sequence(from_sequence).replace(to_sequence, target=target)

    def sequence(self, name):
        if name in self.sequences:
            return self.sequences[name]

        sequence = self.Sequence(self, name)

        self.sequences[name] = sequence
        return sequence

    def set(self, setting, value):
        settings = self.settings[setting]
        true_value = value if isinstance(value, str) else settings[value]

        self.model[setting][true_value]

        return self