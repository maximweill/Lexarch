import pandas as pd
import networkx as nx

def load_data():
    df = pd.read_csv("final_dataset.csv")
    df.dropna(inplace=True)
    for col in ("Pronunciation", "Syllables"):
        df[col] = df[col].apply(lambda string_list: eval(string_list))
    
    return df
data = load_data()

def example_networkx_graph():
    G = nx.karate_club_graph()
    return G
