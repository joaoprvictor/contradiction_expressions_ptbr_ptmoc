# -*- coding: utf-8 -*-
"""pt_br_processing

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gpyVxf17dnFgO3cRNc0QGFzL6eY0AVUz
"""

import pandas as pd

dataframe_coral = pd.read_excel('/content/allPosUtterancesDf_excel_2023-05-21.xlsx')

dataframe_coral_selected = dataframe_coral[["file", "person_code", "turn", 'clean_utterance']]

dataframe_coral_selected = dataframe_coral_selected.astype(str)

# Define a function to count tokens in a text
def count_tokens(text):
    tokens = text.split()
    return len(tokens)


# Tokenize the "clean_utterance" column and count tokens
dataframe_coral_selected['num_tokens'] = dataframe_coral_selected['clean_utterance'].apply(lambda x: count_tokens(x))

coral_tokens = dataframe_coral_selected.groupby('person_code')["num_tokens"].sum()

coral_tokens[:5]

expressions = ['antes','ao passo que','contudo',' e sim','em todo caso','entretanto',
               'mas ', 'não obstante','no entanto','porém','senão','só que ','todavia']

# Create a regular expression pattern by joining your 'expressions' list with '|'
pattern = '|'.join(expressions)


# Fill missing values with an empty string (you can choose a different value if needed)
dataframe_coral_selected['clean_utterance'] = dataframe_coral_selected['clean_utterance'].fillna('')

# Filter the DataFrame based on the 'clean_utterance' column using the regular expression pattern
filtered_df = dataframe_coral_selected[dataframe_coral_selected['clean_utterance'].str.contains(pattern, case=False, regex=True)]

# Add a new column 'Expressão' that contains the matched expressions for each row
filtered_df['Expressão'] = filtered_df['clean_utterance'].str.findall(pattern)

filtered_df[:5]

filtered_df_exploded = filtered_df.explode('Expressão')
# Get a list of unique strings in the "Expressão" column
unique_strings = filtered_df_exploded['Expressão'].unique()

# Create new columns for each unique string and count their occurrences in each row
for string in unique_strings:
    filtered_df_exploded[string] = filtered_df_exploded['Expressão'].apply(lambda x: str(x).count(str(string)))

# Group by the original index (assuming you want to keep the original row structure)
new_df_filtered = filtered_df_exploded.groupby(filtered_df_exploded.index).max()

column_name_mapping = {
    'só que ': 'só que',
    'mas ': 'mas',
    ' e sim': 'e sim'
}

# Use the rename method to rename the columns
new_df_filtered.rename(columns=column_name_mapping, inplace=True)

# Reset the index if needed
new_df_filtered = new_df_filtered.reset_index()

new_df_filtered.columns

# dataframe com as informações de contexto
path = '/content/drive/MyDrive/JVPESSOA D.&L CONSULTING/consultorias/br-mocam/resultados/'
new_df_filtered.to_csv(path+"pt_br_enunciados.csv")
new_df_filtered.to_excel(path+"pt_br_enunciados.xlsx")

new_df_filtered[new_df_filtered["person_code"] == "bfamcv01EVN"]

grouped_df = new_df_filtered.groupby('person_code')[['person_code', 'mas', 'antes', 'só que', 'senão', 'porém', 'contudo',
       'e sim']].sum()

# Reset the index if needed
grouped_df = grouped_df.reset_index()

grouped_df_merged = pd.merge(coral_tokens, grouped_df, on="person_code")

# Define the columns to perform the operation on
columns_to_transform = ['mas', 'antes', 'só que', 'senão', 'porém', 'contudo','e sim']

# Create new columns with the normalized values
for col in columns_to_transform:
    new_col_name = col + '_normalizado'
    grouped_df_merged[new_col_name] = round((grouped_df_merged[col] / grouped_df_merged['num_tokens'].sum()) * 1000, 2)

"""## Metadados"""

coral_metadados = pd.read_csv('/content/allPeopleInfoDf_csv_2023-05-21.csv')

coral_metadados_selected = coral_metadados[['file', "person_code", 'sex', 'age', 'schooling']]

"""## tabela completa"""

grouped_df_merged.columns

all_info = pd.merge(grouped_df_merged, coral_metadados_selected, on="person_code")
all_info = all_info[['person_code', 'sex', 'age',
       'schooling', 'num_tokens', 'mas', 'antes', 'só que', 'senão', 'porém',
       'contudo', 'e sim', 'mas_normalizado', 'antes_normalizado',
       'só que_normalizado', 'senão_normalizado', 'porém_normalizado',
       'contudo_normalizado', 'e sim_normalizado']]

all_info_filtered = all_info[all_info['schooling'] != "x"]
all_info_filtered = all_info_filtered[all_info_filtered['sex'] != "x"]
all_info_filtered = all_info_filtered[all_info_filtered['age'] != "x"]

# dataframe com as informações de contagem
path = '/content/drive/MyDrive/JVPESSOA D.&L CONSULTING/consultorias/br-mocam/resultados/'
all_info_filtered.to_csv(path+"pt_br_contagem.csv")
all_info_filtered.to_excel(path+"pt_br_contagem.xlsx")

# # Find rows in df1 that are not in df2 based on 'person_code'
# rows_to_delete = new_df_filtered[~new_df_filtered['person_code'].isin(all_info_filtered['person_code'])]

# # Delete the rows from df1
# df_edited = new_df_filtered[~new_df_filtered['person_code'].isin(rows_to_delete['person_code'])]

# Select only the numeric columns
numeric_columns = ['antes',
       'só que', 'mas', 'porém', 'senão', 'e sim']
# Calculate the total sum of specific numeric columns for each row and store it in a new column
all_info_filtered['soma_adversativas'] = all_info_filtered[numeric_columns].sum(axis=1)

# Select only the numeric columns part 2
numeric_columns_normalized = ['antes_normalizado', 'só que_normalizado',
       'mas_normalizado', 'porém_normalizado', 'senão_normalizado',
       'e sim_normalizado']
# Calculate the total sum of specific numeric columns for each row and store it in a new column
all_info_filtered['soma_adversativas_normalizada'] = all_info_filtered[numeric_columns_normalized].sum(axis=1)

# Define a function to count the total number of string items in a list
def count_string_items(lst):
    return len(lst)

# INFORMAÇÕES SOBRE O DATASET
info1 = f"o número final de falantes é {len(all_info_filtered)}\n====\n"
info2 = f"o número total de tokens (contagem bruta) é {all_info_filtered['num_tokens'].sum()}\n====\n"
info3 = f"o número TOTAL de expressões adversativas (contagem bruta) é {all_info_filtered['soma_adversativas'].sum()}\n====\n"
print(info1, info2, info3)

with open("informações_coral.txt", "a") as corpus_info_txt:
  corpus_info_txt.write(info1)
  corpus_info_txt.write(info2)
  corpus_info_txt.write(info3)

info4 = f'O número de pessoas por grau de escolaridade é \n{all_info_filtered["schooling"].value_counts()}\n============\n'
info5 = f'O número de pessoas por faixa etária é \n{all_info_filtered["age"].value_counts()}\n============\n'
info6 = f'O número de pessoas por sexo é \n{all_info_filtered["sex"].value_counts()}\n============\n'
with open("informações_coral.txt", "a") as corpus_info_txt:
  corpus_info_txt.write(info4)
  corpus_info_txt.write(info5)
  corpus_info_txt.write(info6)

info7 = f'O número de tokens por grau de escolaridade é \n{all_info_filtered.groupby("age")["num_tokens"].sum()}\n============\n'
info8 = f'O número de tokens por faixa etária é \n{all_info_filtered.groupby("schooling")["num_tokens"].sum()}\n============\n'
info9 = f'O número de tokens por sexo é \n{all_info_filtered.groupby("sex")["num_tokens"].sum()}\n============\n'
with open("informações_coral.txt", "a") as corpus_info_txt:
  corpus_info_txt.write(info7)
  corpus_info_txt.write(info8)
  corpus_info_txt.write(info9)

info10 = f'O número de expressões adversativas (contagem bruta) por grau de escolaridade é \n{all_info_filtered.groupby("age")["soma_adversativas"].sum()}\n============\n'
info11= f'O número de expressões adversativas (contagem bruta)por faixa etária é \n{all_info_filtered.groupby("schooling")["soma_adversativas"].sum()}\n============\n'
info12 = f'O número de expressões adversativas (contagem bruta) por sexo é \n{all_info_filtered.groupby("sex")["soma_adversativas"].sum()}\n============\n'

with open("informações_coral.txt", "a") as corpus_info_txt:
  corpus_info_txt.write(info10)
  corpus_info_txt.write(info11)
  corpus_info_txt.write(info12)

import matplotlib.pyplot as plt
# Flatten the list of lists in the "Expressão" column into a single list of strings
expressions = [expr for sublist in filtered_df['Expressão'] for expr in sublist]
# Create a pandas Series from the flattened list
expressions_series = pd.Series(expressions)

# Use value_counts() to count the occurrences of each string
expression_counts = expressions_series.value_counts()

# Plot the counts
expression_counts.plot(kind='bar', figsize=(10, 6), color = "orange")
plt.xlabel('Expressões de adversidade')
plt.ylabel('Quantidade')
plt.title('Número de expressões adversativas no C-ORAL-BRASIL I')
plt.savefig('/content/drive/MyDrive/JVPESSOA D.&L CONSULTING/consultorias/br-mocam/resultados/n_expressoes_ptbr.png',
            dpi=300, bbox_inches="tight")
plt.show()