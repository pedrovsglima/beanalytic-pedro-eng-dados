import json
import urllib.request
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# lê um arquivo JSON e retorna uma lista de dicionários
def get_data(file):
    with open(file, "r", encoding="utf8") as f:
        data = json.load(f)
    return data

# retorna todas as chaves presentes em uma lista de dicionários
def get_all_keys_as_list(dictionary):
    all_keys = list( set().union( *(d.keys() for d in dictionary) ) )
    return all_keys


class Spreadsheet():

    SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    CONSOLIDATION_WORKSHEET = "DATA CONSOLIDATION"
    HEADER_INDEX = 1
    HEADER_FIRST_CELL = CONSOLIDATION_WORKSHEET+"!A1"

    # a inicialização consiste em se conectar com a referente planilha e deixá-la disponível para trabalho
    def __init__(self, credentials, spreadsheet_key):
        self.spreadsheet_key = spreadsheet_key
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(credentials, Spreadsheet.SCOPE)
        self.client = gspread.authorize(self.creds)
        self.spreadsheet = self.client.open_by_key(self.spreadsheet_key)

    # cria uma aba na planilha com o nome escolhido
    def _create_worksheet(self, worksheet_name):
        return self.spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=20)

    # retorna uma lista contendo todas as abas existentes em uma planilha
    def list_worksheets(self):
        worksheet_objs = self.spreadsheet.worksheets()
        worksheets_list = [worksheet.title for worksheet in worksheet_objs]
        return worksheets_list

    # recebe um conjunto de dados e um cabeçalho, esta função retorna uma lista que garante que a planilha será preenchida conforme o cabeçalho
    def _arrange_values_to_insert(self, data, column_header):
        # mapeamento cabeçalho e chave
        header_to_key = { i : i for i in column_header }
        list_values_to_insert = []
        
        # o algoritmo organiza os dados de acordo com o cabeçalho e, caso um registro não tenha determinada chave, o valor referente ficará em branco
        for instance in data:
            arrange_key_to_header = []
            for column in column_header:
                try:
                    arrange_key_to_header.append( instance[ header_to_key[column] ] )
                except:
                    arrange_key_to_header.append("")
            list_values_to_insert.append(arrange_key_to_header)

        return list_values_to_insert
    
    # insere um conteúdo em uma determinada aba, garantindo o alinhamento com o cabeçalho
    def insert_values(self, data, column_header, worksheet_name):
        self.data = data
        self.last_header = column_header

        # cria uma aba, caso esta ainda não exista
        if worksheet_name not in self.list_worksheets(): self._create_worksheet(worksheet_name)
        
        # define a planilha de trabalho
        self.current_worksheet = self.spreadsheet.worksheet(worksheet_name)
        
        # insere cabeçalho
        self.current_worksheet.insert_row(self.last_header, Spreadsheet.HEADER_INDEX)

        # garante alinhamento entre conteúdo e cabeçalho
        list_values_to_insert = self._arrange_values_to_insert(self.data, self.last_header)

        # anexa os dados
        self.spreadsheet.values_append(worksheet_name, {'valueInputOption': 'USER_ENTERED'}, {'values': list_values_to_insert})

    # consolida os dados de todas as planilhas em uma única
    def consolidation(self):
        # caso ainda não esteja criada, cria a aba "DATA CONSOLIDATION"
        if Spreadsheet.CONSOLIDATION_WORKSHEET not in self.list_worksheets(): self._create_worksheet(Spreadsheet.CONSOLIDATION_WORKSHEET)
        
        # define a planilha de trabalho
        self.data_consolidation_worksheet = self.spreadsheet.worksheet(Spreadsheet.CONSOLIDATION_WORKSHEET)
        
        ### 1. garantir que todas as chaves possíveis estejam como cabeçalho
        # lê o cabeçalho atual
        self.current_header = self.data_consolidation_worksheet.row_values(Spreadsheet.HEADER_INDEX)
        # se necessário, anexa ao cabeçalho atual as chaves presentes na última aba criada
        self.current_header.extend([i for i in self.last_header if i not in self.current_header])
        # escreve o novo cabeçalho
        self.spreadsheet.values_update(Spreadsheet.HEADER_FIRST_CELL, {'valueInputOption': 'USER_ENTERED'}, {'values': [self.current_header]})

        ### 2. ter uma lista com todos os emails da aba DATA CONSOLIDATION
        # definiu-se o 'email' como chave identificadora
        key = "email"
        # verifica em que célula está localizada a chave identificadora
        email_cell = self.data_consolidation_worksheet.find(key)
        # armazena todas os emails presentes na aba "DATA CONSOLIDATION"
        emails_data_consolidation = self.data_consolidation_worksheet.col_values(email_cell.col)[1:]

        ### 3. verificar quais emails da última aba criada ainda não constam na aba "DATA CONSOLIDATION"
        # quando o email não estiver presente, armazena todo o registro para que ele possa ser consolidado
        new_rows = [instance for instance in self.data if instance.get(key) not in emails_data_consolidation]

        ### 4. atualizar aba "DATA CONSOLIDATION"
        # garante alinhamento entre conteúdo e cabeçalho
        list_values_to_insert = self._arrange_values_to_insert(new_rows, self.current_header)
        # anexa os novos dados
        self.spreadsheet.values_append(Spreadsheet.CONSOLIDATION_WORKSHEET, {'valueInputOption': 'USER_ENTERED'}, {'values': list_values_to_insert})


def main():

    # dados referentes à planilha utilizada e às credenciais que autorizam acesso
    CREDENTIALS = "../client_secrets.json"
    SPREADSHEET_KEY = "1TEYK3XHPNlq0iLdqDpW63BC0tcTkl3VUOe5fgG7bpkM"

    # dados referentes ao arquivo JSON disponibilizado
    SOURCE_FILE_ID = "1WaymK35JtvGMsHtjck4EFJlFUSyPfz8r"
    URL_SOURCE_FILE = f"https://docs.google.com/uc?export=download&id={SOURCE_FILE_ID}"
    SOURCE_FILE = "../data.json"
    # download via link do arquivo JSON disponibilizado
    urllib.request.urlretrieve(URL_SOURCE_FILE, SOURCE_FILE)
    
    # arquivo criado e utilizado apenas para testar o algoritmo de consolidação dos dados
    #SOURCE_FILE = "../testing-data-consolidation.json"

    # transforma o arquivo JSON em uma lista de dicionários
    data = get_data(SOURCE_FILE)
    # organiza por ordem alfabética todas as chaves existentes
    data_keys = sorted(get_all_keys_as_list(data))
    # carimbo data e hora para utilizar como nome da aba da planilha
    worksheet_name = datetime.today().strftime("%Y-%m-%d %H.%M.%S")

    # cria objeto da classe Spreadsheet, informando qual planilha quer acessar e as devidas credenciais
    spreadsheet = Spreadsheet(CREDENTIALS, SPREADSHEET_KEY)
    # insere os valores do arquivo JSON na devida aba
    spreadsheet.insert_values(data, data_keys, worksheet_name)
    # consolida os dados de todas as abas
    spreadsheet.consolidation()


if __name__ == '__main__':
    main()    
