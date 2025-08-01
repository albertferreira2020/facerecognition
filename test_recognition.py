#!/usr/bin/env python3
"""
Script de teste para o sistema de reconhecimento facial
"""

import requests
import base64
import json
import os
import sys

def encode_image_to_base64(image_path):
    """Converte uma imagem para base64"""
    try:
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded_string}"
    except Exception as e:
        print(f"Erro ao codificar imagem {image_path}: {e}")
        return None

def test_face_recognition(person_id, test_image_path, server_url="http://localhost:5001"):
    """Testa o reconhecimento facial"""
    
    if not os.path.exists(test_image_path):
        print(f"❌ Imagem de teste não encontrada: {test_image_path}")
        return
    
    person_folder = os.path.join('people', person_id)
    if not os.path.exists(person_folder):
        print(f"❌ Pasta da pessoa não encontrada: {person_folder}")
        return
    
    # Contar imagens na pasta da pessoa
    images_count = len([f for f in os.listdir(person_folder) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))])
    
    print(f"🔍 Testando reconhecimento...")
    print(f"   Pessoa: {person_id}")
    print(f"   Imagens de referência: {images_count}")
    print(f"   Imagem de teste: {test_image_path}")
    
    # Codificar imagem de teste
    base64_image = encode_image_to_base64(test_image_path)
    if not base64_image:
        return
    
    # Preparar requisição
    payload = {
        "person_id": person_id,
        "image_base64": base64_image
    }
    
    try:
        # Fazer requisição
        response = requests.post(f"{server_url}/verify", 
                               json=payload, 
                               headers={'Content-Type': 'application/json'},
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Resultado:")
            print(f"   Match: {result.get('match', False)}")
            print(f"   Similaridade máxima: {result.get('max_similarity', 0):.4f}")
            print(f"   Similaridade média: {result.get('avg_similarity', 0):.4f}")
            print(f"   Distância mínima: {result.get('min_distance', 1):.4f}")
            print(f"   Comparações realizadas: {result.get('num_comparisons', 0)}")
            
            # Interpretação dos resultados
            max_sim = result.get('max_similarity', 0)
            min_dist = result.get('min_distance', 1)
            
            print(f"\n📊 Análise:")
            if max_sim > 0.8:
                print("   🟢 Similaridade excelente")
            elif max_sim > 0.6:
                print("   🟡 Similaridade boa")
            elif max_sim > 0.4:
                print("   🟠 Similaridade baixa")
            else:
                print("   🔴 Similaridade muito baixa")
                
            if min_dist < 0.4:
                print("   🟢 Distância excelente")
            elif min_dist < 0.6:
                print("   🟡 Distância boa")
            elif min_dist < 0.8:
                print("   🟠 Distância alta")
            else:
                print("   🔴 Distância muito alta")
        
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
            print(f"❌ Erro HTTP {response.status_code}")
            print(f"   {error_data.get('error', 'Erro desconhecido')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("   Certifique-se de que o servidor está rodando: python app.py")
    except requests.exceptions.Timeout:
        print("❌ Erro: Timeout na requisição")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def main():
    if len(sys.argv) != 3:
        print("Uso: python test_recognition.py <person_id> <image_path>")
        print("Exemplo: python test_recognition.py 123213521 test_image.jpg")
        return
    
    person_id = sys.argv[1]
    test_image_path = sys.argv[2]
    
    test_face_recognition(person_id, test_image_path)

if __name__ == "__main__":
    main()
