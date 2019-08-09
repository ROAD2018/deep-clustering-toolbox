__all__ = ["lazy_load_checkpoint"]
import functools
from copy import deepcopy as dcp


def lazy_load_checkpoint(func):
    @functools.wraps(func)
    def wrapped_init_(self, *args, **kwargs):
        _kwargs = dcp(kwargs)
        # setting all parent class with checkpoint=None
        if _kwargs.get("checkpoint_path"):
            _kwargs["checkpoint_path"] = None
        # perform normal __init__
        func(self, *args, **_kwargs)
        # reset the checkpoint_path
        self.checkpoint = kwargs.get("checkpoint_path")
        if self.checkpoint:
            print(f"the function to load checkpoint {func}")
            self.load_checkpoint_from_path(self.checkpoint)
        self.to(self.device)

    return wrapped_init_
