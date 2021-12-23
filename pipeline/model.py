"""Generate the tf-idf weights
"""
from collections import defaultdict
import math


FREQUENCIES = {
    "Very rare (<4-1%)": 4,
    "Occasional (29-5%)": 29,
    "Very frequent (99-80%)": 99,
    "Frequent (79-30%)": 79,
    "Excluded (0%)": 0,  # Special as it should not be considered if symptom is the case
    "Obligate (100%)": 100,  # Special as it should not be considered if symptom is not the case
}
NEVER_HAPPENS = "Excluded (0%)"


def generate_tfidf_weights(disease_orpha_code_to_name, symptom_id_to_name, disease_id_to_symptom_id_and_frequency_tuple):
    unique_symptom_ids = symptom_id_to_name.keys()
    unique_disease_ids = disease_orpha_code_to_name.keys()

"""
Computing TF-IDF

**Term frequency**: in this context, the term frequency is how common
each symptom is for a given disease. This is known based on the input 
data, as each symptom has an associated frequency.
- how important is term within current document?

TODO: transform dict so that for each disease -> Dict[symptom -> freq] 

**Inverse document frequency**: how many docs do you appear? And how common?
-> Not sure how to translate it...
-> How important is term overall?

"""

def calculate_symptom_idf(disease_id_to_symptom_id_and_frequency_tuple):
    total_diseases = len(disease_id_to_symptom_id_and_frequency_tuple.keys())
    symptom_idf_dict = defaultdict(float)

    for disease_symptom_list in disease_id_to_symptom_id_and_frequency_tuple:
        for symptom, freq in disease_symptom_list.items():
            if freq != NEVER_HAPPENS:
                symptom_idf_dict[symptom] += 1

    for symptom, freq in symptom_idf_dict.items():
        symptom_idf_dict[symptom] = math.log(total_diseases / float(freq))
    return symptom_idf_dict



"""
Model:
- tf-idf weights to be used to calculate new symptom vector - I guess a single vector? :thinking:
- Do we then need to transfor each disease with its tf-idf weight? :thinking:
"""


"""
Algorithm:
- Symptom vector with 1 if present symptom, 0 if absent
- for each disease:
--> check if any symptom is in excluded list - if so remove from candidates
--> check if any symptom missing from required list - if so remove from candidates

For the input symptom vector:
- calculate weight single vector using tf-idf weights - multiple each 

Given weighted tf-idf vector for inputs: calculate cosine similarity with each disease

Return the list of diseases above some threshold (assuming identical vectors means 1) as candidates, if any
"""