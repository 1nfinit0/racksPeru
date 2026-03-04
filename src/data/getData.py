import requests
import pandas as pd # type: ignore
from pathlib import Path
from io import StringIO
import json
from dotenv import load_dotenv # type: ignore
import os
import pyktok as pyk # type: ignore
import time
import mimetypes
from urllib.parse import urlparse


env_path = Path(__file__).parent / ".env.local"
pathBase = Path(os.getcwd())
load_dotenv(env_path)

CSV_URL = os.getenv("SPREADSHEET_LINK")
OUTPUT_PATH = Path("rawData.json")

def main():
    
    __doc__ = """
    Programa de control y manipulación de datos que serán publicados en la web.
    
        Proceso: 
            1. Considerando el documento rawData.json que se descarga al final de este script como actualización de la fuente de verdad a partir del spreadsheet de Google Sheets que servirá como archivo control de en lo que este punto será el proceso "anterior", almacenaremos el nuevo json en una variable temporal con el fin de comparar con su versión anterior.
            
            2. A partir de la comparación entre ambos JSONs, se generarán 3 nuevos JSONs:
                - productosNuevos.json: Contendrá solo los productos que son nuevos en la versión actual respecto a la anterior.
                - productosEliminados.json: Contendrá solo los productos que han sido eliminados en la versión actual respecto a la anterior.
                - productosModificados.json: Contendrá solo los productos que han sido modificados en la versión actual respecto a la anterior.
                
            3. Se realizarán los procesos de descarga de imágenes y videos asociados a los productos nuevos y modificados, almacenándolos en las carpetas correspondientes dentro del proyecto.
            
            4. Finalmente, se actualizará el archivo rawData.json con la nueva versión de los datos para futuras comparaciones.
    """
    
    
    try:
        # New data
        response = requests.get(CSV_URL)
        response.raise_for_status()
        print("Datos descargados exitosamente desde Google Sheets.")
        csv_content = response.content.decode("utf-8")

        df = pd.read_csv(
            StringIO(csv_content),
        )

        json_str = df.to_json(orient="records", indent=2, force_ascii=False)
        json_loaded = json.loads(json_str)
                
        # Old data
        with open(Path(__file__).parent / "rawData.json", "r", encoding="utf-8") as f:
            old_data_json = json.load(f)
            
        print("\nLas fuentes son iguales:",old_data_json == json_loaded)
    except Exception as e:
        print(f"Error durante el proceso: {e}")

    def productosNuevos(new_json , old_json):
        """
        Devuelve un JSON (lista de dicts) con solo los productos que son nuevos
        en la versión actual respecto a la anterior.
        
        Parámetros:
        - new_json: lista de diccionarios con la versión nueva de productos
        - old_json: lista de diccionarios con la versión anterior de productos
        
        Retorna:
        - lista de diccionarios con los productos nuevos
        """
        old_ids = {item["id"] for item in old_json}
        nuevos = [item for item in new_json if item["id"] not in old_ids]
        
        return nuevos
    

    def productosEliminados(new_json, old_json):
        """
        Devuelve un JSON (lista de dicts) con solo los productos que han sido
        eliminados en la versión actual respecto a la anterior.
        
        Parámetros:
        - new_json: lista de diccionarios con la versión nueva de productos
        - old_json: lista de diccionarios con la versión anterior de productos
        
        Retorna:
        - lista de diccionarios con los productos eliminados
        """
        new_ids = {item["id"] for item in new_json}
        eliminados = [item for item in old_json if item["id"] not in new_ids]
        
        return eliminados


    def productosModificados(new_json, old_json):
        """
        Devuelve un JSON (lista de dicts) con solo los productos que han sido
        modificados en la versión actual respecto a la anterior.
        
        Parámetros:
        - new_json: lista de diccionarios con la versión nueva de productos
        - old_json: lista de diccionarios con la versión anterior de productos
        
        Retorna:
        - lista de diccionarios con los productos modificados (versión nueva)
        """
        old_dict = {item["id"]: item for item in old_json}
        
        modificados = []
        
        for item in new_json:
            codigo = item["id"]
            if codigo in old_dict:
                if item != old_dict[codigo]:
                    modificados.append(item)
        
        return modificados
    
    
    
    cantidadPN =  len(productosNuevos(json_loaded, old_data_json))
    cantidadPE =  len(productosEliminados(json_loaded, old_data_json))
    cantidadPM =  len(productosModificados(json_loaded, old_data_json))
    
    print(f"\nProductos Nuevos: {cantidadPN}\n")
    print(f"Productos Eliminados: {cantidadPE}\n")
    print(f"Productos Modificados: {cantidadPM}\n")
    
    def makeDirForNewProduct(item):
        imgDir = pathBase / "public" / "media" / item['id'] / "images"
        videoDir = pathBase / "public" / "media" / item['id'] / "videos"
        imgDir.mkdir(parents=True, exist_ok=True)
        videoDir.mkdir(parents=True, exist_ok=True)
    
    def downloadVideosForProduct(item):
        try:
            tiktok_url_list = []

            tiktok_url_list.append(item['video1'])
            tiktok_url_list.append(item['video2'])
            tiktok_url_list.append(item['video3'])
            tiktok_url_list.append(item['video4'])

            tiktok_url_list = [url for url in tiktok_url_list if url]

            for entry in os.listdir("."): 
                if entry.endswith(".mp4"): 
                    os.remove(entry)

            print(f"Descargando videos para {item['id']}")

            pyk.save_tiktok_multi_urls(
                tiktok_url_list,
                True,
                'data.csv',
                2
            )

            time.sleep(60)  # Zzz    

            print(f"Videos descargados para {item['id']}")
            
        except Exception as e:
            print(f"Error procesando producto {item.get('id', 'ID desconocido')}: {e}")
        
    
    def downloadImagesForProduct(item):

        # --- limpiar solo archivos del directorio actual ---
        for entry in os.listdir("."):
            if os.path.isfile(entry):
                try:
                    os.remove(entry)
                except Exception as e:
                    print(f"No se pudo eliminar {entry}: {e}")

        image_url_list = [
            item.get('image1'),
            item.get('image2'),
            item.get('image3'),
            item.get('image4'),
        ]

        image_url_list = [url for url in image_url_list if url]

        print(f"Descargando imágenes para {item['id']}")

        VALID_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"}

        HEADERS = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120 Safari/537.36"
            ),
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            "Referer": "https://www.yanbal.com/"
        }

        session = requests.Session()
        session.headers.update(HEADERS)

        # --- descarga ---
        for i, url in enumerate(image_url_list, start=1):
            try:
                parsed = urlparse(url)
                referer = f"{parsed.scheme}://{parsed.netloc}/"

                headers = {
                    "User-Agent": session.headers["User-Agent"],
                    "Accept": session.headers["Accept"],
                    "Referer": referer
                }

                response = session.get(url, headers=headers, timeout=15)
                response.raise_for_status()

                parsed = urlparse(url)
                filename = os.path.basename(parsed.path)
                name, ext = os.path.splitext(filename)
                ext = ext.lower()

                mime_type = response.headers.get("Content-Type", "").split(";")[0]
                guessed_ext = mimetypes.guess_extension(mime_type)

                if ext not in VALID_IMAGE_EXTS:
                    ext = guessed_ext or ".bin"

                final_name = f"{i}{ext}"

                with open(final_name, "wb") as f:
                    f.write(response.content)

                print(f"\t✔ Imagen {i} descargada -> {final_name}")

            except Exception as e:
                print(f"\t✘ Error descargando imagen {i}: {e}")
                continue

        print(f"\tProceso terminado para {item['id']}\n")

        
    def removeDownloadedMedia(item):
        media_path = pathBase / "public" / "media" / item['id']
        if media_path.exists() and media_path.is_dir():
            for child in media_path.rglob('*'):
                if child.is_file():
                    child.unlink()
            for child in reversed(list(media_path.rglob('*'))):
                if child.is_dir():
                    child.rmdir()
            media_path.rmdir()
        print(f"Eliminado: {item['id']}")
    
    
    if cantidadPN > 0:
        for producto in productosNuevos(json_loaded, old_data_json):
            try:
                
                makeDirForNewProduct(producto)
                os.chdir(pathBase / f"public/media/{producto['id']}/videos")
                downloadVideosForProduct(producto)
                os.chdir(pathBase)
                os.chdir(pathBase / f"public/media/{producto['id']}/images")
                downloadImagesForProduct(producto)
                os.chdir(pathBase)
        
            except Exception as e:
                print(f"Error procesando producto {producto.get('id', 'ID desconocido')}: {e}")
                os.chdir(pathBase) if 'pathBase' in locals() else None
                continue 
            
    if cantidadPE > 0:
        for producto in productosEliminados(json_loaded, old_data_json):
            try:
                removeDownloadedMedia(producto)
            except Exception as e:
                print(f"Error eliminando medios para producto {producto.get('id', 'ID desconocido')}: {e}")
                continue
    
    if cantidadPM > 0:
        
        campos_ignorados = {"version","modelo","capacidad","precio", "precioAntes", "descripcion","CPU","bateria","pantalla","camaraFoto","camaraVideo","estado","publicar"}
        old_map = {p["id"]: p for p in old_data_json}
        
        for producto in productosModificados(json_loaded, old_data_json):
            try:
                old_producto = old_map[producto["id"]]

                campos_modificados = {
                    k for k in producto
                    if producto.get(k) != old_producto.get(k)
                }

                if campos_modificados.issubset(campos_ignorados):
                    print(f"Producto {producto['id']} modificado pero sin cambios relevantes, se omite.")
                    continue

                # -------- cambios relevantes --------
                removeDownloadedMedia(producto)
                makeDirForNewProduct(producto)

                os.chdir(pathBase / f"public/media/{producto['id']}/videos")
                downloadVideosForProduct(producto)

                os.chdir(pathBase)
                os.chdir(pathBase / f"public/media/{producto['id']}/images")
                downloadImagesForProduct(producto)

                os.chdir(pathBase)
        
            except Exception as e:
                print(f"Error procesando producto {producto.get('id', 'ID desconocido')}: {e}")
                os.chdir(pathBase) if 'pathBase' in locals() else None
                continue
    
    os.chdir(pathBase / "src/data")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(json_loaded, f, ensure_ascii=False, indent=2)
    os.chdir(pathBase)
    print(f"Actualizado: {OUTPUT_PATH}")
    
if __name__ == "__main__":
    main()


# Los slugs son el id XD