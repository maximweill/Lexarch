import pandas as pd
import os
import ast
import itertools

# ---------------------------------------------------------
# SETUP & LOAD DATA
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(BASE_DIR, 'word_dataset_with_difficulties.csv')

def safe_eval(val):
    """Safely evaluates a string literal to a list, returns empty list on failure."""
    try:
        return ast.literal_eval(val)
    except (ValueError, SyntaxError):
        return []

if os.path.exists(input_file):
    df = pd.read_csv(input_file)
    
    # --- CRITICAL FIXES FOR CSV LOADING ---
    # 1. Strip whitespace from column names
    df.columns = df.columns.str.strip()
    # 2. Remove invisible BOM characters (fixes KeyError: 'Word')
    df.rename(columns=lambda x: x.replace('\ufeff', ''), inplace=True)
    
    # 3. Use safe_eval to prevent crashes on bad data
    df['Syllables'] = df['Syllables'].apply(lambda x: safe_eval(x) if isinstance(x, str) else x)
    df['Pronunciation'] = df['Pronunciation'].apply(lambda x: safe_eval(x) if isinstance(x, str) else x)
else:
    print(f"Warning: {input_file} not found in spelling_bee_map. Backend will fail.")
    df = pd.DataFrame() 

minimum = 5/100
maximum = 10/100

# ---------------------------------------------------------
# HELPER: GET WORD DATA (For the UI)
# ---------------------------------------------------------
def get_word_data(word):
    """
    Looks up a word and returns its syllables/pronunciation for the UI.
    """
    if df.empty: return None

    word = word.upper().strip()
    
    # Ensure 'Word' column exists before checking
    if 'Word' not in df.columns:
        print("Error: 'Word' column missing from CSV in spelling_bee_map.")
        return None

    row = df[df['Word'] == word]
    
    if row.empty:
        return None
    
    return {
        'word': row.iloc[0]['Word'],
        'syllables': row.iloc[0]['Syllables'],
        'pronunciation': row.iloc[0]['Pronunciation']
    }

# ---------------------------------------------------------
# CORE LOGIC
# ---------------------------------------------------------
def similarly_hard(existing_words, confidence_metric, minimum, maximum):
    if df.empty or 'Spelling Difficulty' not in df.columns:
        return {}, {}, list(confidence_metric.keys()), existing_words

    difficulty_map = df.set_index('Word')['Spelling Difficulty'].to_dict()
    
    # 1. Block existing words + current input words
    current_batch_keys = list(confidence_metric.keys())
    temp_existing = set(existing_words)
    temp_existing.update(current_batch_keys)
    blocked_words = list(temp_existing) 
    
    similarity_map = []
    
    for word_key, word_dict in confidence_metric.items():
        target_diff = difficulty_map.get(word_key, None)
        if target_diff is None: continue
        
        for syl, pron in word_dict.items():
            similarity_map.append([target_diff, syl, pron])

    similar_sound = {}
    similar_spell = {}
    save = []
  
    # Randomize search order
    search_df = df.sample(frac=1).reset_index(drop=True)

    for row_index, row in search_df.iterrows():
        if row['Word'] in blocked_words: continue
            
        current_diff = row['Spelling Difficulty']
        current_syllables = row['Syllables']
        current_pronunciation = row['Pronunciation']

        if len(current_syllables) != len(current_pronunciation): continue

        for data in similarity_map:
            target_diff = data[0]
            target_syl = data[1]
            target_pron = data[2]

            # --- CHECK SPELLING ---
            if target_syl in current_syllables:
                if (target_diff - minimum) <= current_diff <= (target_diff + maximum):
                    similar_spell[row['Word']] = [target_syl]
                    blocked_words.append(row['Word']) 
                    break 
                elif current_diff < (target_diff - minimum - 0.1) or current_diff > (target_diff + maximum + 0.1):
                    save.append([row['Word'], target_syl])

            # --- CHECK SOUND ---
            if target_pron in current_pronunciation:
                indices = [i for i, x in enumerate(current_pronunciation) if x == target_pron]
                for idx in indices:
                    associated_syllable = current_syllables[idx]
                    
                    if (target_diff - minimum) <= current_diff <= (target_diff + maximum):
                        if associated_syllable != target_syl:
                            if row['Word'] not in blocked_words:
                                similar_sound[row['Word']] = {associated_syllable, target_pron}
                                blocked_words.append(row['Word'])

    # Backup Logic
    if not similar_spell and not similar_sound and len(save) > 0:
        limit = min(5, len(save))
        for i in range(limit):
            backup_word = save[i][0]
            if backup_word not in blocked_words:
                backup_syl = save[i][1]
                similar_spell[backup_word] = [backup_syl]
                blocked_words.append(backup_word)

    input_keys = list(confidence_metric.keys())
    return similar_spell, similar_sound, input_keys, blocked_words


def generate_test_words(tested_words, minimum, maximum):
    input_words = []
    all_words = []
    saved_dicts = {}
    
    existing_words = []
    for batch in tested_words:
        existing_words.extend(list(batch.keys()))
    
    for batch in tested_words:
        res1, res2, res3, updated_existing = similarly_hard(existing_words, batch, minimum, maximum)

        # --- SMART FILL LOGIC ---
        TARGET_NEW_WORDS = 9 
        all_spelling = list(res1.items())
        all_sounds = list(res2.items())
        
        final_sounds = all_sounds[:4]
        slots_taken = len(final_sounds)
        slots_needed = TARGET_NEW_WORDS - slots_taken
        final_spelling = all_spelling[:slots_needed]
        
        batch_generated = {}
        batch_generated.update(dict(final_spelling))
        batch_generated.update(dict(final_sounds))

        saved_dicts.update(batch_generated)
        input_words.append(res3)
        all_words.extend(res3)
        existing_words = updated_existing

    for i in saved_dicts.keys():
        all_words.append(i)
        
    all_words = list(set(all_words))
    
    return saved_dicts, input_words, all_words