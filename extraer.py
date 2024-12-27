import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
from lxml import etree

class MangaTranslator:
    def __init__(self, url, language_code):
        self.url = url
        self.language_code = language_code
        self.images = []
        self.texts = []
        self.chapter_name = self.get_chapter_name(url)
        self.folder_name = f"chapter_{self.chapter_name}"
        
        # Configurar la ruta correcta de Tesseract
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
        
        # Verificar la instalación de Tesseract
        self.verify_tesseract()

    def verify_tesseract(self):
        try:
            languages = pytesseract.get_languages()
            print(f"Idiomas disponibles: {languages}")
            if self.language_code not in languages:
                raise ValueError(f"El idioma {self.language_code} no está disponible en Tesseract")
        except Exception as e:
            print(f"Error al verificar Tesseract: {e}")
            raise

    def get_chapter_name(self, url):
        # Extraer el número del capítulo de la URL
        return url.split("/")[-2].replace("chapter-", "")

    def download_images(self):
        if os.path.exists(self.folder_name) and os.listdir(self.folder_name):
            user_input = input(f"La carpeta '{self.folder_name}' ya existe y contiene imágenes. ¿Desea descargarlas de nuevo? (s/n): ")
            if user_input.lower() != 's':
                print("Usando imágenes existentes.")
                self.images = [os.path.join(self.folder_name, f) 
                             for f in os.listdir(self.folder_name) 
                             if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
                self.images.sort()  # Asegurar orden correcto
                return

        os.makedirs(self.folder_name, exist_ok=True)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        try:
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            img_tags = soup.find_all('img', id=lambda x: x and x.startswith('image-'))

            for idx, img in enumerate(img_tags, 1):
                img_url = img.get('data-src') or img.get('src')
                if img_url:
                    try:
                        img_response = requests.get(img_url, headers=headers)
                        img_response.raise_for_status()
                        
                        img_name = f"page_{idx:03d}.webp"
                        img_path = os.path.join(self.folder_name, img_name)
                        
                        with open(img_path, 'wb') as img_file:
                            img_file.write(img_response.content)
                        self.images.append(img_path)
                        print(f"Descargada: {img_name}")
                    except requests.RequestException as e:
                        print(f"Error al descargar imagen {img_url}: {e}")
        except requests.RequestException as e:
            print(f"Error al acceder a la URL: {e}")

    def extract_text_from_images(self):
        self.texts = []
        
        for img_path in self.images:
            try:
                with Image.open(img_path) as img:
                    print(f"\nProcesando: {os.path.basename(img_path)}")
                    print(f"Formato: {img.format}")
                    print(f"Tamaño: {img.size}")
                    print(f"Modo: {img.mode}")
                    
                    text = pytesseract.image_to_string(img, lang=self.language_code)
                    text = text.strip()
                    
                    if text:
                        self.texts.append((img_path, text))
                        print("\nTexto extraído:")
                        print("-" * 50)
                        print(text)
                        print("-" * 50)
                    else:
                        print("⚠️ No se detectó ningún texto en la imagen")
                        
            except Exception as e:
                print(f"Error al procesar {img_path}: {e}")

    def save_translations_to_tmx(self):
        # Crear el nombre del archivo TMX basado en el capítulo
        tmx_filename = f"chapter_{self.chapter_name}.tmx"
        
        # Verificar si el archivo ya existe
        if os.path.exists(tmx_filename):
            user_input = input(f"El archivo {tmx_filename} ya existe. ¿Desea reescribirlo? (s/n): ")
            if user_input.lower() != 's':
                print("Operación cancelada.")
                return
        
        tmx = etree.Element("tmx", version="1.4")
        header = etree.SubElement(
            tmx, "header",
            segtype="sentence",
            adminlang="en-us",
            srclang=self.language_code,
            datatype="plaintext"
        )
        
        # Añadir información del capítulo en el header
        note = etree.SubElement(header, "note")
        note.text = f"Manga Chapter: {self.chapter_name}"
        
        body = etree.SubElement(tmx, "body")

        for img_path, text in self.texts:
            if text.strip():
                tu = etree.SubElement(body, "tu")
                tuv = etree.SubElement(tu, "tuv", lang=self.language_code)
                seg = etree.SubElement(tuv, "seg")
                seg.text = text
                
                note = etree.SubElement(tu, "note")
                note.text = f"Imagen fuente: {os.path.basename(img_path)}"

        with open(tmx_filename, 'wb') as f:
            f.write(etree.tostring(
                tmx, 
                pretty_print=True, 
                xml_declaration=True, 
                encoding='UTF-8'
            ))
        print(f"\nTraducciones guardadas en: {tmx_filename}")

def main():
    url = input("Ingrese la URL del capítulo del manga: ")
    language_code = input("Ingrese el código del idioma (eng/jpn/chi_sim): ")
    
    try:
        translator = MangaTranslator(url, language_code)
        translator.download_images()
        translator.extract_text_from_images()
        translator.save_translations_to_tmx()
    except Exception as e:
        print(f"Error en la ejecución: {e}")

if __name__ == "__main__":
    main()