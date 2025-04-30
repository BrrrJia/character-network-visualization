from itertools import combinations
import graphviz
from graphviz import Digraph


def read_character_dict(character_dict_file):
    """
    Read the character dictionary

    Parameters:
        character_dict_file (file): character dictionary file

    Returns:
        character_list (list): modified character dictionary in list

    """
    with open(character_dict_file, 'r') as character_dict:
        character_list = character_dict.read().split('\n')
    return character_list

def read_text(text_file):
    """
    Read the text file

    Parameters:
        text_file (file): text file

    Returns:
        text_tokens_list (list): tokenized text by white space

    """
    with open(text_file, 'r') as text:
        text_tokens_list = text.read().split()
    return text_tokens_list

def dict_ner(character_dict_file, text_file):
    """
    Recognize the character entities based on dictionary

    Parameters:
        character_dict_file (file): character dictionary file
        text_file (file): text file

    Returns:
        name_entity_list (list): a list of character entities
    """
    characters_list = read_character_dict(character_dict_file)
    tokens_list = read_text(text_file)
    name_entity_list = []
    N = len(tokens_list)
    for i in range(N):
        # for the name with just one name
        if tokens_list[i][:-1] in characters_list:
            if tokens_list[i][:-1] == 'MACBETH' or tokens_list[i][:-1] == 'MACDUFF':
                if tokens_list[i-1] != 'LADY':
                    name_entity_list.append(tokens_list[i][:-1])
            else:
                name_entity_list.append(tokens_list[i][:-1])
        elif tokens_list[i][0]+tokens_list[i][1:].upper() in characters_list:
            if tokens_list[i] == 'Macbeth' or tokens_list[i] == 'Macduff':
                if tokens_list[i-1] != 'Lady':
                    name_entity_list.append(tokens_list[i].upper())
            else:
                name_entity_list.append(tokens_list[i].upper())
        # for the name with two names
        if i != N-1:
            bigram = tokens_list[i]+' '+tokens_list[i+1]
            bigram_B = tokens_list[i][0]+tokens_list[i][1:].upper()+' '+tokens_list[i+1][0]+tokens_list[i][1:].upper()
            if bigram[:-1] in characters_list:
                name_entity_list.append(bigram[:-1])
            elif bigram_B in characters_list:
                name_entity_list.append(bigram_B.upper())
        # for the special name 'SON' in text refering to the name 'BOY' in character dictionary
        if tokens_list[i][:-1] == 'SON':
            name_entity_list.append('BOY')
    return name_entity_list

def compare_ner_with_dict(ner_result, characters_dict):
    """
    Check identification results by compared with dictionary

    Parameters:
        ner_result (list): the result of the NER
        characters_dict (list): character dictionary
    Returns:
       result (bool): True means success, False means failure
    """
    if set(ner_result).issubset(set(characters_dict)) and set(characters_dict).issubset(set(ner_result)):
        result = True
    else:
        result = False
    return result
    
def split_by_scene(play_text_file):
    """
    Split the text by scene

    Parameters:
        play_text_file (file): play text file

    Returns:
        scenes_list (list): a list of scenes

    """
    with open(play_text_file, 'r') as play_text:
        scenes_list = play_text.read().split('SCENE')
    return scenes_list

def create_relation_dict(characters_list):
    """
    Create the dictionary of the character relation

    Parameters:
        characters_list (list): a list of characters

    Returns:
        relation_dict (dict): the dictionary of the charater relation
            key (tuple): a pair of characters
            value (int): frequency of the character pair and initialized with 0

    """
    relation_dict = {}
    relation_pairs = list(combinations(characters_list, 2))
    converted_relation_pairs = [frozenset(elem) for elem in relation_pairs]
    for pair in converted_relation_pairs:
        relation_dict[pair] = 0
    return relation_dict
        
def relation_recognizer(play_text_file, characters_dict_file):
    """
    Recognize the relation between characters, if the characters appear in the same scene, then assume they have relation

    Parameters:
        play_text_file (file): play text file
        character_dict_file (file): character dictionary file

    Returns:
        converted_relation_list (list): a list of character pairs and their frequency

    """
    characters_list = read_character_dict(characters_dict_file)
    scenes_list = split_by_scene(play_text_file)
    relation_dict = create_relation_dict(characters_list)

    for scene in scenes_list:
        scene_tokens_list = scene.split()
        scene_name_entity_list = []
        N = len(scene_tokens_list)
        for i in range(N):
            if scene_tokens_list[i][:-1] in characters_list:
                if scene_tokens_list[i][:-1] == 'MACBETH' or scene_tokens_list[i][:-1] == 'MACDUFF':
                    if scene_tokens_list[i-1] != 'LADY':
                        scene_name_entity_list.append(scene_tokens_list[i][:-1])
                else:
                    scene_name_entity_list.append(scene_tokens_list[i][:-1])
            elif scene_tokens_list[i][0]+scene_tokens_list[i][1:].upper() in characters_list:
                if scene_tokens_list[i] == 'Macbeth' or scene_tokens_list[i] == 'Macduff':
                    if scene_tokens_list[i-1] != 'Lady':
                        scene_name_entity_list.append(scene_tokens_list[i].upper())
                else:
                    scene_name_entity_list.append(scene_tokens_list[i])
            
            if i != N-1:
                bigram = scene_tokens_list[i]+' '+scene_tokens_list[i+1]
                bigram_B = scene_tokens_list[i][0]+scene_tokens_list[i][1:].upper()+' '+scene_tokens_list[i+1][0]+scene_tokens_list[i][1:].upper()
                if bigram[:-1] in characters_list:
                    scene_name_entity_list.append(bigram[:-1])
                elif bigram_B in characters_list:
                    scene_name_entity_list.append(bigram_B.upper())
            
            if scene_tokens_list[i][:-1] == 'SON':
                scene_name_entity_list.append('BOY')
        scene_name_entity_set = set(scene_name_entity_list)
        scene_relation_pairs = list(combinations(scene_name_entity_set,2))
        converted_scene_relation_pairs = [frozenset(elem) for elem in scene_relation_pairs]

        for elem in converted_scene_relation_pairs:
            if elem in relation_dict:
                relation_dict[elem] += 1
    pairs_list = [tuple(elem) for elem in relation_dict.keys()]
    frequency_list = relation_dict.values()
    converted_relation_list = [(pair, frequency) for pair, frequency in zip(pairs_list, frequency_list)]
    return converted_relation_list

def create_context_window(sequence, center_index, window_size):
    """
    Create the context window of the center index

    Parameters:
        sequence (list): a list of tokens
        center_index (int): the index of the center index
        window_size (int): the size of the window

    Returns:
        sequence[start_index:end_index] (list): a list of tokens from start index to end index

    """
    start_index = max(0, center_index - window_size // 2)
    end_index = min(len(sequence), center_index + (window_size + 1) // 2)
    return sequence[start_index:end_index]

def relation_recognizer_modified(play_text_file, characters_dict_file):
    """
    Recognize the relation between characters, if another character appear in the context window(length 30) of one character, then assume they have relation

    Parameters:
        play_text_file (file): play text file
        character_dict_file (file): character dictionary file

    Returns:
        converted_relation_list (list): a list of character pairs and their frequency

    """
    characters_list = read_character_dict(characters_dict_file)
    tokens_list = read_text(play_text_file)
    relation_dict = create_relation_dict(characters_list)

    context_window = []
    N = len(tokens_list)
    # check all the tokens in the text
    for i in range(N):
        # for the name with just one name
        if tokens_list[i][:-1] in characters_list:
            if tokens_list[i][:-1] == 'MACBETH' or tokens_list[i][:-1] == 'MACDUFF':
                if tokens_list[i-1] != 'LADY':
                    context_window.append(create_context_window(tokens_list, i, 30))
            else:
                context_window.append(create_context_window(tokens_list, i, 30))
        elif tokens_list[i][0]+tokens_list[i][1:].upper() in characters_list:
            if tokens_list[i] == 'Macbeth' or tokens_list[i] == 'Macduff':
                if tokens_list[i-1] != 'Lady':
                    context_window.append(create_context_window(tokens_list, i, 30))
            else:
                context_window.append(create_context_window(tokens_list, i, 30))
        # for the name with two names
        if i != N-1:
            bigram = tokens_list[i]+' '+tokens_list[i+1]
            bigram_B = tokens_list[i][0]+tokens_list[i][1:].upper()+' '+tokens_list[i+1][0]+tokens_list[i][1:].upper()
            if bigram[:-1] in characters_list:
                context_window.append(create_context_window(tokens_list, i, 30))
            elif bigram_B in characters_list:
                context_window.append(create_context_window(tokens_list, i, 30))
        # for the special name 'SON' in text refering to the name 'BOY' in character dictionary
        if tokens_list[i][:-1] == 'SON':
            context_window.append(create_context_window(tokens_list, i, 30))
        
    # for each entity to check every context tokens
    for win in context_window:
        window_name_entity_list = []
        n = len(win)
        for a in range(n):
            if win[a][:-1] in characters_list:
                if win[a][:-1] == 'MACBETH' or win[a][:-1] == 'MACDUFF':
                    if win[a-1] != 'LADY':
                        window_name_entity_list.append(win[a][:-1])
                else:
                    window_name_entity_list.append(win[a][:-1])
            elif win[a][0]+win[a][1:].upper() in characters_list:
                if win[a] == 'Macbeth' or win[a] == 'Macduff':
                    if win[a-1] != 'Lady':
                        window_name_entity_list.append(win[a])
                else:
                    window_name_entity_list.append(win[a])
            
            if a != n-1:
                bigram = win[a]+' '+win[a+1]
                bigram_B = win[a][0]+win[a][1:].upper()+' '+win[a+1][0]+win[a][1:].upper()
                if bigram[:-1] in characters_list:
                    window_name_entity_list.append(bigram[:-1])
                elif bigram_B in characters_list:
                    window_name_entity_list.append(bigram_B.upper())
            
            if win[a][:-1] == 'SON':
                window_name_entity_list.append('BOY')
        window_name_entity_set = set(window_name_entity_list)
        window_relation_pairs = list(combinations(window_name_entity_set,2))
        converted_window_relation_pairs = [frozenset(elem) for elem in window_relation_pairs]
        for elem in converted_window_relation_pairs:
            if elem in relation_dict:
                relation_dict[elem] += 1

    # convert the relation dictionary to the format which can be implemented by graphviz
    pairs_list = [tuple(elem) for elem in relation_dict.keys()]
    frequency_list = relation_dict.values()
    converted_relation_list = [(pair, frequency) for pair, frequency in zip(pairs_list, frequency_list)]
    return converted_relation_list

def visualise_character_relation(characters_list, relation_list_A, relation_list_B):
    """
    Visualize the results of two relation recognizer

    Parameters:
        character_list (list): a list of characters
        relation_list_A (list): a list of character pairs and their frequency from relation recognizer A
        relation_list_B (list): a list of character pairs and their frequency from relation recognizer B

    """
    graph1 = Digraph()
    for character in characters_list:
        graph1.node(character)
    for pair in relation_list_A:
        edge, frequency = pair
        if frequency != 0:
            graph1.edge(*edge, label=str(frequency), dir='none')
    graph1.render('character_relation_A', view=True)
    graph2 = Digraph()
    for character in characters_list:
        graph2.node(character)
    for pair in relation_list_B:
        edge, frequency = pair
        if frequency != 0:
            graph2.edge(*edge, label=str(frequency), dir='none')
    graph2.render('character_relation_B', view=True)


if __name__ == '__main__':
    # character dictionary
    characters = read_character_dict('/Users/jiayou/Downloads/CharacterDict.txt')
    # the result of dictionary-based NER
    result = dict_ner('/Users/jiayou/Downloads/CharacterDict.txt', '/Users/jiayou/Downloads/Macbeth.txt')
    print('\n-----------------------------------character dictionary---------------------------------')
    print(sorted(characters))
    print('\n-----------------------------------NER result---------------------------------')
    print(sorted(set(result)))
    # compare the NER with the character dictionary
    print('\n-----------------------------------check the result---------------------------------')
    print(compare_ner_with_dict(result,characters))
    # the relation recognizer based on the scene
    relations_A = relation_recognizer('/Users/jiayou/Downloads/Macbeth.txt', '/Users/jiayou/Downloads/CharacterDict.txt')
    # the relation recognizer based on the context window
    relations_B = relation_recognizer_modified('/Users/jiayou/Downloads/Macbeth.txt', '/Users/jiayou/Downloads/CharacterDict.txt')
    # compare the top 10 character relation of two versions of recognizer
    print('\n-----------------------------------top 10 result of version A---------------------------------')
    print(sorted(relations_A, key=lambda i:i[1], reverse= True)[:10])
    print('\n-----------------------------------ctop 10 result of version B---------------------------------')
    print(sorted(relations_B, key=lambda i:i[1], reverse= True)[:10])
    # visualize the character relation
    visualise_character_relation(characters, relations_A, relations_B)



