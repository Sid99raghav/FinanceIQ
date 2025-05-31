from typing import Optional, List, Dict
import json
import os
import re
import random
from lib.generate_concept_explanation import call_llm_and_save_explanation

def get_mcq(parameters: list, qs_num = 20):
    if len(parameters) == 0:
        return []
    
    dir_path = os.path.join('qs')
    for param in parameters:
        dir_path=os.path.join(dir_path,param)
    
    # search all qs.json files in the directory tree and join the json
    questions = []
    qs_file_list = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file == 'qs.json':
                file_path = os.path.join(root, file)
                qs_file_list.append(file_path)

    # shuffle the files
    random.shuffle(qs_file_list)

    for file_path in qs_file_list:
        questions.extend(load_questions_from_json(file_path))
        if len(questions) >= qs_num * 3:
            return questions
    return questions

def load_questions_from_json(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"Error decoding JSON file: {file_path}")
        return []
    
def get_children(parent: Optional[str], data: dict) -> List[dict]:
    #import pdb;pdb.set_trace()
    if not parent:
        return [{"name": key} for key in data.keys()]
    return [{"name": key} for key in data.get(parent, {}).keys()]

# Custom sorting function for natural ordering
def natural_sort_key(value):
    return [int(part) if part.isdigit() else part for part in re.split(r'(\d+)', value)]

# create topics from the qs folder.
# can have multiple levels
def create_topics():
    current_path = 'qs'
    def build_tree(current_path):
        tree = {}
        for entry in sorted(os.listdir(current_path), key=natural_sort_key):
            if entry.startswith('.'):
                continue
            entry_path = os.path.join(current_path, entry)
            if os.path.isdir(entry_path):
                tree[entry] = build_tree(entry_path)
        return tree
    if os.path.isdir(current_path):
        return build_tree(current_path)

def get_subtree(data, key_to_match):
    """
    Recursively searches a nested dictionary and returns a list of dictionaries with 'name' key for the subtopics
    where the key matches `key_to_match`.
    
    Args:
        data (dict): The nested dictionary to search.
        key_to_match (str): The key to match (e.g., a topic like 'Math' or 'Physics').
    
    Returns:
        list: A list of dictionaries with 'name' keys for each subtopic.
    """
    # If the current level of the dictionary matches the key_to_match, return a list of subtopics
    if key_to_match in data:
        return [ subtopic for subtopic in data[key_to_match]]
    
    # Recursively search nested dictionaries
    for key, value in data.items():
        if isinstance(value, dict):
            result = get_subtree(value, key_to_match)
            if result:
                return result
    
    return None


def get_subtree(data, genealogy):
    """
    Recursively traverses a nested dictionary and returns the children of the node at the given genealogy path.
    
    Args:
        data (dict): The nested dictionary to search.
        genealogy (list): A list representing the path to the node (e.g., ["Math", "Geometry"]).
    
    Returns:
        list: A list of dictionaries with 'name' keys for the children of the specified node.
    """
    # Traverse the dictionary following the genealogy path
    current_level = data
    for key in genealogy:
        if key in current_level:
            current_level = current_level[key]
        else:
            return None  # If the path does not exist, return None
    
    # Return the children at the current level
    if isinstance(current_level, dict):
        return [child for child in current_level]
    
    return None

def get_subdirectories(path):
    subdirectories = []
    for d in os.listdir(path):
        if d.startswith('.'):
            continue
        full_path = os.path.join(path, d)  # Create the full path
        if os.path.isdir(full_path):
            subdirectories.append(d)
    try:  # Attempt numerical sorting
        if subdirectories and subdirectories[0].isdigit():  # Ensure the list is not empty
            subdirectories.sort(key=int)  # Sort as integers
    except ValueError:  # Handle cases where names are not integers
        pass
    return subdirectories

def load_topics(genealogy: list):
    #import pdb;pdb.set_trace()
    # create the path from qs + genealogy
    path = 'qs'
    for g in genealogy:
        path = os.path.join(path, g)
    if not os.path.isdir(path):
        print(f"Invalid path: '{path}'. Please provide a valid file or directory.")
        return []
    return get_subdirectories(path)

def generate_concept_explanation_util(topic_path: str, wrong_questions: list, force: bool):
    """
    Generate concept explanations for all leaf directories under the given topic path.

    Args:
        topic_path (str): The topic path in the format "grade/subject/topics/subtopics".
        wrong_questions (list): A list of wrong questions (optional).
        force (bool): Force recreation of the explanation file.

    Returns:
        dict: A dictionary collating explanations from all leaf directories.
    """
    # Parse the topic path into grade, subject, and subtopics
    parts = topic_path.split("/")
    if len(parts) < 2:
        raise ValueError("Invalid topic path format. Expected format: grade/subject/topics/subtopics.")

    grade, subject = parts[0], parts[1]
    subtopics = parts[2:] if len(parts) > 2 else []

    # Define the base directory where the questions are stored
    base_dir = "qs"
    topic_dir = os.path.join(base_dir, *parts)
    if not os.path.exists(topic_dir):
        raise FileNotFoundError(f"Topic directory not found: {topic_dir}")

    # Helper function to find all leaf directories
    def find_leaf_directories(path):
        leaf_dirs = []
        for root, dirs, files in os.walk(path):
            if not dirs:  # If there are no subdirectories, it's a leaf directory
                leaf_dirs.append(root)
        return leaf_dirs

    # Find all leaf directories under the topic directory
    leaf_directories = find_leaf_directories(topic_dir)

    # Collate explanations from all leaf directories
    collated_explanations = {"concept": ""}  # Initialize with an empty "concept" key
    for leaf_dir in leaf_directories:
        output_file = os.path.join(leaf_dir, "explanation.json")  # Always use "explanation.json" as the file name

        # Generate or retrieve the explanation for the current leaf directory
        explanation = call_llm_and_save_explanation(
            grade, subject, subtopics + leaf_dir.split(os.sep)[len(parts) + 1:], wrong_questions, output_file, force
        )

        # Append the explanation's concept to the collated "concept" key
        if "concept" in explanation:
            collated_explanations["concept"] += explanation["concept"] + "\n\n"

    return collated_explanations