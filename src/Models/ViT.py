import torch
import torch.nn as nn
import os
from Models.PatchEmbedding import PatchEmbedding
from Models.TransformerEncoder import TransformerEncoder

class ViT(nn.Module):
    def __init__(self, FLAGS):
        super(ViT, self).__init__()
        self.patch_embedding = PatchEmbedding()  # [32, 3, 224, 224] ===> [32, 196, 768]
        self.cls_token = nn.Parameter(torch.zeros(1, 1, FLAGS.hidden_size))  # [1, 1, 768]
        num_patches = (int(FLAGS.picture_size / FLAGS.patch_size)) ** 2  # 196
        self.pos_embed = nn.Parameter(torch.zeros(1, num_patches + 1, FLAGS.hidden_size))  # [1, 197, 768]
        self.encoder = TransformerEncoder()  # [32, 197, 768] ===> [32, 197, 768]
        self.fc = nn.Linear(FLAGS.hidden_size, FLAGS.num_classes)  # [32, 768] ===> [32, 10]
        self.softmax = nn.Softmax(dim=-1)
        
    def forward(self, x):
        x = self.patch_embedding(x)  # [32, 3, 224, 224] ===> [32, 196, 768]
        cls_tokens = self.cls_token.expand(x.shape[0], -1, -1)  # [32, 1, 768]
        x = torch.cat((cls_tokens, x), dim=1)  # [32, 197, 768]
        x = x + self.pos_embed  # [32, 197, 768] + [1, 197, 768] = [32, 197, 768]
        x = self.encoder(x)  # [32, 197, 768] ===> [32, 197, 768]
        x = x[:, 0]  # [32, 197, 768] ===> [32, 768], 取每个197里的第0个
        x = self.fc(x)  # [32, 768] ===> [32, 10]
        x = self.softmax(x)  # [32, 10]
        return x
        