"""
Script para retreinar todos os modelos com MediaPipe

Este script retreina todos os modelos existentes usando MediaPipe
para aproveitar a maior precisão e detecção superior.
"""

import os
from faceid.mediapipe_trainer import MediaPipeFaceTrainer
from faceid.opencv_trainer import OpenCVFaceTrainer

def retrain_all_models():
    """Retreina todos os modelos usando MediaPipe"""
    
    print("🔄 RETREINAMENTO DE MODELOS")
    print("=" * 50)
    
    # Inicializar trainers
    mediapipe_trainer = MediaPipeFaceTrainer()
    opencv_trainer = OpenCVFaceTrainer()
    
    # Encontrar todas as pessoas no dataset
    dataset_path = "dataset"
    
    if not os.path.exists(dataset_path):
        print("❌ Dataset folder não encontrado!")
        return
    
    # Listar todas as pastas de pessoas
    person_folders = [f for f in os.listdir(dataset_path) 
                     if os.path.isdir(os.path.join(dataset_path, f))]
    
    print(f"📁 Encontradas {len(person_folders)} pessoas no dataset:")
    for person_id in person_folders:
        print(f"   • {person_id}")
    
    print("\n" + "="*50)
    
    # Retreinar cada pessoa
    for i, person_id in enumerate(person_folders, 1):
        print(f"\n🔄 RETREINANDO PESSOA {i}/{len(person_folders)}: {person_id}")
        print("-" * 40)
        
        # Contar imagens no dataset
        person_path = os.path.join(dataset_path, person_id)
        images = [f for f in os.listdir(person_path) 
                 if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        print(f"📸 Imagens disponíveis: {len(images)}")
        
        # Treinar com MediaPipe
        print("🚀 Treinando com MediaPipe...")
        mediapipe_success = mediapipe_trainer.train_person(person_id)
        
        # Treinar com OpenCV (para comparação)
        print("🔧 Treinando com OpenCV...")
        opencv_success = opencv_trainer.train_person(person_id)
        
        # Resultados
        print(f"✅ MediaPipe: {'Sucesso' if mediapipe_success else 'Falhou'}")
        print(f"🔧 OpenCV: {'Sucesso' if opencv_success else 'Falhou'}")
        
        if mediapipe_success and opencv_success:
            print("🎉 Ambos os modelos treinados com sucesso!")
        elif mediapipe_success:
            print("⚠️  Apenas MediaPipe foi bem-sucedido")
        elif opencv_success:
            print("⚠️  Apenas OpenCV foi bem-sucedido")
        else:
            print("❌ Ambos falharam - verificar dataset")
    
    print("\n" + "="*50)
    print("🏁 RETREINAMENTO CONCLUÍDO!")
    print("="*50)

def compare_detection_results():
    """Compara quantas faces cada sistema detecta"""
    
    print("\n📊 COMPARAÇÃO DE DETECÇÃO")
    print("=" * 50)
    
    dataset_path = "dataset"
    person_folders = [f for f in os.listdir(dataset_path) 
                     if os.path.isdir(os.path.join(dataset_path, f))]
    
    mediapipe_trainer = MediaPipeFaceTrainer()
    opencv_trainer = OpenCVFaceTrainer()
    
    total_images = 0
    mediapipe_detected = 0
    opencv_detected = 0
    
    for person_id in person_folders:
        person_path = os.path.join(dataset_path, person_id)
        images = [f for f in os.listdir(person_path) 
                 if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        print(f"\n👤 {person_id}:")
        
        for image_file in images:
            total_images += 1
            image_path = os.path.join(person_path, image_file)
            
            # Testar detecção com cada sistema
            import cv2
            image = cv2.imread(image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # MediaPipe
            mp_encoding = mediapipe_trainer.extract_face_encoding(image_rgb)
            if mp_encoding is not None:
                mediapipe_detected += 1
                mp_status = "✅"
            else:
                mp_status = "❌"
            
            # OpenCV
            cv_encoding = opencv_trainer.extract_face_encoding(image_rgb)
            if cv_encoding is not None:
                opencv_detected += 1
                cv_status = "✅"
            else:
                cv_status = "❌"
            
            print(f"   📷 {image_file}: MediaPipe {mp_status} | OpenCV {cv_status}")
    
    print(f"\n📈 RESULTADOS FINAIS:")
    print(f"   🖼️  Total de imagens: {total_images}")
    print(f"   🚀 MediaPipe detectou: {mediapipe_detected}/{total_images} ({mediapipe_detected/total_images*100:.1f}%)")
    print(f"   🔧 OpenCV detectou: {opencv_detected}/{total_images} ({opencv_detected/total_images*100:.1f}%)")
    
    improvement = mediapipe_detected - opencv_detected
    if improvement > 0:
        print(f"   📊 MediaPipe detectou {improvement} rostos a mais!")
    elif improvement < 0:
        print(f"   📊 OpenCV detectou {abs(improvement)} rostos a mais!")
    else:
        print(f"   📊 Ambos detectaram o mesmo número de rostos")

if __name__ == "__main__":
    print("🎯 ANÁLISE E RETREINAMENTO DE MODELOS")
    print("=" * 50)
    
    # Primeiro comparar detecção
    compare_detection_results()
    
    # Perguntar se quer retreinar
    print(f"\n❓ Deseja retreinar todos os modelos? (y/n): ", end="")
    choice = input().lower().strip()
    
    if choice in ['y', 'yes', 's', 'sim']:
        retrain_all_models()
    else:
        print("ℹ️  Retreinamento cancelado.")
        print("💡 Você pode retreinar individualmente usando:")
        print("   mediapipe_trainer.train_person('person_id')")
        print("   opencv_trainer.train_person('person_id')")
