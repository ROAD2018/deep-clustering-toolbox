from unittest import TestCase

import torch
from deepclustering.arch import ARCH_PARAM_DICT
from deepclustering.model import Model
from deepclustering.utils import simplex
from pathlib2 import Path


class TestModel(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.arch_dicts = ARCH_PARAM_DICT
        self.arch_names = list(ARCH_PARAM_DICT.keys())
        for arch_name in self.arch_names:
            self.arch_dicts[arch_name].update({'name': arch_name})
        # Built the arch_dicts with the default arch_dict from the architecture.
        self.optim_dict = {
            'name': 'Adam',
            'lr': 1e-4,
            'weight_decay': 1e-5
        }
        self.scheduler_dict = {
            'name': 'MultiStepLR',
            'milestones': [10, 20, 30, 40, 50, 60, 70, 80, 90],
            'gamma': 0.7
        }
        self.image = torch.randn(10, 3, 64, 64)

    @staticmethod
    def _init_onenet(arch_dict, optim_dict, scheduler_dict):
        network = Model(arch_dict=arch_dict, optim_dict=optim_dict, scheduler_dict=scheduler_dict)
        return network

    def test_initial_networks(self):
        for arch_name, arch_dict in self.arch_dicts.items():
            # print(f'Building {arch_name} network with parameters:')
            # pprint(arch_dict)
            model = self._init_onenet(arch_dict=arch_dict, optim_dict=self.optim_dict,
                                      scheduler_dict=self.scheduler_dict)
            if arch_name == 'clusternetimsat':
                with self.assertRaises(RuntimeError):
                    predicts = model.predict(self.image)
            elif arch_name == 'vatnet':
                predicts = model.predict(self.image)
                assert not simplex(predicts[0])
            else:
                predicts = model.predict(self.image)
                self.assertEqual(simplex(predicts[0]), True)

    def test_call(self):
        for arch_name, arch_dict in self.arch_dicts.items():
            model = self._init_onenet(arch_dict=arch_dict, optim_dict=self.optim_dict,
                                      scheduler_dict=self.scheduler_dict)
            model.eval()
            if arch_name == 'clusternetimsat':
                with self.assertRaises(RuntimeError):
                    torch.allclose(model.predict(self.image)[0], model(self.image)[0])
            else:
                torch.allclose(model.predict(self.image)[0], model(self.image)[0])

    def test_state_dict(self):
        for arch_name, arch_dict in self.arch_dicts.items():
            print(f'Building {arch_name} network with parameters:')
            # pprint(arch_dict)
            model1 = self._init_onenet(arch_dict=arch_dict, optim_dict=self.optim_dict,
                                       scheduler_dict=self.scheduler_dict)
            model1.eval()
            input_img = self.image if arch_name != 'clusternetimsat' else torch.randn(10, 1, 28, 28)
            predicts = model1.predict(input_img)
            model2 = self._init_onenet(arch_dict=arch_dict, optim_dict=self.optim_dict,
                                       scheduler_dict=self.scheduler_dict)
            model2.eval()
            with self.assertRaises(AssertionError):
                assert torch.allclose(model2(input_img)[0], predicts[0])

            model2.load_state_dict(model1.state_dict)
            assert torch.allclose(model2(input_img)[0], predicts[0])

    def test_initialize_instance_from_cls(self):
        for arch_name, arch_dict in self.arch_dicts.items():
            model1 = self._init_onenet(arch_dict=arch_dict, optim_dict=self.optim_dict,
                                       scheduler_dict=self.scheduler_dict)
            model1.eval()
            input_img = self.image if arch_name != 'clusternetimsat' else torch.randn(10, 1, 28, 28)
            predicts = model1.predict(input_img)
            model2 = Model.initialize_from_state_dict(model1.state_dict)
            model2.eval()
            assert torch.allclose(model2(input_img)[0], predicts[0])

    def test_initialize_instance_from_cls_save(self):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        for arch_name, arch_dict in self.arch_dicts.items():
            model1 = self._init_onenet(arch_dict=arch_dict, optim_dict=self.optim_dict,
                                       scheduler_dict=self.scheduler_dict)
            model1.to(device=device)
            model1.eval()
            input_img = self.image if arch_name != 'clusternetimsat' else torch.randn(10, 1, 28, 28)

            predicts = model1.predict(input_img.to(device))
            torch.save(model1.state_dict, f'{Path(__file__).parent / arch_name}.pth')
            state_dict = torch.load(f'{Path(__file__).parent / arch_name}.pth', map_location=torch.device('cpu'))
            model2 = Model.initialize_from_state_dict(state_dict)
            model2.to(device)
            model2.eval()
            assert torch.allclose(model2(input_img.to(device))[0], predicts[0])
