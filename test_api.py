import requests
import base64
import sys
import os

def test_api_with_person_id():
    """Teste da nova API com person_id"""
    
    base_url = "http://localhost:5001"
    
    print("🎯 === Teste Face Recognition API v2.0 ===")
    print("   (Com person_id específico)")
    print("")
    
    # 1. Testar endpoint principal
    print("1. Testando endpoint principal...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Versão: {data.get('version', 'N/A')}")
        print(f"Endpoints: {list(data.get('endpoints', {}).keys())}")
        print()
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("Certifique-se de que a API está rodando: python app.py\n")
        return
    
    # 2. Listar pessoas disponíveis
    print("2. Listando pessoas disponíveis...")
    try:
        response = requests.get(f"{base_url}/list_people")
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Pessoas encontradas: {data.get('total', 0)}")
        
        people = data.get('people', [])
        if people:
            for person in people:
                print(f"  📁 {person['person_id']}: {person['image_count']} imagens")
        else:
            print("  ⚠️  Nenhuma pessoa encontrada na pasta 'people/'")
        print()
    except Exception as e:
        print(f"❌ Erro: {e}\n")
    
    # 3. Teste com person_id e imagem
    if len(sys.argv) >= 3:
        person_id = sys.argv[1]
        image_path = sys.argv[2]
        
        print(f"3. Testando verificação: pessoa={person_id}, imagem={image_path}")
        
        # Método 1: Form data (arquivo)
        print("   📤 Método 1: Upload de arquivo...")
        try:
            with open(image_path, 'rb') as f:
                response = requests.post(
                    f"{base_url}/verify",
                    data={'person_id': person_id},
                    files={'image': f}
                )
            
            data = response.json()
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Person ID: {data['person_id']}")
                print(f"   ✅ Match: {data['match']}")
                print(f"   📊 Resultado: {data['result']}")
                print(f"   📏 Similaridade média: {data['avg_similarity']}")
                print(f"   📏 Similaridade máxima: {data['max_similarity']}")
                print(f"   🎯 Threshold: {data['threshold']}")
                print(f"   📸 Imagens de referência: {data['total_reference_images']}")
            else:
                print(f"   ❌ Erro: {data.get('error', 'Erro desconhecido')}")
            
        except FileNotFoundError:
            print(f"   ❌ Arquivo {image_path} não encontrado")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        print()
        
        # Método 2: JSON com base64
        print("   📤 Método 2: JSON com base64...")
        try:
            # Converter imagem para base64
            with open(image_path, 'rb') as f:
                image_data = f.read()
                base64_string = base64.b64encode(image_data).decode('utf-8')
            
            # Enviar JSON
            response = requests.post(
                f"{base_url}/verify",
                json={
                    'person_id': person_id,
                    'image_base64': base64_string
                },
                headers={'Content-Type': 'application/json'}
            )
            
            data = response.json()
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Person ID: {data['person_id']}")
                print(f"   ✅ Match: {data['match']}")
                print(f"   📊 Resultado: {data['result']}")
                print(f"   📏 Similaridade média: {data['avg_similarity']}")
                print(f"   📏 Similaridade máxima: {data['max_similarity']}")
                print(f"   🎯 Threshold: {data['threshold']}")
                print(f"   📸 Imagens de referência: {data['total_reference_images']}")
            else:
                print(f"   ❌ Erro: {data.get('error', 'Erro desconhecido')}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    else:
        print("3. Para testar verificação, execute:")
        print("   python test_api_v2.py <person_id> <caminho_para_imagem>")
        print("   Exemplo: python test_api_v2.py 123213521 foto_teste.jpg")
        print("")
        print("💡 Exemplos de uso:")
        print("   🔸 Pessoa 123213521: python test_api_v2.py 123213521 foto1.jpg")
        print("   🔸 Pessoa xxxxx: python test_api_v2.py xxxxx foto2.jpg")
        print("")
        print("📁 Estrutura necessária:")
        print("   people/")
        print("   ├── 123213521/")
        print("   │   ├── ref1.jpg")
        print("   │   └── ref2.jpg")
        print("   └── xxxxx/")
        print("       ├── ref1.jpg")
        print("       └── ref2.jpg")

if __name__ == "__main__":
    test_api_with_person_id()
