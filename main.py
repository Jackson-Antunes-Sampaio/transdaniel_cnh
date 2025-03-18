from dataclasses import dataclass
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import time

base_url = 'https://transito.mg.gov.br/infracoes/multa/consultar-pontuacao-cnh/'

df = pd.read_excel('pontuacao CNH.xlsx')

@dataclass
class KeyModel:
    name: str
    value: str


def get_initial():
    url = base_url

    headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'pt-BR,pt;q=0.9',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    }

    response = requests.request("GET", url, headers=headers)

    # print(response.text)
    cookies = response.cookies
    csrfToken = cookies['csrfToken']

    site = BeautifulSoup(response.text, "html.parser")

    redirectPostToken = site.find('input', {"name" : "_redirectPostToken"}).get('value')
    form_groups = site.find_all('div', class_="form-group text")

    keysModel : KeyModel = []

    for item in form_groups:

        form_control = item.find('input', {'class' : 'form-control', 'type' : 'text', 'style' : 'display:none'})
        
        if form_control != None:
            keysModel.append(KeyModel(form_control.get("name"), form_control.get("value")))



        # names.append(KeyModel(form_groups[1].find_all('input', class_= 'form-control' )[0].get("name"), form_groups[1].find_all('input', class_= 'form-control' )[0].get("value")))
        # names.append(KeyModel(form_groups[2].find_all('input', class_= 'form-control' )[0].get("name"), form_groups[2].find_all('input', class_= 'form-control' )[0].get("value")))

    token_field = site.find('input', {"name" : "_Token[fields]"}).get('value')
    token_unlocked = site.find('input', {"name" : "_Token[unlocked]"}).get('value')
    scripts = site.find_all('script')

    print(f"scripts: {scripts}")

    pattern = r"document\.cookie\s*=\s*'([^']+)'"
    match = re.search(pattern, scripts.__str__())
    if match:
        cookie_value = match.group(1)
        cookie_value = cookie_value.split('=')
        cookies.set(cookie_value[0], cookie_value[1].split(";")[0], path="/")

    name = ""
    for item in keysModel:
        name = f"{name}{item.name}={item.value if item.value != None else ''}&"


    print(f"COOKIES: {cookies.items()}" )
    print(f"redirectPostToken: {redirectPostToken}")
    print(f"csrfToken: {csrfToken}")
    print(f"_Token[fields]: {token_field}")
    print(f"_Token[unlocked]: {token_unlocked}")
    print(f"name: {name}")
    
    
   

    return cookies, csrfToken, redirectPostToken, name, token_field, token_unlocked



for i, row in df.iterrows():

    if(i == 1): exit()

    # cpf = row['CPF']
    # nascimento = row['Nascimento']
    # nascimento = nascimento.strftime("%d/%m/%Y")
    # habilitacao = row['1° Habilitacao']
    # habilitacao = habilitacao.strftime("%d/%m/%Y")

    cpf = "127.870.526-06"
    nascimento = "29/04/1996"
    habilitacao = "10/07/2017"

    print(f"{cpf} - {nascimento} - {habilitacao}")

    cookies, csrfToken, redirectPostToken, names, token_field, token_unlocked = get_initial()


    url_request = f"{base_url}exibir-pontuacao-cnh"

    # Mantendo o CPF com pontos e traço
    cpf = "127.870.526-06"
    
    # Construindo o payload de forma mais segura
    payload = {
        '_method': 'POST',
        '_csrfToken': csrfToken,
        '_redirectPostToken': redirectPostToken,
        'cpf': cpf,  # Mantendo o formato original do CPF
        'dataNascimento': nascimento,
        'dataPrimeiraHabilitacao': habilitacao,
        '_Token[fields]': token_field,
        '_Token[unlocked]': token_unlocked
    }
    
    # Adicionando os campos dinâmicos do names
    for item in names.split('&'):
        if item:
            key, value = item.split('=')
            payload[key] = value
                

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'pt-BR,pt;q=0.9',  # Removido en-US e en
        'Cache-Control': 'max-age=0',  # Alterado de no-cache para max-age=0
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://transito.mg.gov.br',
        'Referer': base_url,
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    try:
        print("\nDados da requisição:")
        print(f"URL: {url_request}")
        print(f"Payload: {payload}")
        print(f"Cookies: {cookies}")
        
        # Gerando o comando curl
        curl_command = 'curl -X POST '
        curl_command += f'"{url_request}" '
        
        # Adicionando headers
        for key, value in headers.items():
            curl_command += f'-H "{key}: {value}" '
        
        # Adicionando cookies
        cookie_string = '; '.join([f'{k}={v}' for k, v in cookies.items()])
        curl_command += f'-H "Cookie: {cookie_string}" '
        
        # Adicionando payload
        payload_string = '&'.join([f'{k}={v}' for k, v in payload.items()])
        curl_command += f'--data-urlencode "{payload_string}"'
        
        print("\nComando curl para teste:")
        print(curl_command)
        
        response = requests.request("POST", url_request, headers=headers, data=payload, cookies=cookies)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Text: {response.text[:500]}...")
        
        if response.status_code == 400:
            print("\nErro 400 - Bad Request. Possíveis causas:")
            print("1. Formato de dados inválido")
            print("2. Campos obrigatórios faltando")
            print("3. Formato de data incorreto")
            print("4. CPF inválido")
            
        if response.status_code == 500:
            print("\nErro interno do servidor. Possíveis causas:")
            print("1. Servidor sobrecarregado")
            print("2. Dados inválidos enviados")
            print("3. Problemas temporários no servidor")
            print("\nTentando novamente em 5 segundos...")
            time.sleep(5)
            response = requests.request("POST", url_request, headers=headers, data=payload, cookies=cookies)
            
        if response.status_code == 403:
            print("\nAcesso negado. Possíveis causas:")
            print("1. Cookies inválidos ou expirados")
            print("2. CSRF token inválido")
            print("3. Servidor bloqueando requisições automatizadas")
            
        site = BeautifulSoup(response.text, "html.parser")
        table = site.find_all('table', class_='table table-sm table-striped table-bordered')
        print(f"\nTabela encontrada: {len(table)}")
        print(table)
    except Exception as e:
        print(f"\nErro na requisição: {str(e)}")
        print(f"Payload enviado: {payload}")
        print(f"Cookies: {cookies}")



