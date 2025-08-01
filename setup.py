#!/usr/bin/env python3
"""
Script para configurar o ambiente de reconhecimento facial
"""

import os
import urllib.request
import bz2
import subprocess
import sys

def install_requirements():
    """Instala as dependências Python"""
    print("Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False
    return True

def download_dlib_models():
    """Baixa os modelos necessários do dlib"""
    print("Baixando modelos de reconhecimento facial...")
    
    models = [
        {
            "name": "shape_predictor_68_face_landmarks.dat",
            "url": "https://github.com/davisking/dlib-models/raw/master/shape_predictor_68_face_landmarks.dat.bz2"
        },
        {
            "name": "dlib_face_recognition_resnet_model_v1.dat",
            "url": "https://github.com/davisking/dlib-models/raw/master/dlib_face_recognition_resnet_model_v1.dat.bz2"
        }
    ]
    
    for model in models:
        model_path = model["name"]
        compressed_path = f"{model_path}.bz2"
        
        if os.path.exists(model_path):
            print(f"✅ {model_path} já existe")
            continue
            
        try:
            print(f"Baixando {model_path}...")
            urllib.request.urlretrieve(model["url"], compressed_path)
            
            print(f"Descomprimindo {model_path}...")
            with bz2.BZ2File(compressed_path, 'rb') as f_in:
                with open(model_path, 'wb') as f_out:
                    f_out.write(f_in.read())
            
            os.remove(compressed_path)
            print(f"✅ {model_path} baixado e descomprimido com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao baixar {model_path}: {e}")
            return False
    
    return True

def main():
    print("🚀 Configurando ambiente de reconhecimento facial...\n")
    
    # Instalar dependências
    if not install_requirements():
        print("❌ Falha na instalação das dependências")
        return
    
    print()
    
    # Baixar modelos
    if not download_dlib_models():
        print("❌ Falha no download dos modelos")
        return
    
    print("\n✅ Configuração concluída com sucesso!")
    print("Agora você pode executar: python app.py")

if __name__ == "__main__":
    main()
