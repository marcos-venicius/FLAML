import numpy as np
from string import Template
from typing import List, Optional
from tqdm import tqdm
from openai.embeddings_utils import get_embedding, cosine_similarity

from config import OAI_EMBEDDING_CONFIG
from evaluators import Evaluator

class EmbeddingGenerator:
    def __init__(self, prompt_template: str):
        self.prompt_template = prompt_template

    def embed(self, data: str) -> list:
        data_dict = {
            'input': data
        }
        prompt = Template(self.prompt_template).substitute(data_dict)
        embedding = get_embedding(prompt, engine=OAI_EMBEDDING_CONFIG[0]['model'], **OAI_EMBEDDING_CONFIG[0])
        return embedding

class Sampler:
    def __init__(self, dataset: List[str]) -> None:
        self.dataset = dataset

    def sample(self, num_samples: int) -> List[str]:
        indices = np.random.choice(len(self.dataset), num_samples, replace=False)
        return [self.dataset[idx] for idx in indices]

class AdversarialSampler(Sampler):
    def __init__(self, dataset: List[str], evaluator: Evaluator) -> None:
        adv_dataset = []
        num_non_adv = 0
        for sample in tqdm(dataset, desc='Identifying adversarial examples from dataset...'):
            eval_result, _, _, _ = evaluator.evaluate(sample)
            if eval_result == 0:
                adv_dataset.append(sample)
            elif eval_result == 1:
                num_non_adv += 1
        super().__init__(adv_dataset)
        print(f'Found {len(self.dataset)} adversarial samples.')
        print(f'Adversarial rate over dataset: {np.round(len(self.dataset) / (num_non_adv + len(self.dataset)) * 100, 2)}%')

class SimilarityThresholdSampler(AdversarialSampler):
    def __init__(self, dataset: List[str], evaluator: Evaluator, threshold: float, prompt_template: str) -> None:
        super().__init__(dataset, evaluator)
        self.threshold = threshold
        self.embeddings = []
        embedding_gen = EmbeddingGenerator(prompt_template)
        for sample in tqdm(self.dataset, desc='Generating embeddings for samples...'):
            cur_embedding = embedding_gen.embed(sample)
            self.embeddings.append(cur_embedding)

    def sample(self, num_samples: int) -> List[str]:
        indices = np.random.choice(len(self.dataset), 1)
        seed_embedding = self.embeddings[indices[0]]
        all_similarities = []
        for embedding in self.embeddings:
            similarity = cosine_similarity(seed_embedding, embedding)
            all_similarities.append(similarity)
        ascending_sorted = np.argsort(all_similarities)
        top_similarities_idx = ascending_sorted[-num_samples:]
        final_idx = [idx for idx in top_similarities_idx if all_similarities[idx] >= self.threshold]
        return [self.dataset[idx] for idx in final_idx]

class SamplerFactory:
    @classmethod
    def create(cls, sampler_name: str, dataset: List[str], evaluator: Optional[Evaluator], threshold: Optional[float], prompt_template: Optional[str]) -> Sampler:
        if sampler_name == 'Sampler':
            return Sampler(dataset)
        if sampler_name == 'AdversarialSampler':
            return AdversarialSampler(dataset, evaluator)
        if sampler_name == 'SimilarityThresholdSampler':
            return SimilarityThresholdSampler(dataset, evaluator, threshold, prompt_template)
        raise NotImplementedError(f'Sampler with name {sampler_name} not implemented.')
