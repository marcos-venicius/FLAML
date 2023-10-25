import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('--data_file', type=str)
args = parser.parse_args()

with open(args.data_file) as fdata:
    data = json.load(fdata)

adv = [sample for sample in data if sample['evaluation'] == 0]
inconclusive = [sample for sample in data if sample['evaluation'] < 0]

total = len(data)
print(f'Adversarial rate: {len(adv) / total}')
print(f'Inconclusive rate: {len(inconclusive) / total}')