import json
import csv
import configparser
import sys
import os
from tqdm import tqdm

module_path = os.path.abspath('.')
sys.path.insert(-1, module_path)
sys.path.append("../../")


def parse_path_cfg():
    cfg = configparser.ConfigParser()
    cfg.read("./preprocess/dataset.cfg")
    path = cfg['PATH']
    return path


def load_kg():
    from preprocess.fix_dataset_error import (entity_list, relation_list, triple_list)
    path = parse_path_cfg()

    with open(path['ENTITY'], 'r', encoding='utf-8') as f:
        for line in f.readlines():
            entity_list.append(line.strip('\n'))
    entity_map = {v: i for i, v in enumerate(entity_list)}
    print('entities: ', len(entity_map))

    with open(path['RELATION'], 'r', encoding='utf-8') as f:
        for line in f.readlines():
            relation_list.append(line.strip('\n'))
    relation_map = {v: i for i, v in enumerate(relation_list)}
    print('relations: ', len(relation_map))

    with open(path['TRIPLE'], 'r', encoding='utf-8') as f:
        for line in f.readlines():
            s, r, t = line.strip('\n').split('\t')
            try:
                assert s in entity_map
                assert r in relation_map
                assert t in entity_map
                triple_list.append(line.strip('\n'))
            except KeyError:
                raise KeyError('Error encountered at ', line.strip('\n'))
    print('triples: ', len(triple_list))
    return entity_map, relation_map, triple_list


def load_dials(dial_type, entity_map, relation_map, triple_list):
    assert dial_type in ['train', 'dev', 'test']
    path = parse_path_cfg()
    triple_set = set(triple_list)
    dial_file_path = path['%s_FILE' % dial_type.upper()]
    print('Loading from ', dial_file_path, end=' ... ')
    with open(dial_file_path, 'r') as f:
        dataset = json.load(f)
        print('Size: ', len(dataset), end=' ... ')
        for dial in tqdm(dataset, total=len(dataset), disable=True):
            content = dial['dialogue']
            for turn in content:
                # print(action_ids)
                if 'metadata' in turn and 'path' in turn['metadata']:
                    score, path, utterance = turn['metadata']['path']
                    # if len(path) > 1:
                    #     print(path)
                    #     exit()
                    for triple in path:
                        if '\t'.join(triple) not in triple_set:
                            raise Exception('Unexpected triple: ', triple)
                        if triple[0] not in entity_map:
                            raise Exception('Unexpected entity: ', triple[0])
                        if triple[1] not in relation_map:
                            raise Exception('Unexpected relation: ', triple[1])
                        if triple[2] not in entity_map:
                            raise Exception('Unexpected entity: ', triple[2])
            # user_rating = json.loads(row[1])
            # assistant_rating = json.loads(row[2])
            # print(user_rating)
            # print(assistant_rating)
    print('%s: finish' % dial_type.upper())
    return


if __name__ == '__main__':
    entity_map, relation_map, triple_list = load_kg()
    load_dials('train', entity_map, relation_map, triple_list)
    load_dials('dev', entity_map, relation_map, triple_list)
    load_dials('test', entity_map, relation_map, triple_list)