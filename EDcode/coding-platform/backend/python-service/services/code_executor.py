from subprocess import Popen, PIPE
import os
import tempfile

class CodeExecutor:
    def __init__(self):
        self.allowed_extensions = ['.py', '.cs']
        self.execution_environment = '/usr/bin/python3'  # Change this to the appropriate Python interpreter path

    def execute_code(self, code, language):
        if language == 'python':
            return self.execute_python_code(code)
        elif language == 'csharp':
            return self.execute_csharp_code(code)
        else:
            raise ValueError("Unsupported language")

    def execute_python_code(self, code):
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file.write(code.encode())
            temp_file_path = temp_file.name

        try:
            process = Popen([self.execution_environment, temp_file_path], stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            return stdout.decode(), stderr.decode()
        finally:
            os.remove(temp_file_path)

    def execute_csharp_code(self, code):
        with tempfile.NamedTemporaryFile(suffix='.cs', delete=False) as temp_file:
            temp_file.write(code.encode())
            temp_file_path = temp_file.name

        try:
            compile_process = Popen(['csc', temp_file_path], stdout=PIPE, stderr=PIPE)
            compile_stdout, compile_stderr = compile_process.communicate()

            if compile_process.returncode != 0:
                return compile_stdout.decode(), compile_stderr.decode()

            executable_path = temp_file_path.replace('.cs', '.exe')
            run_process = Popen([executable_path], stdout=PIPE, stderr=PIPE)
            stdout, stderr = run_process.communicate()
            return stdout.decode(), stderr.decode()
        finally:
            os.remove(temp_file_path)
            if os.path.exists(executable_path):
                os.remove(executable_path)