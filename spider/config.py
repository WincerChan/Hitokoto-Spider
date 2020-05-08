from typing import Dict
from collections import abc
from pathlib import Path
import spider


class FrozenJSON:
    def __new__(cls, args):
        if not isinstance(args, (abc.MutableSequence, abc.MutableMapping)):
            return args
        inst, states = super().__new__(cls), dict()
        for key, value in args.items():
            if isinstance(value, abc.Mapping):
                states[key] = FrozenJSON(value)
            elif isinstance(value, abc.MutableSequence):
                states[key] = [FrozenJSON(item) for item in value]
            else:
                states[key] = value
        super(FrozenJSON, inst).__setattr__('_FrozenJSON__states', states)
        super(FrozenJSON, inst).__setattr__('_FrozenJSON__string', str(args))
        return inst

    def __repr__(self):
        return f'FrozenJSON({self.__string})'

    def __getattr__(self, name):
        self.__states: Dict
        return self.__states.get(name)

    def __getattribute__(self, name):
        return super().__getattribute__(name)

    def __setattr__(self, key, value):
        print(f"WARNING: You should not mutate any value of FrozenJSON."
              f"Change `{key}` field in argument dict, then instantiate FrozenJSON")


class FrozenConfig(FrozenJSON):
    _CONFIG = "./config.yml"
    _Yaml = __import__('yaml')

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            config_json = cls._Yaml.load(open(cls._CONFIG), Loader=cls._Yaml.SafeLoader)
            cls._instance = super().__new__(cls, config_json)
        return cls._instance
