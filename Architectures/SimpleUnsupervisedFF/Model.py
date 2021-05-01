from torch import nn


def ff_sequential(h_list):
    mod_list = []
    for h0, h1 in zip(h_list, h_list[1:-1]):
        mod_list.append(nn.Linear(h0, h1))
        mod_list.append(nn.ReLU())
    mod_list.append(nn.Linear(h_list[-2], h_list[-1]))
    return nn.Sequential(*mod_list)


def get_model(multi_channel=True):
    if multi_channel:
        return ff_sequential([12 * 8 * 8, 1024, 1024, 512, 256, 128, 64])
    else:
        return ff_sequential([8 * 8, 1024, 1024, 512, 256, 128, 64])