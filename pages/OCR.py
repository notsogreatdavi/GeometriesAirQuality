import cv2
import pytesseract
import streamlit as st
import json
import os
import easyocr
from PIL import Image
import numpy as np

# Configuração do Tesseract
pytesseract.pytesseract.tesseract_cmd = r'libs\Tesseract-OCR\tesseract.exe'

# Variáveis globais
pontos = []
rois = {}
zoom_level = 1.0
offset_x, offset_y = 0, 0
nomes_rois = ["nome"]
json_file = 'metricas.json'

def salvar_coordenadas_json():
    with open(json_file, 'w') as f:
        json.dump(rois, f, indent=4)
    st.success(f"Coordenadas salvas em {json_file}")

def carregar_coordenadas_json():
    global rois
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            try:
                rois = json.load(f)
            except json.JSONDecodeError:
                rois = {}

def aplicar_zoom_e_pan(imagem, zoom_level, offset_x, offset_y):
    """Aplica zoom e deslocamento na imagem."""
    altura, largura = imagem.shape[:2]
    nova_largura, nova_altura = int(largura * zoom_level), int(altura * zoom_level)
    imagem_redimensionada = cv2.resize(imagem, (nova_largura, nova_altura))
    
    x1 = max(offset_x, 0)
    y1 = max(offset_y, 0)
    x2 = min(x1 + largura, nova_largura)
    y2 = min(y1 + altura, nova_altura)
    
    imagem_visivel = imagem_redimensionada[y1:y2, x1:x2]
    return imagem_visivel

def capturar_rois(imagem, rois_para_editar):
    global pontos, rois, zoom_level, offset_x, offset_y
    zoom_level, offset_x, offset_y = 1.0, 0, 0

    st.write("### Captura de ROIs")
    st.write("Clique e arraste para selecionar as regiões de interesse (ROIs).")

    for nome_atual in rois_para_editar:
        st.write(f"Selecionando coordenadas para: {nome_atual}")
        pontos = []

        while True:
            imagem_visivel = aplicar_zoom_e_pan(imagem, zoom_level, offset_x, offset_y)
            st.image(imagem_visivel, channels="BGR", use_container_width=True, caption="Imagem com Zoom e Pan")

            if st.button(f"Confirmar ROI para {nome_atual}"):
                if len(pontos) == 2:
                    x1, y1 = pontos[0]
                    x2, y2 = pontos[1]
                    rois[nome_atual] = [x1, y1, x2, y2]
                    pontos.clear()
                    break
                else:
                    st.warning("Selecione dois pontos para definir o ROI.")

            if st.button("Cancelar"):
                break

    salvar_coordenadas_json()
    st.success("Novas coordenadas foram salvas com sucesso!")
    pos_edicao_opcoes(imagem)


def realizar_ocr(imagem, roi, nome_roi):
    """
    Realiza OCR na região de interesse (ROI).
    Usa EasyOCR para ROIs específicos e PyTesseract para o restante.
    """
    x1, y1, x2, y2 = roi
    roi_cortada = imagem[y1:y2, x1:x2]
    
    # Lista de ROIs que usarão EasyOCR
    rois_easyocr = ["acao", "quantidade", "data", "cbo", "cnes"]
    
    if nome_roi in rois_easyocr:
        reader = easyocr.Reader(['pt'])  # Configurar EasyOCR para português
        resultados = reader.readtext(roi_cortada, detail=0)
        texto = " ".join(resultados).strip()
    else:
        config = '--oem 3 --psm 7'
        texto = pytesseract.image_to_string(roi_cortada, lang='por', config=config).strip()
    
    return texto

def processar_rois(imagem):
    """
    Processa os ROIs usando o OCR adequado (EasyOCR ou PyTesseract).
    """
    dados_texto = {nome_roi: realizar_ocr(imagem, roi, nome_roi) for nome_roi, roi in rois.items()}
    st.write("### Dados Capturados")
    for nome_roi, texto in dados_texto.items():
        st.write(f"{nome_roi.capitalize()}: {texto}")
    salvar_coordenadas_json()

def pos_edicao_opcoes(imagem):
    """Oferece opções após a edição dos ROIs."""
    st.write("### Opções Após Edição")
    if st.button("Processar Dados OCR"):
        processar_rois(imagem)
    if st.button("Retornar ao Menu Inicial"):
        menu_inicial(imagem)

def menu_inicial(imagem):
    st.write("### Menu Inicial")
    if st.button("Usar ROIs existentes"):
        processar_rois(imagem)

# Interface do Streamlit
st.title("Extração de Dados de Imagens")

# Carregar coordenadas existentes
carregar_coordenadas_json()

# Upload da imagem
uploaded_file = st.file_uploader("Carregue uma imagem", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    imagem = np.array(Image.open(uploaded_file))
    st.image(imagem, channels="BGR", use_column_width=True, caption="Imagem Carregada")
    menu_inicial(imagem)