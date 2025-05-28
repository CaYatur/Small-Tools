from flask import Blueprint, request, jsonify
import subprocess
import os

packages_bp = Blueprint('packages', __name__)

@packages_bp.route('/packages/install', methods=['POST'])
def install_package():
    package_name = request.json.get('package')
    if not package_name:
        return jsonify({'error': 'Package name is required'}), 400

    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
        return jsonify({'message': f'Package {package_name} installed successfully'}), 200
    except subprocess.CalledProcessError:
        return jsonify({'error': f'Failed to install package {package_name}'}), 500

@packages_bp.route('/packages/list', methods=['GET'])
def list_packages():
    try:
        installed_packages = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).decode('utf-8')
        packages = installed_packages.splitlines()
        return jsonify({'packages': packages}), 200
    except subprocess.CalledProcessError:
        return jsonify({'error': 'Failed to list packages'}), 500

@packages_bp.route('/packages/uninstall', methods=['POST'])
def uninstall_package():
    package_name = request.json.get('package')
    if not package_name:
        return jsonify({'error': 'Package name is required'}), 400

    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', '-y', package_name])
        return jsonify({'message': f'Package {package_name} uninstalled successfully'}), 200
    except subprocess.CalledProcessError:
        return jsonify({'error': f'Failed to uninstall package {package_name}'}), 500