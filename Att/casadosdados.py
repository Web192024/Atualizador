import sys
import os
import json
import pandas as pd
import subprocess
import requests
from PyQt5.QtWidgets import (
    QApplication, 
    QWidget, 
    QLabel, 
    QLineEdit, 
    QComboBox, 
    QCheckBox, 
    QVBoxLayout, 
    QHBoxLayout, 
    QPushButton, 
    QDateEdit, 
    QFormLayout, 
    QMessageBox)
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp, QDate
from io import StringIO


class ExtratorDadosTela(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):
        # Criando os widgets
        self.setWindowTitle('Extrator de Dados')
        self.setGeometry(100, 100, 600, 400)

        self.razao_social_label = QLabel('Razão Social ou Nome Fantasia:')
        self.razao_social_edit = QLineEdit()
        self.razao_social_edit.setPlaceholderText('Razão Social ou Fantasia')

        self.atividade_principal_label = QLabel('Atividade Principal (CNAE):')
        self.atividade_principal_combo = QComboBox()
        self.atividade_principal_combo.addItems([])
        self.popularAtividadePrincipalCombo()
        
        self.incluir_atividade_secundaria_checkbox = QCheckBox('Incluir Atividade Secundária')

        self.natureza_juridica_label = QLabel('Natureza Jurídica:')
        self.natureza_juridica_combo = QComboBox()
        self.natureza_juridica_combo.addItems([])
        self.naturezaJuridicaCombo()

        self.situacao_cadastral_label = QLabel('Situação Cadastral:')
        self.situacao_cadastral_combo = QComboBox()
        self.situacao_cadastral_combo.addItems(['','ATIVA', 'BAIXADA', 'INAPTA', 'SUSPENSA', 'NULA'])

        self.estado_label = QLabel('ESTADO (UF):')
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(['','Acre', 
                                    'Alagoas', 'Amapá', 
                                    'Amazonas', 'Bahia', 
                                    'Ceará', 'Distrito Federal', 
                                    'Espírito Santo', 'Goiás', 
                                    'Maranhão', 'Minas Gerais', 
                                    'Mato Grosso do Sul', 'Mato Grosso', 
                                    'Pará', 'Paraíba', 
                                    'Pernambuco', 'Piauí', 
                                    'Paraná', 'Rio de Janeiro', 
                                    'Rio Grande do Norte', 'Rondônia', 
                                    'Roraima', 'Rio Grande do Sul', 
                                    'Santa Catarina', 'Sergipe', 
                                    'São Paulo', 'Tocantins', 
                                    'Exterior'])
        self.estado_combo.currentIndexChanged.connect(self.estado_changed)

        self.municipio_label = QLabel('Município:')
        self.municipio_edit = QLineEdit()
        self.municipio_edit.setPlaceholderText('Digite o nome do município')
        self.municipio_edit.setEnabled(False)

        self.bairro_label = QLabel('Bairro:')
        self.bairro_edit = QLineEdit()
        self.bairro_edit.setPlaceholderText('Nome do bairro')

        self.cep_label = QLabel('CEP (Somente 8 dígitos):')
        self.cep_edit = QLineEdit()
        self.cep_edit.setPlaceholderText('Número de 8 dígitos')
        cep_validator = QRegExpValidator(QRegExp(r'\d{8}'), self)  # Aceita apenas 8 dígitos
        self.cep_edit.setValidator(cep_validator)

        self.ddd_label = QLabel('DDD:')
        self.ddd_edit = QLineEdit()
        self.ddd_edit.setPlaceholderText('Número de 2 dígitos')
        ddd_validator = QRegExpValidator(QRegExp(r'\d{2}'), self)  # Aceita apenas 8 dígitos
        self.ddd_edit.setValidator(ddd_validator)

        self.data_abertura_inicio_label = QLabel('Data de Abertura - A partir de:')
        self.data_abertura_inicio_edit = QDateEdit()
        self.data_abertura_inicio_edit.setDisplayFormat('dd/MM/yyyy')

        self.data_abertura_fim_label = QLabel('Data de Abertura - Até:')
        self.data_abertura_fim_edit = QDateEdit()
        self.data_abertura_fim_edit.setDisplayFormat('dd/MM/yyyy')
        self.data_abertura_fim_edit.setCalendarPopup(True)
        self.data_abertura_fim_edit.setDate(QDate.currentDate())

        self.capital_social_inicio_label = QLabel('Capital Social (A partir de):')
        self.capital_social_inicio_edit = QLineEdit()
        self.capital_social_inicio_edit.setPlaceholderText('Ex: 5000')
        self.capital_social_inicio_edit.setValidator(QDoubleValidator())

        self.capital_social_fim_label = QLabel('Capital Social (Até):')
        self.capital_social_fim_edit = QLineEdit()
        self.capital_social_fim_edit.setPlaceholderText('Ex: 10000')
        self.capital_social_fim_edit.setValidator(QDoubleValidator())
        
        self.somente_mei_checkbox = QCheckBox('Somente MEI')
        
        self.excluir_mei_checkbox = QCheckBox('Excluir MEI')
        
        self.com_contato_de_telefone_checkbox = QCheckBox('Com contato de telefone')
        
        self.somente_fixo_checkbox = QCheckBox('Somente fixo')
        
        self.somente_matriz_checkbox = QCheckBox('Somente matriz')
        
        self.somente_filial_checkbox = QCheckBox('Somente filial')
        
        self.somente_celular_checkbox = QCheckBox('Somente celular')
        
        self.com_email_checkbox = QCheckBox('Com e-mail')

        # Layout
        layout = QFormLayout()
        
        layout.addRow(self.razao_social_label, self.razao_social_edit)
        layout.addRow(self.atividade_principal_label, self.atividade_principal_combo)
        layout.addRow(self.incluir_atividade_secundaria_checkbox)
        layout.addRow(self.natureza_juridica_label, self.natureza_juridica_combo)
        layout.addRow(self.situacao_cadastral_label, self.situacao_cadastral_combo)
        layout.addRow(self.estado_label, self.estado_combo)
        layout.addRow(self.municipio_label, self.municipio_edit)
        layout.addRow(self.bairro_label, self.bairro_edit)
        layout.addRow(self.cep_label, self.cep_edit)
        layout.addRow(self.ddd_label, self.ddd_edit)
        layout.addRow(self.data_abertura_inicio_label, self.data_abertura_inicio_edit)
        layout.addRow(self.data_abertura_fim_label, self.data_abertura_fim_edit)
        layout.addRow(self.capital_social_inicio_label, self.capital_social_inicio_edit)
        layout.addRow(self.capital_social_fim_label, self.capital_social_fim_edit)
        
        layout.addRow(self.somente_mei_checkbox, self.excluir_mei_checkbox)
        layout.addRow(self.com_contato_de_telefone_checkbox, self.somente_fixo_checkbox)
        layout.addRow(self.somente_matriz_checkbox, self.somente_filial_checkbox)
        layout.addRow(self.somente_celular_checkbox, self.com_email_checkbox)

        # Botão de consulta
        consultar_button = QPushButton('Consultar')
        layout.addRow(consultar_button)

        self.setLayout(layout)

        # Conectar o botão a uma função
        consultar_button.clicked.connect(self.consultar_dados)

        # Mostrar a janela
        self.show()
     
        
    def resource_path(relative_path):
        """Obtenha o caminho absoluto para o recurso, funciona para desenvolvimento e para o PyInstaller."""
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(
            os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
    

    def naturezaJuridicaCombo(self):
        lista_natju = []  # Declare a variável antes do bloco try
        try:
            # URL do arquivo CSV
            url = "https://drive.google.com/uc?id=1cYtDjZfEohDQQl-gUgCnDClyuZNkVm5n&"
            # Obtenha o conteúdo do arquivo CSV
            response = requests.get(url)
            data = StringIO(response.text)
            # Tente ler o arquivo CSV normalmente
            dados_natju = pd.read_csv(data, encoding="latin", sep=";")
            # Se a leitura for bem-sucedida, combine as informações e preencha o QComboBox
            dados_natju['informacao_combinada'] = dados_natju['Código NATJU'].astype(str) + ' - ' + dados_natju['Denominaçăo NATJU']
            lista_natju = dados_natju['informacao_combinada'].tolist()
        except pd.errors.ParserError as e:
            # Imprima a exceção completa
            print(f"Erro ao ler o arquivo CSV. Exceção: {e}")


        # Agora a variável lista_natju está acessível mesmo que ocorra uma exceção
        self.lista_natju = [""] + lista_natju
        self.natureza_juridica_combo.addItems(self.lista_natju)


    def buscarInformacaoNatJu(self, texto):
        # Função chamada quando o texto no QLineEdit muda
        # Atualiza a lista de sugestões da QComboBox de acordo com o texto digitado
        lista_filtrada = [item for item in self.lista_natju if texto.lower() in item.lower()]
        self.natureza_juridica_combo.clear()
        self.natureza_juridica_combo.addItems([""] + lista_filtrada)
     

    def popularAtividadePrincipalCombo(self):
        lista_cnae = []  # Declare a variável antes do bloco try
        try:
            # URL do arquivo CSV
            url = "https://drive.google.com/uc?id=11E3G2AdxrL31nf6lX9iKdSOWoT8r4CHF"
            # Obtenha o conteúdo do arquivo CSV
            response = requests.get(url)
            data = StringIO(response.text)
            # Tente ler o arquivo CSV normalmente
            dados_cnae = pd.read_csv(data, encoding="latin", sep=";")
            # Se a leitura for bem-sucedida, combine as informações e preencha o QComboBox
            dados_cnae['informacao_combinada'] = dados_cnae['Código CNAE Fiscal'].astype(str) + ' - ' + dados_cnae['Denominação CNAE Fiscal']
            lista_cnae = dados_cnae['informacao_combinada'].tolist()
        except pd.errors.ParserError as e:
            # Imprima a exceção completa
            print(f"Erro ao ler o arquivo CSV. Exceção: {e}")
        
        # Agora a variável lista_cnae está acessível mesmo que ocorra uma exceção
        self.lista_cnae = [""] + lista_cnae
        self.atividade_principal_combo.addItems(self.lista_cnae)


    def buscarInformacao(self, texto):
        # Função chamada quando o texto no QLineEdit muda
        # Atualiza a lista de sugestões da QComboBox de acordo com o texto digitado
        lista_filtrada = [item for item in self.lista_cnae if texto.lower() in item.lower()]
        self.atividade_principal_combo.clear()
        self.atividade_principal_combo.addItems([""] + lista_filtrada)


    def consultar_dados(self):
        # Adicione aqui a lógica para processar os dados inseridos
        dados = {
            'razao_social': self.razao_social_edit.text(),
            'atividade_principal': self.atividade_principal_combo.currentText(),
            'incluir_atividade_secundaria': self.incluir_atividade_secundaria_checkbox.isChecked(),
            'natureza_juridica': self.natureza_juridica_combo.currentText(),
            'situacao_cadastral': self.situacao_cadastral_combo.currentText(),
            'estado': self.estado_combo.currentText(),
            'municipio': self.municipio_edit.text(),
            'bairro': self.bairro_edit.text(),
            'cep': self.cep_edit.text(),
            'ddd': self.ddd_edit.text(),
            'data_abertura_inicio': self.data_abertura_inicio_edit.date().toString('dd/MM/yyyy'),
            'data_abertura_fim': self.data_abertura_fim_edit.date().toString('dd/MM/yyyy'),
            'capital_social_inicio': self.capital_social_inicio_edit.text(),
            'capital_social_fim': self.capital_social_fim_edit.text(),
            'somente_mei': self.somente_mei_checkbox.isChecked(),
            'excluir_mei': self.excluir_mei_checkbox.isChecked(),
            'com_contato_de_telefone': self.com_contato_de_telefone_checkbox.isChecked(),
            'somente_fixo': self.somente_fixo_checkbox.isChecked(),
            'somente_matriz': self.somente_matriz_checkbox.isChecked(),
            'somente_filial': self.somente_filial_checkbox.isChecked(),
            'somente_celular': self.somente_celular_checkbox.isChecked(),
            'com_email': self.com_email_checkbox.isChecked(),
        }

        # Crie um nome de arquivo baseado
        nome_arquivo = f"dados_consulta.json"

        # Crie o arquivo JSON e escreva os dados nele
        with open(nome_arquivo, 'w', encoding='utf-8') as arquivo_json:
            json.dump(dados, arquivo_json, indent=4, ensure_ascii=False)

        # Use resource_path para obter o caminho absoluto do arquivo disp.py
        extract_path = self.resource_path("extract.py")

        # Adicionando verificação se o arquivo existe antes de executar
        if os.path.exists(extract_path):
            comando_disparador = f"python {extract_path}"
            
            try:
                # Executa o processo subprocesso
                subprocess.Popen(comando_disparador, shell=True)
            except Exception as e:
                QMessageBox.critical(
                    f"Erro ao executar o arquivo extract.py, não foi possível inciar o extrator")
        else:
            QMessageBox.information(
                "Arquivo extract.py não encontrado.")
           
    
    def estado_changed(self, index):
        # Método para ser chamado quando o estado é alterado
        if index > 0:  # Verifica se o estado selecionado não é o vazio
            self.municipio_edit.setEnabled(True)
        else:
            self.municipio_edit.setEnabled(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ExtratorDadosTela()
    sys.exit(app.exec_())