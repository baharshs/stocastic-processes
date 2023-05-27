import streamlit as st
import graphviz
from graph_tools import Graph
import random
import seaborn as sns


graph_viz = graphviz.Graph()
graph = Graph(directed=False, multiedged=False)
population = []
sum_k_u = 0
girls_sum_k_u = 0
boys_sum_k_u = 0
girls_seen_count = 0
boys_seen_count = 0


def walk():
    global sum_k_u
    global girls_sum_k_u
    global boys_sum_k_u
    global girls_seen_count
    global boys_seen_count
    visits = {node: 0 for node in population}
    path = [starting_node]
    current = starting_node
    for i in range(main_count):
        current = random.choice(graph.neighbors(current))
        visits[current] += 1
        path.append(current)

    visits = {k: v for k, v in sorted(visits.items(), key=lambda item: item[1])}
    st.text(f'Path: {" -> ".join(path)}')
    palette = sns.color_palette("light:#5A9", len(population)).as_hex()
    if show_graph:  # if checkbox checked
        for idx, key in enumerate(visits.keys()):
            graph_viz.node(key, f'{key}-{visits.get(key)}', style='filled', fillcolor=palette[idx])
    else:
        for node in population:
            if 'G' in node:
                graph_viz.node(node, f'{node}-{visits.get(node)}', style='filled', fillcolor='#32a846')
            else:
                graph_viz.node(node, f'{node}-{visits.get(node)}', style='filled', fillcolor='#2a74ad')

    for key in visits.keys():
        if 'G' in key:
            girls_seen_count += visits.get(key)
        else:
            boys_seen_count += visits.get(key)

    with open('output.txt', mode='w') as f:

        f.write(f'{" -> ".join(path)}\n')

        for key in visits.keys():
            try:
                value = visits.get(key) / graph.degree(key)
                f.write(f'{key}:{visits.get(key)}, {value}\n')
                if 'G' in key:
                    girls_sum_k_u += value
                else:
                    boys_sum_k_u += value
                sum_k_u += value
            except ZeroDivisionError:
                f.write(f'{key}:{visits.get(key)}, {0} Degree\n')
        f.write(f'Girls Sum:{girls_seen_count}\n')
        f.write(f'Boys Sum:{boys_seen_count}\n')
        f.write(f'Total K U Sum:{sum_k_u}\n')
        f.write(f'Girls K U Sum:{girls_sum_k_u}\n')
        f.write(f'Boys K U Sum:{boys_sum_k_u}\n')
        try:
            f.write(f'{girls_sum_k_u/sum_k_u}')
        except ZeroDivisionError:
            f.write(f'{0}')


with st.sidebar:
    with st.form("nodes_form"):
        boys_nodes_count = st.number_input('Number of Boys', value=0)  # 5 B1 B2 B3 B4 B5
        girls_nodes_count = st.number_input('Number of Girls', value=0)

        nodes_count = boys_nodes_count + girls_nodes_count

        girls_degrees_sigma = st.number_input('Girls Edges(sum)', value=0)
        boys_degrees_sigma = st.number_input('Boys Edges(sum)', value=0)
        girls = [f'G{i}' for i in range(1, int(girls_nodes_count) + 1)]  # inline for
        boys = [f'B{i}' for i in range(1, int(boys_nodes_count) + 1)]

        main_count = st.number_input('Random Walk Count', value=0)
        starting_node = st.text_input('Starting Node')
        show_graph = st.checkbox('Distributed Formatted Graph', value=True)
        submitted = st.form_submit_button("Apply")
        boys_sigma = 0
        girls_sigma = 0
        if submitted:
            population = girls + boys
            random.shuffle(population)

            while girls_sigma < girls_degrees_sigma:
                node = random.choice(girls)

                while True:
                    target_node = random.choice(population)
                    if node == target_node:
                        continue
                    target_gender = target_node[0]

                    if len(graph.edges_at(target_node)) == nodes_count - 1:
                        continue

                    if target_gender == 'G' and girls_degrees_sigma - girls_sigma == 1:
                        continue
                    if target_node in graph.neighbors(node):
                        continue
                    break
                graph.add_edge(node, target_node)
                if 'B' in target_node:
                    boys_sigma += 1
                    girls_sigma += 1
                if 'G' in target_node:
                    girls_sigma += 2

            while boys_sigma < boys_degrees_sigma:
                node = random.choice(boys)

                while True:
                    target_node = random.choice(population)
                    if node == target_node:
                        continue
                    target_gender = target_node[0]

                    if len(graph.edges_at(target_node)) == nodes_count - 1:
                        continue
                    if target_gender == 'B' and boys_degrees_sigma - boys_sigma == 1:
                        continue
                    if target_node in graph.neighbors(node):
                        continue
                    break
                graph.add_edge(node, target_node)
                if 'G' in target_node:
                    boys_sigma += 1
                    girls_sigma += 1
                if 'B' in target_node:
                    boys_sigma += 2

            i = 0
            extra_girls = (girls_sigma - girls_degrees_sigma) / 2
            while i < int(extra_girls):  # G-G
                random_girl = random.choice(girls)
                neighbors = graph.neighbors(random_girl)
                if 'G' in str(neighbors):
                    for n in neighbors:
                        if 'G' in n:
                            graph.delete_edge(random_girl, n)

                            i += 1
                            break
                girls_sigma -= 2

            for edge in graph.edges():
                graph_viz.edge(edge[0], edge[1])

            walk()

st.graphviz_chart(graph_viz)
st.header('output')
st.text(f'Girls Sum:{girls_seen_count}\n')
st.text(f'Boys Sum:{boys_seen_count}\n')
st.text(f'Total K U Sum:{sum_k_u}\n')
st.text(f'Girls K U Sum:{girls_sum_k_u}\n')
st.text(f'Boys K U Sum:{boys_sum_k_u}\n')
try:
    st.text(f'P: {girls_sum_k_u / sum_k_u}')
except ZeroDivisionError:
    st.text(f'P: {0}')
