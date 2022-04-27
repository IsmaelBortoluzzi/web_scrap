import sqlite3
from requests_html import HTML, HTMLSession
from requests.exceptions import ChunkedEncodingError

connection = sqlite3.connect('unidades_medicas.db')
cursor = connection.cursor()

sql_select = cursor.execute("""
    SELECT treated_cities_fus.Nome, treated_cities_fus.Uf FROM treated_cities_fus
""").fetchall()

sql_insertion = """
    INSERT INTO ListaPossiveisClientes (Nome, TipoAtendimento, Endereço, Telefone, Cidade, Estado)
    VALUES %s
"""

values_to_insert = """"""
counter = 0

for city, state in sql_select:

    counter += 1
    print(counter)

    url = session = response = None
    try:
        url = f'https://www.cidadesdomeubrasil.com.br/{state}/{city}/hospitais'
        session = HTMLSession()
        response = session.get(url, allow_redirects=False)

    except ChunkedEncodingError as e:
        print('Deu aquele ChunkedEncodingError, vamo tentar de volta')
        try:
            url = f'https://www.cidadesdomeubrasil.com.br/{state}/{city}/hospitais'
            session = HTMLSession()
            response = session.get(url, allow_redirects=False)
        except:
            print('Não deu :/')
            with open('not_200_statuscode.txt', 'a') as file:
                file.write(f'{counter}: {city} - {state}, status code: {response.status_code}\n')
            continue

    except Exception as ex:  # exception inesperada
        print(ex)
        continue

    if response.status_code != 200:
        print('ops!', response.status_code)
        with open('not_200_statuscode.txt', 'a') as file:  # anotar qual cidade deu redirect ou server error
            file.write(f'{counter}: {city} - {state}, status code: {response.status_code}\n')
        continue

    medical_units = response.html.find('#no-more-tables', first=True)  # pegar a table de dados

    trs = medical_units.find('tr')
    table_data = trs[1:]  # tirar o título fora
    treated_medical_units_list = list()

    for td in table_data:
        has_phone_number = td.text.split('\n')

        if len(has_phone_number) == 3:  # se tem 3 é pq n tem telefonr
            has_phone_number.append('TELEFONE NÃO INFORMADO')
            treated_medical_units_list.append(has_phone_number)

        elif len(has_phone_number) == 4:  # se tem 4 ta tudo certo
            treated_medical_units_list.append(has_phone_number)

        else:  # senão os dados estão inconsistente
            continue

        row_values = "("  # monta a query
        for value in has_phone_number:
            row_values += f"'{value}',"

        formatted_city_name = city.replace('_', ' ').upper()
        formatted_uf_name = state.upper()

        row_values += f"'{formatted_city_name}','{formatted_uf_name}'),"
        values_to_insert += row_values  # acumula a query de todos os valores pra depois fazer o insert no banco

    try:
        cursor.execute(sql_insertion % values_to_insert[:-1] + ';')
        connection.commit()
    except sqlite3.OperationalError:  # por segunça deixar no except
        with open('cidades_com_OperationalError.txt', 'a') as file:
            file.write(f'{counter}: {city} - {state}, verificar individualmente: {response.status_code}\n')
        continue

connection.close()
