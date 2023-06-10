from PyPDF2 import PdfReader
import re
import os
from unidecode import unidecode
from docx import Document
from chardet.universaldetector import UniversalDetector
import spacy
from pdf2docx import Converter
import os


# Funções Auxiliares
# -------------------------------------------------------------------------------

def extrair_texto_do_pdf(arquivo_pdf):
    pdf_reader = PdfReader(arquivo_pdf)
    texto_completo = ""
    for page in pdf_reader.pages:
        texto_completo += page.extract_text()
    return texto_completo

def extrair_texto_do_doc(arquivo_doc):
    try: 
        doc = Document(arquivo_doc)
        text = " ".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except:
        raise Exception(f'Arquivo {arquivo_doc} com problema! ')

def detect_encoding(filename):
    detector = UniversalDetector()
    with open(filename, 'rb') as f:
        for line in f:
            detector.feed(line)
            if detector.done:
                break
    detector.close()
    return detector.result['encoding']

def read_txt_file(filename):
    encoding = detect_encoding(filename)
    with open(filename, 'r', encoding=encoding) as file:
        content = file.read()
    return content

def escreve_arquivo(texto, nome_arquivo, cabecalho):
    with open(nome_arquivo, 'a', encoding='utf-8', newline='\n') as arquivo: 
        arquivo.write('**** ' + cabecalho + '\n')
        arquivo.write(texto + '\n')

def nome_arquivo(texto):
    caracteres_especiais = '[^A-Za-z0-9 ]+'
    texto = texto.replace(' ', '_')
    texto = unidecode(texto.lower())
    texto = re.sub(caracteres_especiais, '', texto)
    return texto

# Processa cada arquivo PDF
def convert_pdf_docx(arquivo, arquivo_destino):
    cv = Converter(arquivo)
    # Processar todas as páginas
    cv.convert(arquivo_destino, start=0, end=None)

# def monta_cabecalho(nome_arquivo):
#     nome_arquivo_sem_extensao = os.path.splitext(nome_arquivo)[0]
#     items = nome_arquivo_sem_extensao.split('_')
#     cabecalho = []
#     if len(items) % 2 == 0:
#         for i in range(0, len(items), 2):
#             cabecalho.append(f'{items[i]}_{items[i+1]}')
#     else:
#         cabecalho = items
#     # Usa a função map para adicionar '*' antes de cada string na lista
#     cabecalho = map(lambda s: '*' + s, cabecalho)
#     resultado = " ".join(cabecalho)
#     return resultado.lower()

def monta_cabecalho(nome_arquivo):
    nome_arquivo_sem_extensao = os.path.splitext(nome_arquivo)[0]
    partes = nome_arquivo_sem_extensao.split('_')
    resultado = []
    indice_nm = partes.index('nm')
    indice_programa = partes.index('programa')
    indice_modalidade = partes.index('modalidade')
    indice_notafinal = partes.index('notafinal')

    resultado.append('nm_' + '_'.join(partes[indice_nm+1:indice_programa]).replace('_', '-'))
    resultado.append('programa_' + '_'.join(partes[indice_programa+1:indice_modalidade]).replace('_', '-'))
    resultado.append('modalidade_' + '_'.join(partes[indice_modalidade+1:indice_notafinal]).replace('_', '-'))
    resultado.append('notafinal_' + '_'.join(partes[indice_notafinal+1:]))
    resultado = " ".join(resultado)

    return resultado


    # if len(items) % 2 == 0:
    #     for i in range(0, len(items), 2):
    #         cabecalho.append(f'{items[i]}_{items[i+1]}')
    # else:
    #     cabecalho = items
    # # Usa a função map para adicionar '*' antes de cada string na lista
    # cabecalho = map(lambda s: '*' + s, cabecalho)
    # resultado = " ".join(cabecalho)
    # return resultado.lower()


# Funções de Processamento de Texto
# -------------------------------------------------------------------------------

# Remove quebras de linha e tabulação
def remove_quebras_linha_tabulacao(texto):
    texto = texto.replace('\t', ' ')
    texto = texto.replace('\n', ' ')
    return re.sub(' +', ' ', texto) # remove espaços múltiplos

def substitui_multiplas_expressoes(texto):
    pares_substituicao = [
        ('PPGA', 'programa de pós-graduação'),
        ('PPG', 'programa de pós-graduação'),
        ('FNDE', 'Fundo Nacional de Desenvolvimento da Educação'),
        ('Coordenação de Aperfeiçoamento de Pessoal de Nível Superior','CAPES'),
        (' o programa', ' programa de pós-graduação'),
        (' do programa', ' programa de pós-graduação'),
        (' no programa', ' programa de pós-graduação'),
        ('professor ', 'docente '),
        ('professores ', 'docentes '),
        (' dp ', ' docente permanente '),
        (' ndp ', ' núcleo docente permanente '),
        (' MB ', ' muito-bom '),
        (' B ', ' bom '),
        ('aluno ', 'discentes '),
        ('alunos ', 'discentes '),
    ]

    for expressao_antiga, expressao_nova in pares_substituicao:
        texto = texto.lower().replace(expressao_antiga.lower(), expressao_nova.lower())
    return texto

# Trata locuções substantivas para que as mesmas apareceçam juntas por underline
def trata_locusoes_substantivas(texto):
    # Aqui, você deve listar todas as locuções substantivas que deseja tratar.
    locucoes = ['programa de pós-graduação',
                'programas de pós-graduação',
                'UNIVERSIDADE FEDERAL', 
                'Ministério da Educação',
                'Avaliação Quadrienal 2017',
                'administração pública',
                'muito bom',
                'docente permanente',
                'linhas de pesquisa',
                'linha de pesquisa',
                'produção científica',
                'Comunidade científica',
                'Processo seletivo',
                'Estrutura curricular',
                'Docentes permanentes',
                'docente permanente',
                'Salas de aula',
                'Exames de qualificação',
                'Secretaria do Programa',
                'docentes colaboradores',
                'docentes visitantes',
                'docentes permantes',
                'Produção intelectual',
                'Produção técnica',
                'corpo docente',
                ]
    for locucao in locucoes:
        # Converte a locução para minúsculas e substitui espaços por sublinhados
        locucao_sublinhado = locucao.lower().replace(' ', '_')
        # Converte o texto e a locução para minúsculas antes de fazer a substituição
        texto = texto.lower().replace(locucao.lower(), locucao_sublinhado)
    return texto


# Substitui os hífens em palavras compostas por underline (_)
def substitui_hifen(texto):
    return texto.replace('-', '_')

# Remove os caracteres especificados
def remove_caracteres(texto):
    caracteres = ['"', "'", '-', '$', '%', '*', '...', '`']
    for caractere in caracteres:
        texto = texto.replace(caractere, '')
    return texto

# Remove expressões
def remove_expressoes(texto):
    expressoes = ['et al', 'cols', 'a', 'o', 'e', 'as', 'os', 
                  'no', 'nos', 'na', 'nas', 'do', 'dos', 'de', 'que', 'em']
    for expressao in expressoes:
        texto = re.sub(r'\b' + expressao + r'\b', '', texto, flags=re.IGNORECASE)
    return texto


# Capitaliza nomes próprios
# TODO usar o método melhorado e usar lista de palavras (nomes)
def capitalizar_nomes_proprios(texto):
    nlp = spacy.load('pt_core_news_lg')
    doc = nlp(texto)
    
    for entidade in doc.ents:
        if entidade.label_ == 'PER':
            texto = texto.replace(entidade.text, entidade.text.title())

    return texto

# Trocar "o programa", "o curso" por programa de pós graduação 

# Combina todas as funções
def processa_texto(texto):
    texto = remove_quebras_linha_tabulacao(texto)
    texto = substitui_multiplas_expressoes(texto)
    texto = trata_locusoes_substantivas(texto)
    texto = substitui_hifen(texto)
    texto = remove_caracteres(texto)
    texto = remove_expressoes(texto)
    return texto


# Programa 
# -------------------------------------------------------------------------------

pasta = './fichas'

# Lista todos os arquivos na pasta
arquivos = os.listdir(pasta)

# Filtra a lista de arquivos para incluir apenas os arquivos PDF
arquivos_pdf = [arquivo for arquivo in arquivos if arquivo.endswith('.pdf')]
arquivos_doc = [arquivo for arquivo in arquivos if arquivo.endswith('.doc') or arquivo.endswith('.docx')] 
arquivos_txt = [arquivo for arquivo in arquivos if arquivo.endswith('.txt')]


# Processa cada arquivo DOC
for arquivo_doc in arquivos_doc:
    # Cria o caminho completo para o arquivo
    caminho_completo = os.path.join(pasta, arquivo_doc)
    texto = extrair_texto_do_doc(caminho_completo)
    texto = processa_texto(texto)
    cabecalho = monta_cabecalho(arquivo_doc)
    escreve_arquivo(texto=texto, nome_arquivo='corpus_textual.txt', cabecalho=cabecalho)

# Processa cada arquivo TXT
for arquivo_txt in arquivos_txt:
    # Cria o caminho completo para o arquivo
    caminho_completo = os.path.join(pasta, arquivo_txt)
    texto = read_txt_file(caminho_completo)
    texto = processa_texto(texto)
    cabecalho = monta_cabecalho(arquivo_txt)
    escreve_arquivo(texto=texto, nome_arquivo='corpus_textual.txt', cabecalho=cabecalho)

# Processa cada arquivo PDF
for arquivo_pdf in arquivos_pdf:
    # Cria o caminho completo para o arquivo
    caminho_completo = os.path.join(pasta, arquivo_pdf)
    # Extrai o texto do arquivo PDF
    texto = extrair_texto_do_pdf(caminho_completo)
    texto = processa_texto(texto)
    cabecalho = monta_cabecalho(arquivo_pdf)
    escreve_arquivo(texto=texto, nome_arquivo='corpus_textual.txt', cabecalho=cabecalho)
