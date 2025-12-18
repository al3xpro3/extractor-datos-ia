import streamlit as st
import pandas as pd
import google.generativeai as genai
from PyPDF2 import PdfReader
import io
from PIL import Image

# Configuración de la IA
genai.configure(api_key="AIzaSyD7by2grJUWEGZ-H_N1p3EMjVsceKKb7eY")
model = genai.GenerativeModel('gemini-1.5-flash')

# ⚡ CONFIGURACIÓN: Sin necesidad de login, acceso público directo
st.set_page_config(
    page_title="Extractor IA Pro", 
    layout="centered",
    initial_sidebar_state="collapsed"
)
st.title("🤖 Extractor de Datos Inteligente")
st.markdown("Sube un archivo y dime qué información necesitas extraer en un CSV.")

# --- LÓGICA DE PROCESAMIENTO ---
def extraer_texto(file):
    if file.type == "application/pdf":
        reader = PdfReader(file)
        texto = ""
        for page in reader.pages:
            texto += page.extract_text()
        return texto
    elif file.type == "text/plain":
        return file.read().decode("utf-8")
    else:
        return None

def procesar_imagen(file):
    """Procesa una imagen y extrae texto/datos usando Gemini"""
    image = Image.open(file)
    return image

def procesar_con_vision(file, instruccion, es_imagen=False):
    """Usa capacidades de visión de Gemini para analizar imágenes"""
    if es_imagen:
        image = procesar_imagen(file)
        prompt = f"""
        Analiza esta imagen y extrae la información solicitada: {instruccion}.
        RESPONDE ÚNICAMENTE CON EL CONTENIDO DEL CSV.
        Usa comas como delimitador. No incluyas explicaciones ni bloques de código markdown.
        """
        response = model.generate_content([prompt, image])
    else:
        texto_archivo = extraer_texto(file)
        prompt = f"""
        Analiza el siguiente texto y extrae la información solicitada: {instruccion}.
        RESPONDE ÚNICAMENTE CON EL CONTENIDO DEL CSV.
        Usa comas como delimitador. No incluyas explicaciones ni bloques de código markdown.
        
        Texto:
        {texto_archivo}
        """
        response = model.generate_content(prompt)
    
    return response.text.replace('```csv', '').replace('```', '').strip()

# --- INTERFAZ ---
st.markdown("### 📁 Tipos de archivo soportados:")
st.markdown("- 📄 PDFs (se extrae texto automáticamente)")
st.markdown("- 🖼️ Imágenes (JPG, PNG - perfecto para recibos y facturas)")
st.markdown("- 📝 Archivos de texto (TXT)")

archivo = st.file_uploader("Cargar archivo (PDF, Imagen o TXT)", type=["pdf", "txt", "jpg", "jpeg", "png"])
instruccion = st.text_area("¿Qué datos quieres extraer?", placeholder="Ej: Extrae la fecha, el nombre del cliente y el monto total.")

if archivo and instruccion:
    if st.button("Generar CSV"):
        with st.spinner("El bot está leyendo el archivo..."):
            # Detectar tipo de archivo
            es_imagen = archivo.type in ["image/jpeg", "image/png"]
            es_pdf = archivo.type == "application/pdf"
            
            try:
                if es_imagen or es_pdf:
                    resultado_csv = procesar_con_vision(archivo, instruccion, es_imagen=es_imagen)
                else:
                    texto_archivo = extraer_texto(archivo)
                    if texto_archivo:
                        resultado_csv = procesar_con_vision(archivo, instruccion, es_imagen=False)
                    else:
                        st.error("No se pudo leer el archivo.")
                        resultado_csv = None
                
                if resultado_csv:
                    st.success("¡Extracción completada!")
                    st.text_area("Vista previa del resultado:", resultado_csv, height=200)
                    
                    # Botón de descarga
                    st.download_button(
                        label="📥 Descargar archivo CSV",
                        data=resultado_csv,
                        file_name="extraccion_bot.csv",
                        mime="text/csv"
                    )
            except Exception as e:
                st.error(f"Error al procesar el archivo: {str(e)}")
