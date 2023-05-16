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
from unidecode import unidecode


def extrair_texto_do_pdf(arquivo_pdf):
    pdf_reader = PdfReader(arquivo_pdf)
    texto_completo = ""
    for page in pdf_reader.pages:
        texto_completo += page.extract_text()
    return texto_completo


# Substitui os hífens em palavras compostas por underline (_)
def substitui_hifen(texto):
    return texto.replace('-', '_')

def substitui_espaco(texto):
    # Aqui, você deve listar todas as locuções substantivas que deseja tratar.
    locucoes = ['Coordenação de Aperfeiçoamento de Pessoal de Nível Superior', 
                'UNIVERSIDADE FEDERAL', 
                'programa de pós-graduação', 
                'programa de pós-graduação em administração',
                'pós graduação',
                'Ministério da Educação',
                'Ministério de Planejamento, Orçamento e Gestão',
                'Secretaria da Presidência da República',
                'Fundo Nacional de Desenvolvimento da Educação',
                'Avaliação Quadrienal 2017',
                'administração pública'
                ]
    for locucao in locucoes:
        # Converte a locução para minúsculas e substitui espaços por sublinhados
        locucao_sublinhado = locucao.lower().replace(' ', '_')
        # Converte o texto e a locução para minúsculas antes de fazer a substituição
        texto = texto.lower().replace(locucao.lower(), locucao_sublinhado)
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
    texto = substitui_multiplas_expressoes(texto)
    texto = substitui_espaco(texto)
    texto = remove_quebras_linha(texto)
    texto = substitui_hifen(texto)
    texto = remove_caracteres(texto)
    texto = remove_expressoes(texto)
    return texto

def escreve_arquivo(texto, nome_arquivo, cabecalho):
    with open(nome_arquivo, 'a', encoding='utf-8', newline='\n') as arquivo: 
        arquivo.write('**** ' + cabecalho + '\n')
        arquivo.write(texto + '\n')

def get_valor_final(texto):
    # Busca pelo texto após "Parecer Final" e pega as próximas 3 linhas
    match = re.search(r'Parecer Final\n(.*)\n(.*)\n(.*)', texto, re.MULTILINE)
    if match:
        # Se o texto for encontrado, procura por um número nas 3 linhas
        for i in range(1, 4):
            numero = re.search(r'\d+', match.group(i))
            if numero:
                return numero.group()
    return 'colocar_nota_manual' 

def nome_arquivo(texto):
    caracteres_especiais = '[^A-Za-z0-9 ]+'
    texto = texto.replace(' ', '_')
    texto = unidecode(texto.lower())
    texto = re.sub(caracteres_especiais, '', texto)
    return texto

def substitui_multiplas_expressoes(texto):
    pares_substituicao = [
        ('PPGA'.lower(), 'programa_de_pós_graduação_em_administração'.lower()),
        ('PPG'.lower(), 'programa_de_pós_graduação'.lower()),
        ('FNDE'.lower(), 'Fundo_Nacional_de_Desenvolvimento_da_Educação'.lower()),
        ('Coordenação de Aperfeiçoamento de Pessoal de Nível Superior'.lower(),'CAPES'.lower())
    ]

    for expressao_antiga, expressao_nova in pares_substituicao:
        texto = texto.lower().replace(expressao_antiga, expressao_nova)
    return texto


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
        #print('*'*25)
        # if sigla_instituicao == 'FGV/SP':
        #    print(texto)
        # print(get_valor_final(texto))
        print('*'*25)
        texto = processa_texto(texto)
        cabecalho = "*" + processa_texto(sigla_instituicao.lower()) + ' *' + get_valor_final(texto)
        print((nome_arquivo(nome_instituicao)+'.txt'))
        escreve_arquivo(texto=texto, nome_arquivo='iramuteq.txt', cabecalho=cabecalho)


    # resultado = re.search(r'programa: (.*?)modalidade', texto, re.IGNORECASE | re.DOTALL)
    # if resultado:
    #     programa = resultado.group(1).strip().replace('\n', ' ')
    #     # print(f'programa: {programa}')
    
    # resultado = re.search(r'modalidade: (.*?)área de avaliação', texto, re.IGNORECASE | re.DOTALL)
    # if resultado:
    #     modalidade = resultado.group(1).strip().replace('\n', ' ')
    #     # print(f'modalidade: {modalidade}')