import os
import sys
from PIL import Image
import pytesseract

def test_tesseract_installation():
    # Actualizar a la ruta correcta de instalación
    tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    # Actualizar la ruta del tessdata
    tessdata_dir = r'C:\Program Files\Tesseract-OCR\tessdata'
    os.environ['TESSDATA_PREFIX'] = tessdata_dir
    
    # Verificar instalación
    if not os.path.exists(tesseract_cmd):
        print(f"ERROR: No se encuentra Tesseract en la ruta: {tesseract_cmd}")
        print("Por favor, verifica que Tesseract está instalado correctamente")
        return False
        
    if not os.path.exists(tessdata_dir):
        print(f"ERROR: No se encuentra el directorio tessdata en: {tessdata_dir}")
        return False
        
    # Verificar idiomas disponibles
    try:
        available_languages = pytesseract.get_languages()
        print("Idiomas disponibles:", available_languages)
    except Exception as e:
        print("ERROR al obtener idiomas:", str(e))
        return False
    
    return True

def test_image_extraction(image_path):
    try:
        with Image.open(image_path) as img:
            print(f"\nInformación de la imagen:")
            print(f"Formato: {img.format}")
            print(f"Tamaño: {img.size}")
            print(f"Modo: {img.mode}")
            
            print("\nIntentando extraer texto...")
            text = pytesseract.image_to_string(img, lang='eng')
            print("\nTexto extraído:")
            print("-" * 50)
            print(text)
            print("-" * 50)
            
            if not text.strip():
                print("⚠️ No se detectó ningún texto en la imagen")
            
            return True
    except Exception as e:
        print(f"ERROR al procesar la imagen: {str(e)}")
        return False

def main():
    print("=== Verificando instalación de Tesseract ===")
    if not test_tesseract_installation():
        print("\n❌ La verificación de Tesseract falló")
        return
    
    print("\n✅ Tesseract está instalado correctamente")
    
    # Probar con una imagen
    print("\n=== Probando extracción de texto ===")
    folder_name = "chapter-445"  # Nombre de tu carpeta
    
    if not os.path.exists(folder_name):
        print(f"ERROR: No se encuentra la carpeta {folder_name}")
        return
        
    images = [f for f in os.listdir(folder_name) if f.endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    if not images:
        print(f"ERROR: No se encontraron imágenes en {folder_name}")
        return
        
    test_image = os.path.join(folder_name, images[0])
    if not test_image_extraction(test_image):
        print("\n❌ La prueba de extracción falló")
    else:
        print("\n✅ Prueba de extracción completada")

if __name__ == "__main__":
    main()