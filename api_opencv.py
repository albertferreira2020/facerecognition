from flask import Flask, request, jsonify
import os
from faceid.opencv_trainer import OpenCVFaceTrainer

app = Flask(__name__)
trainer = OpenCVFaceTrainer()

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        person_id = data.get('person_id')
        images_base64 = data.get('image_base64', [])
        
        if not person_id or not images_base64:
            return jsonify({'error': 'person_id and image_base64 are required'}), 400
        
        saved_images = trainer.save_base64_images(person_id, images_base64)
        
        if not saved_images:
            return jsonify({'error': 'Failed to save images'}), 500
        
        success = trainer.train_person(person_id)
        
        if not success:
            return jsonify({'error': 'Failed to train model'}), 500
        
        return jsonify({
            'success': True,
            'person_id': person_id,
            'images_saved': len(saved_images)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verify', methods=['POST'])
def verify():
    try:
        data = request.get_json()
        person_id = data.get('person_id')
        image_base64 = data.get('image_base64')
        
        if not person_id or not image_base64:
            return jsonify({'error': 'person_id and image_base64 are required'}), 400
        
        # Verificar com OpenCV Trainer
        is_match, similarity = trainer.verify_face(person_id, image_base64)
        
        if is_match:
            # ✅ MATCH CONFIRMADO - Salvar imagem e retreinar
            print(f"✅ Match confirmado para {person_id} - salvando imagem e retreinando...")
            
            # Salvar a nova imagem na pasta da pessoa
            saved_images = trainer.save_base64_images(person_id, [image_base64])
            
            if saved_images:
                print(f"📁 Imagem salva: {saved_images[0]}")
                
                # Retreinar o modelo com a nova imagem
                retrain_success = trainer.train_person(person_id)
                print(f"🎯 Retreinamento {'bem-sucedido' if retrain_success else 'falhou'}")
            else:
                print(f"⚠️ Falha ao salvar imagem para {person_id}")
                retrain_success = False
            
            # Calcular confiança como porcentagem
            confidence = max(0, (1 - similarity) * 100) if similarity <= 1 else max(0, 100 - (similarity * 0.01))
            
            return jsonify({
                'match': True,
                'similarity': float(similarity),
                'confidence': float(confidence),
                'person_id': person_id,
                'retrained': retrain_success,
                'images_saved': len(saved_images) if saved_images else 0,
                'verification_method': 'OpenCV LBPH'
            })
        else:
            # ❌ NO MATCH - Não salvar nem retreinar
            print(f"❌ No match para {person_id} - similaridade: {similarity}")
            
            confidence = max(0, (1 - similarity) * 100) if similarity <= 1 else max(0, 100 - (similarity * 0.01))
            
            return jsonify({
                'match': False,
                'similarity': float(similarity),
                'confidence': float(confidence),
                'person_id': person_id,
                'retrained': False,
                'verification_method': 'OpenCV LBPH'
            })
            
    except FileNotFoundError:
        return jsonify({'error': f'Person {person_id} not found. Please register first.'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('dataset', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=3002)
