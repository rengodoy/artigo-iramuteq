# from PyPDF2 import PdfReader

# def extrair_texto_por_pagina(arquivo_pdf):
#     pdf_reader = PdfReader(arquivo_pdf)
#     textos_por_pagina = []
#     for page in pdf_reader.pages:
#         textos_por_pagina.append(page.extract_text())
#     return textos_por_pagina

# textos = extrair_texto_por_pagina('meu_arquivo.pdf')

# # Imprimindo o texto de cada página
# for i, texto in enumerate(textos):
#     print(f"Texto da página {i+1}:")
#     print(texto)
#     print("\n---\n")



from PyPDF2 import PdfReader
import re
import os


def extrair_texto_do_pdf(arquivo_pdf):
    pdf_reader = PdfReader(arquivo_pdf)
    texto_completo = ""
    for page in pdf_reader.pages:
        texto_completo += page.extract_text()
    return texto_completo


# Substitui os hífens em palavras compostas por underline (_)
def substitui_hifen(texto):
    resultado = re.sub(r'(\w+)-(\w+)', r'\1_\2', texto)
    return resultado

# Substitui os espaços em locuções substantivas por underline (_)
def substitui_espaco(texto):
    # Aqui, você deve listar todas as locuções substantivas que deseja tratar.
    locucoes = ['dona de casa', 'segunda-feira', 'bem-me-quer']
    for locucao in locucoes:
        texto = texto.replace(locucao.replace(' ', '_'), locucao)
        texto = texto.replace(locucao.replace(' ', '_'), locucao)
    return texto

# Remove as expressões especificadas
def remove_expressoes(texto):
    expressoes = ['et', 'al.', 'cols.', 'a', 'o', 'e', 'as', 'os', 
                  'no', 'nos', 'na', 'nas', 'do', 'dos', 'de', 'que', 'em']
    palavras = texto.split()
    palavras_filtradas = [palavra for palavra in palavras if palavra.lower() not in expressoes]
    texto = ' '.join(palavras_filtradas)
    return texto

def remove_expressoes2(texto):
    expressoes = ['et al', 'cols', 'a', 'o', 'e', 'as', 'os', 
                  'no', 'nos', 'na', 'nas', 'do', 'dos', 'de', 'que', 'em']
    for expressao in expressoes:
        texto = re.sub(r'\b' + expressao + r'\b', '', texto, flags=re.IGNORECASE)
    return texto

# Remove os caracteres especificados
def remove_caracteres(texto):
    caracteres = ['"', "'", '-', '$', '%', '*']
    for caractere in caracteres:
        texto = texto.replace(caractere, '')
    return texto

# Remove quebras de linha
def remove_quebras_linha(texto):
    return texto.replace('\n', ' ')

# Combina todas as funções
def processa_texto(texto):
    texto = remove_quebras_linha(texto)
    texto = remove_caracteres(texto)
    texto = remove_expressoes(texto)
    texto = substitui_hifen(texto)
    texto = substitui_espaco(texto)
    return texto

def escreve_arquivo(texto, nome_arquivo):
    with open(nome_arquivo, 'w', encoding='utf-8', newline='\n') as arquivo:
        arquivo.write(texto)

pasta = './fichas'

# Lista todos os arquivos na pasta
arquivos = os.listdir(pasta)

# Filtra a lista de arquivos para incluir apenas os arquivos PDF
arquivos_pdf = [arquivo for arquivo in arquivos if arquivo.endswith('.pdf')]


# Processa cada arquivo PDF
for arquivo_pdf in arquivos_pdf:
    # Cria o caminho completo para o arquivo
    caminho_completo = os.path.join(pasta, arquivo_pdf)
    
    # Extrai o texto do arquivo PDF
    texto = extrair_texto_do_pdf(caminho_completo)

    resultado = re.search(r'instituição de ensino: (.*?)Programa', texto, re.IGNORECASE | re.DOTALL)
    if resultado:
        nome_instituicao = resultado.group(1).strip().replace('\n', ' ')
        resultado = re.search(r'(.*?) \(([^)]+)\)$', nome_instituicao)
        sigla_instituicao = resultado.group(2)
        nome_instituicao = resultado.group(1)
        print(f'nome: {nome_instituicao}')
        print(f'sigla: {sigla_instituicao}')
        print('*'*25)
        print(texto)
        print('*'*25)
    resultado = re.search(r'programa: (.*?)modalidade', texto, re.IGNORECASE | re.DOTALL)
    if resultado:
        programa = resultado.group(1).strip().replace('\n', ' ')
        # print(f'programa: {programa}')
    
    resultado = re.search(r'modalidade: (.*?)área de avaliação', texto, re.IGNORECASE | re.DOTALL)
    if resultado:
        modalidade = resultado.group(1).strip().replace('\n', ' ')
        # print(f'modalidade: {modalidade}')
