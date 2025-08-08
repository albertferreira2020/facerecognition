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
        
        is_match, similarity = trainer.verify_face(person_id, image_base64)
        
        if is_match:
            trainer.save_base64_images(person_id, [image_base64])
            trainer.train_person(person_id)
            
            return jsonify({
                'match': True,
                'similarity': float(similarity),
                'person_id': person_id,
                'retrained': True
            })
        else:
            return jsonify({
                'match': False,
                'similarity': float(similarity),
                'person_id': person_id
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('dataset', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=3002)
