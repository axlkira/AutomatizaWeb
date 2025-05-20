import os
import shutil

def organizar_imagenes(ruta_base="_1. Imagenes", max_por_carpeta=500):
    if not os.path.exists(ruta_base):
        print(f"La carpeta {ruta_base} no existe.")
        return

    imagenes = [f for f in os.listdir(ruta_base) if os.path.isfile(os.path.join(ruta_base, f))]

    if not imagenes:
        print("No se encontraron imágenes en la carpeta.")
        return

    num_subcarpeta = 1
    for i in range(0, len(imagenes), max_por_carpeta):
        carpeta_destino = os.path.join(ruta_base, str(num_subcarpeta))
        os.makedirs(carpeta_destino, exist_ok=True)

        for imagen in imagenes[i:i+max_por_carpeta]:
            shutil.move(os.path.join(ruta_base, imagen), os.path.join(carpeta_destino, imagen))

        print(f"{len(imagenes[i:i+max_por_carpeta])} imágenes movidas a {carpeta_destino}")
        num_subcarpeta += 1

if __name__ == "__main__":
    organizar_imagenes()
