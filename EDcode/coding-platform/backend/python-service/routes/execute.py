from flask import Blueprint, request, jsonify
from services.code_executor import execute_code

execute_bp = Blueprint('execute', __name__)

@execute_bp.route('/execute', methods=['POST'])
def execute():
    data = request.get_json()
    code = data.get('code')
    language = data.get('language')
    
    if not code or not language:
        return jsonify({'error': 'Code and language are required'}), 400
    
    output, error = execute_code(code, language)
    
    return jsonify({
        'output': output,
        'error': error
    })