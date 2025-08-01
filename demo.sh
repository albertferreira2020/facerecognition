#!/bin/bash

echo "=== Demonstração da API modificada ==="
echo ""

echo "1. Estado inicial da pasta people/123213521/"
ls -la people/123213521/
echo ""

echo "2. Testando API com person_id inexistente..."
curl -X POST http://127.0.0.1:5001/verify \
  -H "Content-Type: application/json" \
  -d '{"person_id": "999", "image_base64": "invalid_base64"}' \
  2>/dev/null | python3 -m json.tool
echo ""

echo "3. Para testar com imagem real:"
echo "   - Adicione fotos na pasta people/123213521/"
echo "   - Use: python test_api.py 123213521 sua_foto.jpg"
echo ""

echo "4. Quando der MATCH, a foto será salva automaticamente em:"
echo "   people/123213521/match_[uuid].jpg"
echo ""

echo "Lembre-se: A pasta temp_uploads não é mais necessária!"
echo "As imagens de match são salvas diretamente na pasta da pessoa."
