from pathlib import Path

from torch.utils.data import DataLoader
from torchvision import transforms

from deepclustering import DATA_PATH
from deepclustering.dataset.classification.cifar import CIFAR10
from deepclustering.manager import ConfigManger
from deepclustering.model import Model
from playground.swa.swa_trainer import SWATrainer

DEFAULT_CONFIG = str(Path(__file__).parent / "config.yaml")

config = ConfigManger(DEFAULT_CONFIG_PATH=DEFAULT_CONFIG, verbose=True).config
# create model:
model = Model(
    arch_dict=config["Arch"],
    optim_dict=config["Optim"],
    scheduler_dict=config["Scheduler"],
)

transform_train = transforms.Compose([
    transforms.RandomCrop(32, padding=4),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
])
transform_test = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
])
train_loader = DataLoader(CIFAR10(root=DATA_PATH, transform=transform_train, train=True), **config["DataLoader"])
val_loader = DataLoader(CIFAR10(root=DATA_PATH, transform=transform_test, train=False), **config["DataLoader"])

trainer = SWATrainer(
    model=model,
    train_loader=train_loader,
    val_loader=val_loader,
    config=config,
    **config["Trainer"]
)
trainer.start_training()
