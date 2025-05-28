const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const { exec, spawn } = require('child_process');

const app = express();
const PORT = process.env.PORT || 3000;

// Store active Python processes for interactive input
const activeProcesses = new Map();

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.static(path.join(__dirname, 'public')));

// Create necessary directories
const createDirectories = () => {
    const dirs = [
        'temp',
        'temp/python',
        'outputs',
        'public'
    ];
    
    dirs.forEach(dir => {
        const dirPath = path.join(__dirname, dir);
        if (!fs.existsSync(dirPath)) {
            fs.mkdirSync(dirPath, { recursive: true });
            console.log(`📁 Created directory: ${dir}`);
        }
    });
};

createDirectories();

// Python code execution with interactive support
app.post('/api/execute/python', (req, res) => {
    const { code, packages, interactive } = req.body;
    
    if (!code) {
        return res.status(400).json({ error: 'Code is required' });
    }

    const filename = `python_${Date.now()}.py`;
    const filepath = path.join(__dirname, 'temp', 'python', filename);
    
    try {
        // Write code to file
        fs.writeFileSync(filepath, code);
        
        // Install packages if provided
        if (packages && packages.length > 0) {
            const installCmd = `python -m pip install ${packages.join(' ')}`;
            exec(installCmd, (error, stdout, stderr) => {
                if (error) {
                    console.warn('Package installation warning:', stderr);
                }
                if (interactive) {
                    executeInteractivePython(filepath, res);
                } else {
                    executePython(filepath, res);
                }
            });
        } else {
            if (interactive) {
                executeInteractivePython(filepath, res);
            } else {
                executePython(filepath, res);
            }
        }
    } catch (error) {
        res.status(500).json({ error: 'Failed to write file: ' + error.message });
    }
});

// Interactive Python execution
const executeInteractivePython = (filepath, res) => {
    const env = { 
        ...process.env, 
        PYTHONIOENCODING: 'utf-8',
        PYTHONUTF8: '1'
    };
    
    const childProcess = spawn('python', ['-u', filepath], { 
        env,
        stdio: ['pipe', 'pipe', 'pipe']
    });
    
    let output = '';
    let error = '';
    let isResponseSent = false;
    let isWaitingForInput = false;
    
    const processId = Date.now().toString();
    
    childProcess.stdout.on('data', (data) => {
        const chunk = data.toString('utf8');
        output += chunk;
        
        // Input bekleme kontrolü - daha kapsamlı
        if (chunk.includes('girin') || 
            chunk.includes('input') || 
            chunk.endsWith(': ') ||
            chunk.endsWith('? ') ||
            chunk.includes('Enter') ||
            chunk.includes('yazın')) {
            isWaitingForInput = true;
        }
    });

    childProcess.stderr.on('data', (data) => {
        error += data.toString('utf8');
    });

    childProcess.on('close', (code) => {
        if (!isResponseSent) {
            isResponseSent = true;
            activeProcesses.delete(processId);
            
            try {
                fs.unlinkSync(filepath);
            } catch (cleanupError) {
                console.warn('File cleanup warning:', cleanupError.message);
            }
            
            res.json({
                output: output,
                error: error,
                exitCode: code,
                waitingForInput: false
            });
        }
    });

    // Store process BEFORE checking for input
    activeProcesses.set(processId, {
        process: childProcess,
        output: output,
        error: error,
        isResponseSent: false,
        filepath: filepath
    });

    // Check for input after initial output
    setTimeout(() => {
        if (isWaitingForInput && !isResponseSent) {
            isResponseSent = true;
            
            // Update stored process data
            const processData = activeProcesses.get(processId);
            if (processData) {
                processData.output = output;
                processData.error = error;
            }
            
            console.log(`Interactive process ${processId} waiting for input`);
            console.log('Current output:', output);
            
            res.json({
                output: output,
                error: error,
                waitingForInput: true,
                processId: processId,
                prompt: 'Bir değer girin:'
            });
        } else if (!isResponseSent) {
            // No input needed, complete immediately
            isResponseSent = true;
            activeProcesses.delete(processId);
            
            try {
                fs.unlinkSync(filepath);
            } catch (cleanupError) {
                console.warn('File cleanup warning:', cleanupError.message);
            }
            
            res.json({
                output: output,
                error: error,
                exitCode: 0,
                waitingForInput: false
            });
        }
    }, 2000); // Daha uzun bekleme süresi

    // Timeout after 60 seconds for interactive programs
    setTimeout(() => {
        if (!isResponseSent) {
            isResponseSent = true;
            childProcess.kill('SIGKILL');
            activeProcesses.delete(processId);
            
            try {
                fs.unlinkSync(filepath);
            } catch (cleanupError) {
                console.warn('File cleanup warning:', cleanupError.message);
            }
            
            res.status(408).json({ error: 'Execution timeout (60 seconds)' });
        }
    }, 60000);
};

// Send input to interactive Python process
app.post('/api/input/python', (req, res) => {
    const { input, processId } = req.body;
    
    console.log(`Received input for process ${processId}: "${input}"`);
    console.log('Request body:', req.body);
    console.log('Active processes:', Array.from(activeProcesses.keys()));
    
    if (!processId) {
        console.log('No processId provided in request');
        return res.status(400).json({ error: 'Process ID is required' });
    }
    
    if (!activeProcesses.has(processId)) {
        console.log(`Process ${processId} not found in active processes`);
        console.log('Available processes:', Array.from(activeProcesses.keys()));
        return res.status(400).json({ error: 'Process not found or expired' });
    }
    
    const processData = activeProcesses.get(processId);
    const childProcess = processData.process;
    
    try {
        // Send input to process
        childProcess.stdin.write(input + '\n');
        console.log(`Successfully sent input to process ${processId}: "${input}"`);
        
        let output = '';
        let error = '';
        let responseTimer;
        let dataReceived = false;
        
        const dataHandler = (data) => {
            const chunk = data.toString('utf8');
            output += chunk;
            dataReceived = true;
            
            console.log(`Received output from process ${processId}:`, chunk);
            
            // Reset timer on new output
            clearTimeout(responseTimer);
            responseTimer = setTimeout(() => {
                childProcess.stdout.removeListener('data', dataHandler);
                childProcess.stderr.removeListener('data', errorHandler);
                
                // Check if still waiting for input
                const isWaitingForInput = chunk.includes('girin') || 
                                         chunk.includes('input') || 
                                         chunk.endsWith(': ') ||
                                         chunk.endsWith('? ') ||
                                         chunk.includes('Enter') ||
                                         chunk.includes('yazın');
                
                console.log(`Process ${processId} - waiting for input: ${isWaitingForInput}`);
                
                res.json({
                    output: output,
                    error: error,
                    waitingForInput: isWaitingForInput,
                    processId: isWaitingForInput ? processId : null
                });
                
                if (!isWaitingForInput) {
                    console.log(`Process ${processId} completed, cleaning up`);
                    activeProcesses.delete(processId);
                    
                    // Clean up file
                    if (processData.filepath) {
                        try {
                            fs.unlinkSync(processData.filepath);
                        } catch (cleanupError) {
                            console.warn('File cleanup warning:', cleanupError.message);
                        }
                    }
                }
            }, 1500);
        };
        
        const errorHandler = (data) => {
            const chunk = data.toString('utf8');
            error += chunk;
            console.log(`Received error from process ${processId}:`, chunk);
        };
        
        childProcess.stdout.on('data', dataHandler);
        childProcess.stderr.on('data', errorHandler);
        
        // Initial timeout - longer for slow responses
        responseTimer = setTimeout(() => {
            if (!dataReceived) {
                console.log(`Process ${processId} - no response, assuming completion`);
            }
            
            childProcess.stdout.removeListener('data', dataHandler);
            childProcess.stderr.removeListener('data', errorHandler);
            
            res.json({
                output: output || 'İşlem tamamlandı.',
                error: error,
                waitingForInput: false,
                processId: null
            });
            
            activeProcesses.delete(processId);
            
            // Clean up file
            if (processData.filepath) {
                try {
                    fs.unlinkSync(processData.filepath);
                } catch (cleanupError) {
                    console.warn('File cleanup warning:', cleanupError.message);
                }
            }
        }, 3000);
        
    } catch (error) {
        console.log(`Error sending input to process ${processId}:`, error.message);
        activeProcesses.delete(processId);
        res.status(500).json({ error: 'Failed to send input: ' + error.message });
    }
});

// Regular Python execution (non-interactive)
const executePython = (filepath, res) => {
    const env = { 
        ...process.env, 
        PYTHONIOENCODING: 'utf-8',
        PYTHONUTF8: '1'
    };
    
    const childProcess = spawn('python', ['-u', filepath], { env });
    let output = '';
    let error = '';
    let isResponseSent = false;
    
    childProcess.stdout.on('data', (data) => {
        output += data.toString('utf8');
    });

    childProcess.stderr.on('data', (data) => {
        error += data.toString('utf8');
    });

    childProcess.on('close', (code) => {
        if (!isResponseSent) {
            isResponseSent = true;
            
            try {
                fs.unlinkSync(filepath);
            } catch (cleanupError) {
                console.warn('File cleanup warning:', cleanupError.message);
            }
            
            res.json({
                output: output,
                error: error,
                exitCode: code
            });
        }
    });

    setTimeout(() => {
        if (!isResponseSent) {
            isResponseSent = true;
            childProcess.kill('SIGKILL');
            
            try {
                fs.unlinkSync(filepath);
            } catch (cleanupError) {
                console.warn('File cleanup warning:', cleanupError.message);
            }
            
            res.status(408).json({ error: 'Execution timeout (30 seconds)' });
        }
    }, 30000);
};

// Python EXE builder (unchanged)
app.post('/api/build/python', (req, res) => {
    const { code, filename, packages } = req.body;
    
    if (!code || !filename) {
        return res.status(400).json({ error: 'Code and filename are required' });
    }

    const checkPyInstaller = () => {
        return new Promise((resolve, reject) => {
            exec('python -m PyInstaller --version', (error, stdout, stderr) => {
                if (error) {
                    reject(new Error('PyInstaller not found'));
                } else {
                    resolve();
                }
            });
        });
    };

    const installPyInstaller = () => {
        return new Promise((resolve, reject) => {
            exec('python -m pip install pyinstaller', (error, stdout, stderr) => {
                if (error) {
                    console.warn('PyInstaller installation warning:', stderr);
                    reject(error);
                } else {
                    resolve();
                }
            });
        });
    };

    checkPyInstaller()
        .catch(() => {
            console.log('PyInstaller bulunamadı, yükleniyor...');
            return installPyInstaller();
        })
        .then(() => {
            const tempDir = path.join(__dirname, 'temp', 'python', `build_${Date.now()}`);
            const pyFile = path.join(tempDir, `${filename}.py`);
            const outputDir = path.join(__dirname, 'outputs');
            
            try {
                fs.mkdirSync(tempDir, { recursive: true });
                fs.writeFileSync(pyFile, code);
                
                let buildCmd = `python -m PyInstaller --onefile --clean --noconfirm --distpath="${outputDir}" "${pyFile}"`;
                
                if (packages && packages.length > 0) {
                    const installCmd = `python -m pip install ${packages.join(' ')}`;
                    exec(installCmd, (error) => {
                        if (error) console.warn('Package installation warning:', error);
                        buildExecutable(buildCmd, filename, tempDir, res);
                    });
                } else {
                    buildExecutable(buildCmd, filename, tempDir, res);
                }
            } catch (error) {
                res.status(500).json({ error: 'Build preparation failed: ' + error.message });
            }
        })
        .catch((error) => {
            res.status(500).json({ 
                error: 'PyInstaller kurulumu başarısız. Lütfen manuel olarak "python -m pip install pyinstaller" komutuyla yükleyin.' 
            });
        });
});

const buildExecutable = (buildCmd, filename, tempDir, res) => {
    console.log('Building executable with command:', buildCmd);
    
    exec(buildCmd, { cwd: tempDir }, (error, stdout, stderr) => {
        console.log('Build stdout:', stdout);
        console.log('Build stderr:', stderr);
        
        try {
            fs.rmSync(tempDir, { recursive: true, force: true });
        } catch (cleanupError) {
            console.warn('Temp cleanup warning:', cleanupError);
        }
        
        if (error) {
            return res.status(500).json({ error: 'Build failed: ' + stderr });
        }
        
        const exePath = path.join(__dirname, 'outputs', `${filename}.exe`);
        
        if (fs.existsSync(exePath)) {
            res.download(exePath, `${filename}.exe`, (err) => {
                if (!err) {
                    setTimeout(() => {
                        try {
                            fs.unlinkSync(exePath);
                        } catch (deleteError) {
                            console.warn('File delete warning:', deleteError);
                        }
                    }, 5000);
                }
            });
        } else {
            res.status(500).json({ error: 'Executable not found after build' });
        }
    });
};

// Serve frontend
app.get('*', (req, res) => {
    const indexPath = path.join(__dirname, 'public', 'index.html');
    res.sendFile(indexPath);
});

app.listen(PORT, () => {
    console.log(`🐍 CaYaCODE Python Platform running on http://localhost:${PORT}`);
    console.log('📁 Directories ready');
    console.log('✨ Python support with GUI detection: Ready');
});

module.exports = app;