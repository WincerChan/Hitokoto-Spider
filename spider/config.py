from typing import Dict
from collections import abc


class FrozenJSON:
    def __init__(self, args):
        states = dict()
        for key, value in args.items():
            if isinstance(value, abc.Mapping):
                states[key] = FrozenJSON(value)
            elif isinstance(value, abc.MutableSequence):
                states[key] = [FrozenJSON(item) for item in value]
            else:
                states[key] = value
        super().__setattr__('_FrozenJSON__states', states)

    def __getattribute__(self, name):
        return super().__getattribute__(name)

    def __setattr__(self, key, value):
        print(f"WARNING: You should not mutate any value of FrozenJSON."
              f"Change `{key}` field in argument dict, then instantiate FrozenJSON")


