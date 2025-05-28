def validate_code_input(code):
    if not isinstance(code, str):
        raise ValueError("Code must be a string.")
    if len(code.strip()) == 0:
        raise ValueError("Code cannot be empty.")
    # Additional validation rules can be added here

def validate_package_name(package_name):
    if not isinstance(package_name, str):
        raise ValueError("Package name must be a string.")
    if len(package_name.strip()) == 0:
        raise ValueError("Package name cannot be empty.")
    # Additional validation rules can be added here

def validate_execution_request(request):
    if not isinstance(request, dict):
        raise ValueError("Request must be a dictionary.")
    if 'code' not in request or 'packages' not in request:
        raise ValueError("Request must contain 'code' and 'packages' keys.")
    validate_code_input(request['code'])
    for package in request['packages']:
        validate_package_name(package)