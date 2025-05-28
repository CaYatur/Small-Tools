let editor;
let currentLanguage = 'python';
let packages = [];
let consoleWindow = null;
let currentProcessId = null;

// Initialize CodeMirror editor
document.addEventListener('DOMContentLoaded', function() {
    editor = CodeMirror.fromTextArea(document.getElementById('codeEditor'), {
        lineNumbers: true,
        mode: 'python',
        theme: 'monokai',
        indentUnit: 4,
        lineWrapping: true,
        autoCloseBrackets: true,
        matchBrackets: true
    });

    // Set default Python code with input example
    editor.setValue(`# CaYaCODE Platform - Python Örnek Kodu
# -*- coding: utf-8 -*-
import sys
import os

# Unicode desteği için
if sys.platform == "win32":
    os.system("chcp 65001 >nul")

print("Merhaba CaYaCODE Platform!")
print("Bu platforma hoş geldiniz!")

# Kullanıcıdan input alma örneği
name = input("Adınızı girin: ")
age = input("Yaşınızı girin: ")

print(f"Merhaba {name}! {age} yaşındasınız.")

# Basit bir hesaplama
sayi1 = int(input("İlk sayıyı girin: "))
sayi2 = int(input("İkinci sayıyı girin: "))
toplam = sayi1 + sayi2

print(f"Toplam: {toplam}")

# Liste örneği
meyveler = ["elma", "armut", "muz", "portakal"]
print("\\nMeyveler:")
for i, meyve in enumerate(meyveler, 1):
    print(f"{i}. {meyve}")

print("\\nProgram tamamlandı!")
`);
});

// GUI kütüphanelerini kontrol et
function hasGUILibraries(code) {
    const guiLibraries = [
        'tkinter', 'pygame', 'PyQt5', 'PyQt6', 'PySide2', 'PySide6',
        'kivy', 'wxpython', 'flet', 'customtkinter', 'dearpygui',
        'turtle', 'matplotlib.pyplot', 'cv2.imshow'
    ];
    
    const lowerCode = code.toLowerCase();
    return guiLibraries.some(lib => {
        return lowerCode.includes(`import ${lib}`) || 
               lowerCode.includes(`from ${lib}`) ||
               (lib === 'turtle' && lowerCode.includes('import turtle')) ||
               (lib === 'tkinter' && lowerCode.includes('from tkinter')) ||
               (lib === 'pygame' && lowerCode.includes('import pygame'));
    });
}

// Input kullanımını kontrol et
function hasInputFunction(code) {
    return code.includes('input(') || code.includes('input (');
}

async function runCode() {
    const code = editor.getValue();
    
    if (!code.trim()) {
        appendToConsole('❌ Hata: Kod boş olamaz!', 'error');
        return;
    }

    // GUI kontrolü
    if (hasGUILibraries(code)) {
        appendToConsole('🖼️ GUI uygulaması tespit edildi!', 'warning');
        appendToConsole('⚠️ Pencere arayüzlü uygulamalar web ortamında çalıştırılamaz.', 'error');
        appendToConsole('💡 Çözüm: EXE dosyası olarak indirin ve bilgisayarınızda çalıştırın.', 'info');
        appendToConsole('📦 EXE indirmek için dosya adı girin ve "EXE İndir" butonuna tıklayın.', 'info');
        return;
    }
    
    // Input kontrolü - ayrı konsol aç
    if (hasInputFunction(code)) {
        appendToConsole('🔄 Etkileşimli program tespit edildi - Ayrı konsol açılıyor...', 'info');
        openConsoleWindow(code);
        return;
    }
    
    // Normal kod çalıştırma (input() olmayan kodlar)
    appendToConsole('🔄 Kod çalıştırılıyor...', 'info');
    
    try {
        const response = await fetch('/api/execute/python', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: code,
                packages: packages,
                interactive: false // Normal mod
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            if (result.output) {
                appendToConsole('📤 Çıktı:', 'success');
                appendToConsole(result.output, 'output');
            }
            
            if (result.error) {
                appendToConsole('⚠️ Hata/Uyarı:', 'error');
                appendToConsole(result.error, 'error');
            }
            
            appendToConsole(`✅ İşlem tamamlandı (Çıkış kodu: ${result.exitCode})`, 'success');
        } else {
            appendToConsole('❌ Sunucu hatası: ' + result.error, 'error');
        }
    } catch (error) {
        appendToConsole('❌ Bağlantı hatası: ' + error.message, 'error');
    }
}

// Ayrı konsol penceresi aç - processId assignment'i düzelt
function openConsoleWindow(code) {
    // Mevcut konsol varsa kapat
    if (consoleWindow && !consoleWindow.closed) {
        consoleWindow.close();
    }
    
    // Yeni konsol penceresi aç
    consoleWindow = window.open('', 'PythonConsole', 
        'width=800,height=600,scrollbars=yes,resizable=yes,toolbar=no,menubar=no'
    );
    
    consoleWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Python Konsol - CaYaCODE</title>
            <style>
                body {
                    background: #1e1e1e;
                    color: #fff;
                    font-family: 'Courier New', monospace;
                    margin: 0;
                    padding: 20px;
                    height: 100vh;
                    overflow: hidden;
                }
                .header {
                    background: #2d2d30;
                    padding: 10px;
                    margin: -20px -20px 20px -20px;
                    border-bottom: 2px solid #4CAF50;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .output-area {
                    height: calc(100vh - 150px);
                    overflow-y: auto;
                    background: #252526;
                    padding: 15px;
                    border: 1px solid #3e3e42;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    font-size: 14px;
                }
                .input-area {
                    margin-top: 10px;
                    display: flex;
                    gap: 10px;
                    align-items: center;
                }
                .input-area input {
                    flex: 1;
                    background: #3c3c3c;
                    color: #fff;
                    border: 1px solid #555;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-size: 14px;
                    font-family: 'Courier New', monospace;
                }
                .input-area button {
                    background: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                }
                .input-area button:hover {
                    background: #45a049;
                }
                .input-area button:disabled {
                    background: #666;
                    cursor: not-allowed;
                }
                .status {
                    color: #FFD700;
                    font-size: 12px;
                }
                .close-btn {
                    background: #f44336;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 12px;
                }
                .close-btn:hover {
                    background: #da190b;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div>
                    <h3>🐍 Python Etkileşimli Konsol</h3>
                    <div class="status" id="status">Program başlatılıyor...</div>
                </div>
                <button class="close-btn" onclick="window.close()">Kapat</button>
            </div>
            <div class="output-area" id="output"></div>
            <div class="input-area">
                <input type="text" id="inputField" placeholder="Değer girin..." disabled>
                <button id="sendBtn" onclick="sendInput()" disabled>Gönder</button>
            </div>
            
            <script>
                let waitingForInput = false;
                let processId = null; // Bu değişken önemli
                
                // window.processId'yi tanımla (ana pencereden erişilebilir)
                window.processId = null;
                
                // Enter key support
                document.getElementById('inputField').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter' && !this.disabled) {
                        sendInput();
                    }
                });
                
                function appendOutput(text) {
                    const output = document.getElementById('output');
                    output.textContent += text;
                    output.scrollTop = output.scrollHeight;
                }
                
                function setStatus(text) {
                    document.getElementById('status').textContent = text;
                }
                
                function enableInput() {
                    const inputField = document.getElementById('inputField');
                    const sendBtn = document.getElementById('sendBtn');
                    inputField.disabled = false;
                    sendBtn.disabled = false;
                    inputField.focus();
                    waitingForInput = true;
                    
                    // processId'yi güncelle
                    processId = window.processId;
                    console.log('enableInput called with processId:', processId);
                    setStatus('Input bekleniyor... (Process ID: ' + processId + ')');
                }
                
                function disableInput() {
                    const inputField = document.getElementById('inputField');
                    const sendBtn = document.getElementById('sendBtn');
                    inputField.disabled = true;
                    sendBtn.disabled = true;
                    waitingForInput = false;
                }
                
                async function sendInput() {
                    const inputField = document.getElementById('inputField');
                    const input = inputField.value;
                    
                    if (!input && input !== '0') return;
                    
                    // processId'yi güncel al
                    processId = window.processId;
                    console.log('Sending input with processId:', processId);
                    
                    if (!processId) {
                        appendOutput('HATA: Process ID bulunamadı!\\n');
                        setStatus('Hata: Process ID yok');
                        return;
                    }
                    
                    // Input'u göster
                    appendOutput(input + '\\n');
                    inputField.value = '';
                    disableInput();
                    setStatus('İşleniyor...');
                    
                    try {
                        const response = await fetch('/api/input/python', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ 
                                input: input,
                                processId: processId 
                            })
                        });
                        
                        const result = await response.json();
                        
                        if (result.output) {
                            appendOutput(result.output);
                        }
                        
                        if (result.error) {
                            appendOutput('HATA: ' + result.error + '\\n');
                        }
                        
                        if (result.waitingForInput) {
                            // ProcessId'yi güncelle
                            if (result.processId) {
                                window.processId = result.processId;
                                processId = result.processId;
                            }
                            enableInput();
                        } else {
                            setStatus('Program tamamlandı. (Çıkış kodu: ' + (result.exitCode || 0) + ')');
                        }
                    } catch (error) {
                        appendOutput('BAĞLANTI HATASI: ' + error.message + '\\n');
                        setStatus('Hata oluştu');
                    }
                }
                
                // Pencere kapatılınca ana pencereye bildir
                window.addEventListener('beforeunload', function() {
                    if (window.opener && !window.opener.closed) {
                        window.opener.appendToConsole('🔴 Konsol penceresi kapatıldı.', 'info');
                    }
                });
                
                // Global fonksiyonları tanımla (ana pencereden erişilebilir)
                window.enableInput = enableInput;
                window.appendOutput = appendOutput;
                window.setStatus = setStatus;
            </script>
        </body>
        </html>
    `);
    
    // Python programını başlat
    startInteractiveProgram(code);
}

// Etkileşimli program başlat
async function startInteractiveProgram(code) {
    try {
        const response = await fetch('/api/execute/python', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: code,
                packages: packages,
                interactive: true
            })
        });
        
        const result = await response.json();
        
        if (consoleWindow && !consoleWindow.closed) {
            if (result.output) {
                consoleWindow.appendOutput(result.output);
            }
            
            if (result.error) {
                consoleWindow.appendOutput('HATA: ' + result.error + '\\n');
            }
            
            if (result.waitingForInput) {
                // BURASI ÖNEMLİ: processId'yi konsol penceresine ata
                consoleWindow.processId = result.processId;
                console.log('Process ID assigned to console window:', result.processId);
                
                // enableInput fonksiyonunu çağır
                consoleWindow.enableInput();
            } else if (result.exitCode !== undefined) {
                consoleWindow.setStatus('Program tamamlandı. (Çıkış kodu: ' + result.exitCode + ')');
            }
        }
        
        appendToConsole('🟢 Etkileşimli konsol açıldı.', 'success');
        
    } catch (error) {
        appendToConsole('❌ Konsol başlatma hatası: ' + error.message, 'error');
        if (consoleWindow && !consoleWindow.closed) {
            consoleWindow.close();
        }
    }
}

async function buildExecutable() {
    const code = editor.getValue();
    const filename = document.getElementById('filename').value.trim();
    
    if (!code.trim()) {
        appendToConsole('❌ Hata: Kod boş olamaz!', 'error');
        return;
    }
    
    if (!filename) {
        appendToConsole('❌ Hata: Dosya adı gerekli!', 'error');
        return;
    }
    
    appendToConsole('🔨 EXE dosyası oluşturuluyor...', 'info');
    
    try {
        const response = await fetch('/api/build/python', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: code,
                filename: filename,
                packages: packages
            })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${filename}.exe`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            appendToConsole(`✅ ${filename}.exe başarıyla indirildi!`, 'success');
        } else {
            const result = await response.json();
            appendToConsole('❌ EXE oluşturma hatası: ' + result.error, 'error');
        }
    } catch (error) {
        appendToConsole('❌ EXE oluşturma hatası: ' + error.message, 'error');
    }
}

function addPackage() {
    const packageInput = document.getElementById('packageInput');
    const packageName = packageInput.value.trim();
    
    if (!packageName) {
        appendToConsole('❌ Paket adı boş olamaz!', 'error');
        return;
    }
    
    if (packages.includes(packageName)) {
        appendToConsole(`⚠️ ${packageName} paketi zaten ekli!`, 'warning');
        return;
    }
    
    packages.push(packageName);
    packageInput.value = '';
    updatePackageList();
    appendToConsole(`📦 ${packageName} paketi eklendi.`, 'success');
}

function removePackage(packageName) {
    packages = packages.filter(p => p !== packageName);
    updatePackageList();
    appendToConsole(`🗑️ ${packageName} paketi kaldırıldı.`, 'info');
}

function updatePackageList() {
    const packageList = document.getElementById('packageList');
    
    if (packages.length === 0) {
        packageList.innerHTML = '<div style="color: #ccc; text-align: center; padding: 10px;">Henüz paket eklenmedi</div>';
        return;
    }
    
    packageList.innerHTML = packages.map(pkg => `
        <div class="package-item">
            <span>📦 ${pkg}</span>
            <button class="btn" style="padding: 4px 8px; font-size: 11px;" onclick="removePackage('${pkg}')">Kaldır</button>
        </div>
    `).join('');
}

function appendToConsole(message, type = 'normal') {
    const consoleOutput = document.getElementById('consoleOutput');
    const timestamp = new Date().toLocaleTimeString();
    const line = `[${timestamp}] ${message}\n`;
    
    consoleOutput.textContent += line;
    consoleOutput.scrollTop = consoleOutput.scrollHeight;
}

function clearConsole() {
    const consoleOutput = document.getElementById('consoleOutput');
    consoleOutput.textContent = 'CaYaCODE Platform - Python Kodlama Ortamı ✨\nKodunuzu yazın ve çalıştır butonuna tıklayın.\n';
}

// Package input enter key support
document.getElementById('packageInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        addPackage();
    }
});

// Filename input enter key support
document.getElementById('filename').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        buildExecutable();
    }
});

// Ctrl+Enter to run code
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 'Enter') {
        runCode();
    }
});