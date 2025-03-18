from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# Configuração do Chrome
chrome_options = Options()
# chrome_options.add_argument('--headless')  # Descomente para rodar sem interface gráfica
chrome_options.add_argument('--start-maximized')
chrome_options.add_argument('--disable-notifications')
chrome_options.add_argument('--disable-popup-blocking')

# Inicializar o driver
driver = webdriver.Chrome(options=chrome_options)

# URL do site

url = 'https://transito.mg.gov.br/infracoes/multa/consultar-pontuacao-cnh/'
namePlan = 'Pontuacao_cnh.xlsx'

def set_fields(df: pd.DataFrame, i : int, observacao : str = '-', placa : str  = '-', infracao: str  = '-', data_hora: str  = '-', local: str  = '-', pontos: str  = '-'):
    
    df.loc[i,'Observação'] = observacao
    df.loc[i, 'Placa'] = placa
    df.loc[i, 'Infração'] = infracao
    df.loc[i, 'Data/Hora'] = data_hora
    df.loc[i, 'Local'] = local
    df.loc[i, 'Pontos'] = pontos

try:

    df = pd.read_excel(namePlan)
   
    df = df.reset_index(drop=True)

    # Abrir o site
    driver.get(url)
    
    for i, row in df.iterrows():
        print(row['Observação'])
        if pd.notnull(row['Observação']): continue
        print(f"INDEX: {i}")
        

        cpf = row['CPF']
        nascimento = row['Nascimento']
        nascimento = nascimento.strftime("%d/%m/%Y")
        habilitacao = row['1° Habilitacao']
        habilitacao = habilitacao.strftime("%d/%m/%Y")

        # Dados de teste
        # cpf = "127.870.526-06"
        # nascimento = "29/04/1996"
        # habilitacao = "10/07/2017"
        
        # Aguardar os elementos estarem presentes
        wait = WebDriverWait(driver, 30)
        
        # Preencher CPF
        cpf_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="cpf"]')))
        cpf_input.clear()
        cpf_input.send_keys(cpf)
        
        # Preencher Data de Nascimento
        nascimento_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="datanascimento"]')))
        nascimento_input.clear()
        nascimento_input.send_keys(nascimento)
        
        # Preencher Data de Primeira Habilitação
        habilitacao_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="dataprimeirahabilitacao"]')))
        habilitacao_input.clear()
        habilitacao_input.send_keys(habilitacao)
        
        # Clicar no botão de consultar
        botao_consultar = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/form/button')))
        botao_consultar.click()
        
        # Aguardar a resposta carregar
        time.sleep(5)
        
        # Verificar se existe a mensagem de não pontuação
        try:
            mensagem_sem_pontuacao = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/div')))
            if "NAO CONSTA PONTUACAO PARA ESSE CONDUTOR" in mensagem_sem_pontuacao.text:
                print("\nNAO CONSTA PONTUACAO PARA ESSE CONDUTOR")
                set_fields(df, i, observacao='NAO CONSTA PONTUACAO PARA ESSE CONDUTOR')
                time.sleep(3)
                continue

            if "NUMERO DO CPF INEXISTENTE" in mensagem_sem_pontuacao.text:
                print("\nNUMERO DO CPF INEXISTENTE")
                set_fields(df, i, observacao='NUMERO DO CPF INEXISTENTE')
                time.sleep(3)
                continue

            if "DATA DE NASCIMENTO INVALIDA" in mensagem_sem_pontuacao.text:
                print("\nDATA DE NASCIMENTO INVALIDA")
                set_fields(df, i, observacao='DATA DE NASCIMENTO INVALIDA')
                time.sleep(3)
                continue

            if "DATA DA PRIMEIRA HABILITACAO INVALIDA" in mensagem_sem_pontuacao.text:
                print("\nDATA DA PRIMEIRA HABILITACAO INVALIDA")
                set_fields(df, i, observacao='DATA DA PRIMEIRA HABILITACAO INVALIDA')
                time.sleep(3)
                continue

            
                
        except:
            pass
        
        # Encontrar a tabela
        
        tabela = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/div[3]/div[1]/table')))

        # Listas para armazenar os dados
        placas = []
        infracoes = []
        datas_horas = []
        locais = []
        pontos = []
        
        # Encontrar todas as linhas da tabela (exceto o cabeçalho)
        linhas = tabela.find_elements(By.TAG_NAME, 'tr')[1:]  # Pula o cabeçalho
        
        # Extrair dados de cada linha
        for linha in linhas:
            colunas = linha.find_elements(By.TAG_NAME, 'td')
            if len(colunas) >= 5:  # Verifica se tem todas as colunas necessárias
                placas.append(colunas[0].text)
                infracoes.append(colunas[1].text)
                datas_horas.append(colunas[2].text)
                locais.append(colunas[3].text)
                pontos.append(colunas[4].text)
        
        # Imprimir os dados coletados
        print("\nDados coletados:")
        print("=" * 50)
        for j in range(len(placas)):  # Mudando i para j no loop
            print(f"Placa: {placas[j]}")
            print(f"Infração: {infracoes[j]}")
            print(f"Data/Hora: {datas_horas[j]}")
            print(f"Local: {locais[j]}")
            print(f"Pontos: {pontos[j]}")
            print("-" * 50)
        
        # Salvando os dados usando o índice correto do DataFrame
        set_fields(df, i, observacao="-", placa = ','.join(placas), infracao = ','.join(infracoes), data_hora= ','.join(datas_horas), local = ','.join(locais) , pontos=sum([int(item) for item in pontos]))
        
        print(f"\nSalvando dados para o índice {i} do DataFrame:")
        print(f"CPF: {cpf}")
        print(f"Placa: {placas[0]}")
        print(f"Infração: {infracoes[0]}")
        print(f"Data/Hora: {datas_horas[0]}")
        print(f"Local: {locais[0]}")
        print(f"Pontos: {pontos[0]}")

        # Aguardar um pouco antes de voltar
        time.sleep(2)
        
        # Clicar no botão Voltar
        # botao_voltar = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div[3]/div[1]/a')))
        # botao_voltar.click()
        driver.get(url)
        
        # Aguardar a página voltar ao estado inicial
        time.sleep(3)
        
    
    
except Exception as e:
    print(f"Ocorreu um erro: {str(e)}")
    
finally:
    # Fechar o navegador

    df.to_excel(namePlan, index=False)

    time.sleep(5)
    driver.quit() 