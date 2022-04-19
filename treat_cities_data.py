import sqlite3
import pandas as pd
from requests_html import HTML, HTMLSession

connection = sqlite3.connect('unidades_medicas.db')
cursor = connection.cursor()

cidades_ufs = pd.read_sql_query("""
    SELECT Cidade.Nome, Estado.Uf FROM Cidade LEFT JOIN Estado ON Cidade.EstadoId = Estado.Id
""", connection)

df = pd.DataFrame(cidades_ufs)

df['Uf'] = df['Uf'].str.lower()
df['Nome'] = df['Nome'].str.replace(' ', '_').str.lower()
df['Nome'] = df['Nome'].str.replace('_d_o', '_do_o')
df['Nome'] = df['Nome'].str.replace('_d_agua', '_da_agua')
df['Nome'] = df['Nome'].str.replace('_d_arco', '_do_arco')
df['Nome'] = df['Nome'].str.replace('_d_alho', '_do_alho')
df['Nome'] = df['Nome'].str.replace('_d_', '_da_')

print(df.to_string())

df.to_sql('treated_cities_fus', con=connection, if_exists='replace')

connection.commit()
connection.close()
