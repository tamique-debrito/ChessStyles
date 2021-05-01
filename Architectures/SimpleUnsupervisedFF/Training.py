import os
import torch
from torch import nn
from torch.utils.data import DataLoader

from CONSTANTS import SAVED_MODELS_PATH, TEST_GAME_DATA_PATH
from Architectures.SimpleUnsupervisedFF.Model import get_model

from Dataset.DataLoader.GameDataset import GameDataset

def train_basic_contrastive(epochs=100, batch_size=128, num_workers=0, lr=1e-2, multi_channel=True, save_model=True):
    device = torch.device('cuda:0') if torch.cuda.is_available() else 'cpu'

    ds = GameDataset(multi_channel=multi_channel, return_contrastive=True, tensors_in_memory=True)
    loader = DataLoader(ds, batch_size=batch_size, num_workers=num_workers, shuffle=True)

    model_name = f'simple_unsupervised_contrastive_ff_{"multi" if multi_channel else "single"}_channel'
    model = get_model(multi_channel)
    model = model.to(device)

    optim = torch.optim.Adam(model.parameters(), lr=lr)



    for epoch in range(1, epochs + 1):
        running_loss = 0
        for i, d in enumerate(loader, 1):
            boards = d['before'].to(device).flatten(1)
            boards_cont = d['before_cont'].to(device).flatten(1)

            enc = model(boards)
            enc_cont = model(boards_cont)

            loss = torch.cosine_similarity(enc, enc_cont).mean()

            optim.zero_grad()
            loss.backward()
            optim.step()

            running_loss += loss.item()

            print(f'\rBatch {i}/{len(loader)} | average loss: {running_loss / i:.3f}', end='')


        print(f'\rEpoch {epoch}/{epochs} | average loss: {running_loss/len(loader):.3f}')

    if save_model:
        torch.save(model, os.path.join(SAVED_MODELS_PATH, model_name))

if __name__ == "__main__":
    train_basic_contrastive(100, lr=1e-4)