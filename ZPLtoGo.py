import requests
import os
import sys
import zipfile

def convert_zpl_txt_to_pdf(input_path, output_path):
    try:
        # Lê o conteúdo do arquivo .txt
        with open(input_path, 'r') as file:
            zpl_content = file.read()
        
        # Define a URL para a conversão via API Labelary
        url = 'http://api.labelary.com/v1/printers/8dpmm/labels/4x6/'
        
        # Configura os headers
        headers = {'Accept': 'application/pdf'}
        
        # Envia a requisição para a API
        response = requests.post(url, headers=headers, data=zpl_content.encode('utf-8'), stream=True)
        
        if response.status_code == 200:
            # Verifica o tamanho do arquivo PDF
            if len(response.content) < 1024:  # por exemplo, 1KB
                print("O arquivo PDF gerado é muito pequeno. Verifique o conteúdo ZPL.")
                with open('debug_response.pdf', 'wb') as debug_file:
                    debug_file.write(response.content)
                return
            
            # Salva o arquivo PDF
            with open(output_path, 'wb') as out_file:
                out_file.write(response.content)
            print(f'PDF salvo em {output_path}')
        else:
            print('Erro: ' + response.text)
            print('Código de status HTTP:', response.status_code)
            with open('error_log.txt', 'a') as error_log:  # Append para registrar múltiplos erros
                error_log.write(f'Erro ao processar {input_path}: {response.text}\n')
    
    except Exception as e:
        print(f'Erro ao processar {input_path}: {e}')
        with open('error_log.txt', 'a') as error_log:
            error_log.write(f'Erro ao processar {input_path}: {str(e)}\n')

# Obtém o diretório onde o executável está localizado
if getattr(sys, 'frozen', False):
    # Se o script está sendo executado como um executável
    current_directory = os.path.dirname(sys.executable)
else:
    # Se o script está sendo executado diretamente
    current_directory = os.path.dirname(os.path.abspath(__file__))

# Caminhos para os arquivos
input_folder = current_directory  # Usa o diretório atual
output_folder = current_directory  # Usa o diretório atual

# Procura por arquivos .zip no diretório atual
for filename in os.listdir(input_folder):
    if filename.endswith('.zip'):
        zip_path = os.path.join(input_folder, filename)
        
        # Extrai os arquivos .txt do arquivo .zip
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            for txt_filename in zip_file.namelist():
                if txt_filename.endswith('.txt'):
                    txt_path = os.path.join(input_folder, txt_filename)
                    with zip_file.open(txt_filename) as txt_file:
                        with open(txt_path, 'wb') as extracted_file:
                            extracted_file.write(txt_file.read())
                    
                    pdf_filename = os.path.splitext(txt_filename)[0] + '.pdf'
                    pdf_path = os.path.join(output_folder, pdf_filename)
                    convert_zpl_txt_to_pdf(txt_path, pdf_path)
                    
                    # Exclui o arquivo .txt extraído
                    os.remove(txt_path)
