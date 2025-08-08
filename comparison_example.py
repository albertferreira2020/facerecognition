"""
Exemplo de uso comparando OpenCV vs MediaPipe Face Recognition

Este exemplo mostra como usar ambas as implementações e suas diferenças.
"""

import base64
from faceid.opencv_trainer import OpenCVFaceTrainer
from faceid.mediapipe_trainer import MediaPipeFaceTrainer

def compare_face_recognition_systems():
    """Compara os dois sistemas de reconhecimento facial"""
    
    print("=" * 60)
    print("COMPARAÇÃO: OpenCV vs MediaPipe Face Recognition")
    print("=" * 60)
    
    # Inicializar ambos os sistemas
    opencv_trainer = OpenCVFaceTrainer()
    mediapipe_trainer = MediaPipeFaceTrainer()
    
    print("\n1. INICIALIZAÇÃO")
    print("-" * 30)
    print("✅ OpenCV: Haar Cascades + LBPH")
    print("✅ MediaPipe: Face Detection + Face Mesh")
    
    # Exemplo de treinamento
    person_id = "00000000000000001"
    
    print(f"\n2. TREINAMENTO DA PESSOA: {person_id}")
    print("-" * 30)
    
    # Treinar com OpenCV
    print("🔄 Treinando com OpenCV...")
    opencv_success = opencv_trainer.train_person(person_id)
    print(f"OpenCV Training: {'✅ Sucesso' if opencv_success else '❌ Falhou'}")
    
    # Treinar com MediaPipe  
    print("🔄 Treinando com MediaPipe...")
    mediapipe_success = mediapipe_trainer.train_person(person_id)
    print(f"MediaPipe Training: {'✅ Sucesso' if mediapipe_success else '❌ Falhou'}")
    
    print("\n3. CARACTERÍSTICAS DOS SISTEMAS")
    print("-" * 30)
    
    print("📊 OpenCV LBPH:")
    print("   • Detecção: Haar Cascades")
    print("   • Encoding: LBPH (Local Binary Pattern)")
    print("   • Threshold: ~12,000")
    print("   • Precisão: ~75-80%")
    print("   • Apple Silicon: ✅ Funciona")
    
    print("\n📊 MediaPipe:")
    print("   • Detecção: Deep Learning (BlazeFace)")
    print("   • Encoding: Face Landmarks (468 pontos)")
    print("   • Threshold: ~0.6")
    print("   • Precisão: ~95-98%")
    print("   • Apple Silicon: ✅ Nativo")
    
    print("\n4. VANTAGENS E DESVANTAGENS")
    print("-" * 30)
    
    print("🟢 OpenCV Vantagens:")
    print("   • Simples de implementar")
    print("   • Baixo uso de recursos")
    print("   • Funciona em hardware antigo")
    
    print("🔴 OpenCV Desvantagens:")
    print("   • Menor precisão")
    print("   • Sensível à iluminação")
    print("   • Problemas com ângulos")
    
    print("\n🟢 MediaPipe Vantagens:")
    print("   • Alta precisão")
    print("   • Robusto a variações")
    print("   • Otimizado para mobile")
    print("   • Nativo Apple Silicon")
    
    print("🔴 MediaPipe Desvantagens:")
    print("   • Maior uso de recursos")
    print("   • Dependência do Google")
    print("   • Mais complexo")
    
    return opencv_trainer, mediapipe_trainer

def test_verification_comparison(opencv_trainer, mediapipe_trainer, person_id, test_image_base64):
    """Testa verificação com ambos os sistemas"""
    
    print(f"\n5. TESTE DE VERIFICAÇÃO: {person_id}")
    print("-" * 30)
    
    # Testar OpenCV
    print("🔄 Verificando com OpenCV...")
    opencv_match, opencv_similarity = opencv_trainer.verify_face(person_id, test_image_base64)
    print(f"OpenCV: {'✅ MATCH' if opencv_match else '❌ NO MATCH'} (Similaridade: {opencv_similarity:.2%})")
    
    # Testar MediaPipe
    print("🔄 Verificando com MediaPipe...")
    mediapipe_match, mediapipe_similarity = mediapipe_trainer.verify_face(person_id, test_image_base64)
    print(f"MediaPipe: {'✅ MATCH' if mediapipe_match else '❌ NO MATCH'} (Similaridade: {mediapipe_similarity:.2%})")
    
    # Comparar resultados
    print(f"\n📈 COMPARAÇÃO DE RESULTADOS:")
    print(f"   • OpenCV: {opencv_similarity:.2%}")
    print(f"   • MediaPipe: {mediapipe_similarity:.2%}")
    
    if opencv_match != mediapipe_match:
        print("⚠️  DIVERGÊNCIA: Os sistemas discordam!")
        print("   • Recomenda-se usar MediaPipe como referência")
    else:
        print("✅ CONSENSO: Ambos os sistemas concordam")

def installation_guide():
    """Guia de instalação para Apple Silicon"""
    
    print("\n6. GUIA DE INSTALAÇÃO (Apple Silicon)")
    print("-" * 30)
    
    print("📦 Para OpenCV (já instalado):")
    print("   pip install opencv-contrib-python")
    
    print("\n📦 Para MediaPipe:")
    print("   pip install mediapipe")
    print("   # Ou se houver problemas:")
    print("   pip install --upgrade mediapipe")
    
    print("\n🚀 Verificar instalação:")
    print("   python -c 'import mediapipe as mp; print(mp.__version__)'")

def recommendations():
    """Recomendações de uso"""
    
    print("\n7. RECOMENDAÇÕES DE USO")
    print("-" * 30)
    
    print("🎯 Use OpenCV quando:")
    print("   • Hardware limitado")
    print("   • Prototipagem rápida")
    print("   • Ambiente controlado")
    
    print("\n🎯 Use MediaPipe quando:")
    print("   • Precisão é crucial")
    print("   • Ambiente variável")
    print("   • Produção/Apple Silicon")
    print("   • Múltiplos ângulos/iluminação")
    
    print("\n💡 Estratégia Híbrida:")
    print("   • Use MediaPipe como principal")
    print("   • OpenCV como fallback")
    print("   • Combine resultados para máxima confiabilidade")

if __name__ == "__main__":
    # Executar comparação
    opencv_trainer, mediapipe_trainer = compare_face_recognition_systems()
    
    # Guias adicionais
    installation_guide()
    recommendations()
    
    print("\n" + "=" * 60)
    print("CONCLUSÃO: MediaPipe é superior em precisão e")
    print("compatibilidade com Apple Silicon!")
    print("=" * 60)
