from shiny.express import input, render, ui
from shiny import reactive
import pandas as pd

import matplotlib.pyplot as plt
import networkx as nx

from app_helper import data, example_networkx_graph

ui.input_text("word", "Enter word:", value="CONSTITUTION")

G = example_networkx_graph()
@render.plot
def graph():
    fig, ax = plt.subplots(figsize=(5, 5))
    nx.draw(G, with_labels=True, node_size=400, ax=ax)
    return fig


ui.input_slider("n", "N", 0, 100, 20)

@render.table
def txt():
    return data.head(input.n())
