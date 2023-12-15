import copy
import math
import pandas
import random

from pathlib import Path


def read_context(path_stimuli,
                 items_key = 'word'):
    """
    """
    stim = list(pandas.read_csv(path_stimuli)[items_key])

    return stim


def read_critical_verbs(path_stimuli,
                        intransitive_key = 'verb_intransitive',
                        ditransitive_key = 'verb_ditransitive'):
    """
    """
    stim = pandas.read_csv(path_stimuli)
    intransitives = list(stim[intransitive_key])
    ditransitives = list(stim[ditransitive_key])

    return [{'intransitive': intransitive, 'ditransitive': ditransitive} for intransitive, ditransitive in zip(intransitives, ditransitives)]


def shuffle_stimuli(stimuli):
    """
    """
    for stimulus_type in stimuli:
        random.shuffle(stimuli[stimulus_type])


def generate_list_conditions(num_lists,
                             possible_conditions = ['intransitive', 'ditransitive']):
    """
    """
    random.shuffle(possible_conditions)
    list_conditions = possible_conditions * num_lists
    list_conditions = list_conditions[:num_lists]
    random.shuffle(list_conditions)

    return list_conditions


def generate_trial_frame(stimuli,
                         trial_order = ['ADJ', 'AN', 'CRIT', 'ADJ', 'AN', 'IN']):
    """
    """
    trial = []
    for item in trial_order:
        trial.append(stimuli[item].pop())

    return trial


def generate_list_frame(stimuli,
                        crit_key = 'CRIT'):
    """
    """
    stimuli_copy = copy.deepcopy(stimuli)
    shuffle_stimuli(stimuli = stimuli_copy)

    all_lists = []
    for _ in range(len(stimuli[crit_key])):
        all_lists.append(generate_trial_frame(stimuli = stimuli_copy))

    return all_lists


def generate_participant(frame, frame_condition, list_conditions,
                         num_blocks = 4,
                         participant_id = 0,
                         crit_position = 2,
                         col_order = ['participant_id',
                                      'experiment_section',
                                      'frame_condition',
                                      'block_num',
                                      'trial_num',
                                      'list_condition',
                                      'crit_pair',
                                      'crit_word',
                                      'study_list',
                                      'study_position',
                                      'study_word'],
                         participant_dir = 'participants_trial_info'):
    """
    """
    participant_file = f'trial_structure_participant_{participant_id}.tsv'
    participant_path = Path.cwd().joinpath(participant_dir).joinpath(participant_file)
    participant_path.parent.mkdir(exist_ok = True)

    # Blockify
    all_blocks = list(range(num_blocks)) * len(frame)
    all_blocks = all_blocks[:len(frame)]
    all_blocks.sort()

    # Generate tracking variables for each list
    participant_ids = [participant_id] * len(frame)
    frame_conditions = [frame_condition] * len(frame)
    trial_nums = list(range(len(frame)))
    crit_pairs = []
    crit_words = []
    all_trials = []
    all_positions = []

    # Generate a row for each list
    for trial_frame_words, condition in zip(frame, list_conditions):
        crit_pairs.append(trial_frame_words[crit_position])
        crit_words.append(trial_frame_words[crit_position][condition])

        trial_frame_words[crit_position] = trial_frame_words[crit_position][condition]

        all_positions.append(list(range(len(trial_frame_words))))
        all_trials.append(trial_frame_words)

    # Generate a pandas dataframe
    df = pandas.DataFrame({'participant_id': participant_ids,
                           'experiment_section': 'presentation',
                           'frame_condition': frame_conditions,
                           'block_num': all_blocks,
                           'trial_num': trial_nums,
                           'list_condition': list_conditions,
                           'crit_pair': crit_pairs,
                           'crit_word': crit_words,
                           'study_list': all_trials,
                           'study_positions': all_positions})

    # Janky solution: Explode the dataframe so that we have 1 word in the study list per row
    list_index = df['study_positions'].explode()
    list_elements = df[['trial_num', 'study_list']].explode('study_list')
    list_elements['study_positions'] = list_index
    list_elements.rename(columns = {'study_list': 'study_word',
                                    'study_positions': 'study_position'},
                         inplace = True)

    df_long = list_elements.merge(df, on = 'trial_num')
    df_long = df_long[col_order]

    df_long.to_csv(participant_path, sep = '\t', index = False, index_label = False)

    return


def generate_frame_conditions(num_participants, possible_conditions):
    """
    """
    random.shuffle(possible_conditions)
    frame_conditions = possible_conditions * num_participants
    frame_conditions = frame_conditions[:num_participants]
    random.shuffle(frame_conditions)

    return frame_conditions


def generate_participants(num_participants, frames,
                          participant_dir = 'participants_trial_info'):
    """
    """
    frame_conditions = generate_frame_conditions(num_participants = num_participants,
                                                 possible_conditions = list(frames.keys()))

    for frame_condition, participant_number in zip(frame_conditions, range(num_participants)):
        frame_copy = copy.deepcopy(frames[frame_condition])
        random.shuffle(frame_copy)  # Shuffle order of lists
        list_conditions = generate_list_conditions(num_lists = len(frame_copy))

        generate_participant(frame = frame_copy,
                             frame_condition = frame_condition,
                             list_conditions = list_conditions,
                             participant_id = participant_number)


if __name__ == '__main__':
    random.seed(9)

    path_anim_nouns = Path.cwd().joinpath('stimuli/animate_nouns.csv')
    path_inanim_nouns = Path.cwd().joinpath('stimuli/inanimate_nouns.csv')
    path_adjs = Path.cwd().joinpath('stimuli/adjectives.csv')
    path_verbs = Path.cwd().joinpath('stimuli/critical_verbs.csv')

    anim_nouns = read_context(path_stimuli = path_anim_nouns)
    inanim_nouns = read_context(path_stimuli = path_inanim_nouns)
    adjs = read_context(path_stimuli = path_adjs)
    crits = read_critical_verbs(path_stimuli = path_verbs)

    stimuli = {'AN': anim_nouns,
               'IN': inanim_nouns,
               'ADJ': adjs,
               'CRIT': crits}

    frame_a = generate_list_frame(stimuli = stimuli)
    frame_b = generate_list_frame(stimuli = stimuli)

    generate_participants(num_participants = 300,
                          frames = {'a': frame_a,
                                    'b': frame_b})