import json
import pandas as pd

def json_to_csv_pronunciation(json_file: str, csv_file: str) -> None:
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    rows = []
    for pron, syll_dict in data.items():
        for syll, word_dict in syll_dict.items():
            if syll == "_total":
                continue
            for word, freq in word_dict.items():
                if word == "_total":
                    continue
                rows.append({
                    "Pronunciation": pron,
                    "Syllable": syll,
                    "Word": word,
                    "Frequency": freq
                })

    df = pd.DataFrame(rows)
    df.to_csv(csv_file, index=False, encoding="utf-8")

def json_to_csv_spelling(json_file: str, csv_file: str) -> None:
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    rows = []
    for syll, pron_dict in data.items():
        for pron, word_dict in pron_dict.items():
            if pron == "_total":
                continue
            for word, freq in word_dict.items():
                if word == "_total":
                    continue
                rows.append({
                    "Syllable": syll,
                    "Pronunciation": pron,
                    "Word": word,
                    "Frequency": freq
                })

    df = pd.DataFrame(rows)
    df.to_csv(csv_file, index=False, encoding="utf-8")

def main():
    json_to_csv_pronunciation("pronunciation_search.json", "pronunciation_search.csv")
    json_to_csv_spelling("spelling_search.json", "spelling_search.csv")

if __name__ == "__main__":
    main()
