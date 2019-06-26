import warnings

import torch
from torch import Tensor
from apex import amp
from .general import Model
import contextlib


def to_Apex(model: Model, opt_level=None, verbosity=0, **kwargs) -> Model:
    # consider the apex model
    if opt_level is None:
        # no action is taken.
        return model
    try:
        # try to convert to apex model.
        orig_device: torch.device = model.torchnet.parameters().__next__().device
        model.to(torch.device('cuda'))
        model.torchnet, model.optimizer = amp.initialize(
            model.torchnet, model.optimizer,
            opt_level=opt_level,
            verbosity=verbosity,
            **kwargs
        )
        model.to(orig_device)
        model.is_apex = True
    except Exception as e:
        # nothing happens.
        warnings.warn(f'to_apex fails with eror message: {e}', RuntimeWarning)
        assert model.is_apex is False
    finally:
        return model


@contextlib.contextmanager
def AMPGradientBackwardStep(loss: Tensor, model: Model):
    model.zero_grad()
    with amp.scale_loss(loss, model.optimizer) as scaled_loss:
        yield scaled_loss
    model.step()
