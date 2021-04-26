# type: ignore
# pylint: disable=no-member

from transformers import BartTokenizer, BartForConditionalGeneration, AdamW, get_cosine_schedule_with_warmup
import torch

import uuid
import tqdm
import json
import time
import os

class Engine:
    def __init__(self, path:str="./training/bart_enwiki_BASE-6c279:0:400000"):
        self.tokenizer = BartTokenizer.from_pretrained(path)
        self.model = BartForConditionalGeneration.from_pretrained(path)
        device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        self.model.to(device)

    def __pre_process_sample(self, article:str="", context:str=""):
        return self.tokenizer.convert_tokens_to_ids(
                [self.tokenizer.bos_token] + 
                self.tokenizer.tokenize(article) + 
                [self.tokenizer.sep_token] + 
                self.tokenizer.tokenize(context) + 
                [self.tokenizer.eos_token])

    def generate_syntheses(self, processed_samples:[torch.Tensor]):
        summary_ids = self.model.generate(processed_samples, num_beams=4, early_stopping=True)
        return [self.tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summary_ids]

    def batch_process_samples(self, samples:[[str,str]], clip_to=512):
        results = []
        max_length = 0

        for sample in samples:
            sample_encoded = self.__pre_process_sample(sample[0], sample[1])[:clip_to]
            results.append(sample_encoded)
            max_length = max(max_length, len(sample_encoded))

        for indx, i in enumerate(results):
            results[indx] = i+[self.tokenizer.pad_token_id for i in range(max_length-len(i))]

        return torch.LongTensor(results)

    def batch_execute(self, samples:[[str,str]]):
        return self.generate_syntheses(self.batch_process_samples(samples))

    def execute(self, article_title:str="", context:str=""):
        return self.batch_execute([article_title, context])[0]
