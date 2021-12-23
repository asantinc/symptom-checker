import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple, Set

import xmltodict

import logging


logger = logging.getLogger()

DATA_PATH = Path(__file__).parent.parent / 'data'
RAW_DATA_PATH = DATA_PATH / 'raw'
PROCESSED_DATA_PATH = DATA_PATH / 'processed'


def parse_file(file_name: Path) -> Dict:
    logger.info('Parsing file...')
    with open(file_name, encoding="ISO-8859-1") as f:
        xml_content = f.read()
    logger.info('Parsing complete')
    return xmltodict.parse(xml_content)


def _generate_mappings(source_data_dict: Dict):
    _disease_orpha_code_to_name = {}
    _symptom_id_to_name = {}
    _disease_id_to_symptom_id_and_frequency_tuple = defaultdict(set)

    all_diseases = source_data_dict['JDBOR']['HPODisorderSetStatusList']['HPODisorderSetStatus']

    logger.info(f'Processing Diseases: {len(all_diseases)}')
    for i, disease in enumerate(all_diseases):
        logger.info(f'processing disease {i}/{len(all_diseases)}')
        disease = disease['Disorder']
        name = disease['Name']['#text']
        disease_code = disease['OrphaCode']
        _disease_orpha_code_to_name[disease_code] = name

        relevant_symptoms = disease['HPODisorderAssociationList'].get('HPODisorderAssociation', [])
        logger.info(f'Processing symptoms {len(relevant_symptoms)}', )
        for symptom in relevant_symptoms:
            symptom_id = symptom['HPO']['HPOId']
            symptom_name = symptom['HPO']['HPOTerm']
            symptom_frequency = symptom['HPOFrequency']['Name']['#text']
            _symptom_id_to_name[symptom_id] = symptom_name
            _disease_id_to_symptom_id_and_frequency_tuple[disease_code].add((symptom_id, symptom_frequency))
    return _disease_orpha_code_to_name, _symptom_id_to_name, _disease_id_to_symptom_id_and_frequency_tuple


def _output_mappings_to_file(disease_orpha_code_to_name, symptom_id_to_name, disease_id_to_symptom_id_and_frequency_tuple, frequencies):
    with open(PROCESSED_DATA_PATH / 'symptom_id_to_name.json', 'w') as f:
        json.dump(symptom_id_to_name, f)
    with open(PROCESSED_DATA_PATH / 'disease_orpha_code_to_name.json', 'w') as f:
        json.dump(disease_orpha_code_to_name, f)

    for disease, symptom_frequency_tuple in disease_id_to_symptom_id_and_frequency_tuple.items():
        disease_id_to_symptom_id_and_frequency_tuple[disease] = list(symptom_frequency_tuple)
    with open(PROCESSED_DATA_PATH / 'disease_id_to_symptom_id_and_frequency_tuple.json', 'w') as f:
        json.dump(disease_id_to_symptom_id_and_frequency_tuple, f)

    with open(PROCESSED_DATA_PATH / 'frequencies.json', 'w') as f:
        json.dump(list(frequencies), f)


def _load_disease_to_symptom_mappings() -> Tuple[Dict, Dict, Dict]:
    with open(PROCESSED_DATA_PATH / 'symptom_id_to_name.json', 'r') as f:
        _symptom_id_to_name = json.load(f)
    with open(PROCESSED_DATA_PATH / 'disease_orpha_code_to_name.json', 'r') as f:
        _disease_orpha_code_to_name = json.load(f)
    with open(PROCESSED_DATA_PATH / 'disease_id_to_symptom_id_and_frequency_tuple.json', 'r') as f:
        _disease_id_to_symptom_id_and_frequency_tuple = json.load(f)
    return _disease_orpha_code_to_name, _symptom_id_to_name, _disease_id_to_symptom_id_and_frequency_tuple


def _find_unique_frequencies(disease_id_to_symptom_id_and_frequency_tuple: Dict) -> Set[str]:
    return {
        s[1]
        for disease, symptoms in disease_id_to_symptom_id_and_frequency_tuple.items()
        for s in symptoms
    }


def main():
    data_dict = parse_file(RAW_DATA_PATH / 'en_product4.xml')
    disease_orpha_code_to_name, symptom_id_to_name, disease_id_to_symptom_id_and_frequency_tuple = _generate_mappings(data_dict)

    frequencies = _find_unique_frequencies(disease_id_to_symptom_id_and_frequency_tuple)
    _output_mappings_to_file(disease_orpha_code_to_name, symptom_id_to_name, disease_id_to_symptom_id_and_frequency_tuple, frequencies)


if __name__ == '__main__':
    main()
