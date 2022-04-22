from requests_html import HTML, HTMLSession
import sqlite3

connection = sqlite3.connect('/media/dev2/5E8D11D5735BC2C8/the_db/unidades_medicas.db')
cursor = connection.cursor()

# cursor.execute("""DROP TABLE ListaPossiveisClientes""")

# cursor.execute("""CREATE TABLE ListaPossiveisClientes(
# Id INTEGER PRIMARY KEY AUTOINCREMENT,
# Nome VARCHAR(255),
# TipoAtendimento VARCHAR(255),
# Endereço VARCHAR(255),
# Telefone VARCHAR(255),
# Cidade VARCHAR(255)
# )""")

# cursor.execute(
#         '''
#             CREATE TABLE IF NOT EXISTS ListaPossiveisClientes
#               (Id INT, Nome VARCHAR, TipoAtendimento VARCHAR, Endereço VARCHAR, Telefone VARCHAR)
#         '''
#     )

sql_insertion = """
INSERT INTO ListaPossiveisClientes (Nome, TipoAtendimento, Endereço, Telefone, Cidade)
VALUES %s
"""

url = 'https://www.cidadesdomeubrasil.com.br/sc/chapeco/hospitais'
session = HTMLSession()
medical_units = session.get(url)

medical_units = medical_units.html.find('#no-more-tables', first=True)

trs = medical_units.find('tr')
table_heads = trs[0]
table_data = trs[1:]
values_to_insert = ""

treated_medical_units_list = list()
for td in table_data:

    has_phone_number = td.text.split('\n')

    if len(has_phone_number) < 4:
        has_phone_number.append('TELEFONE NÃO INFORMADO')
        treated_medical_units_list.append(has_phone_number)
    else:
        treated_medical_units_list.append(has_phone_number)

    row_values = "("
    for value in has_phone_number:
        row_values += f"'{value}',"
    # row_values = row_values[:-1]
    row_values += "'Chapecó'),"

    values_to_insert += row_values

values_to_insert = values_to_insert[:-1] + ';'
cursor.execute(sql_insertion % values_to_insert)

print(*treated_medical_units_list)

connection.commit()
connection.close()
