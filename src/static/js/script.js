// SafeSound JavaScript Application
class SafeSound {
    constructor() {
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.audioContext = null;
        this.analyser = null;
        this.websocket = null;
        this.selectedFile = null;
        
        this.initializeApp();
        this.setupEventListeners();
        this.loadThemePreference();
    }
    
    initializeApp() {
        console.log('SafeSound initialized');
        this.updateTranscriptionInfo('Aguardando transcrição...');
    }
    
    setupEventListeners() {
        // Theme toggle
        document.getElementById('darkModeToggle').addEventListener('change', (e) => {
            this.toggleTheme(e.target.checked);
        });
        
        // File upload
        const fileInput = document.getElementById('fileInput');
        const uploadBtn = document.getElementById('uploadBtn');
        const uploadArea = document.getElementById('uploadArea');
        
        uploadBtn.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e.target.files[0]));
        
        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        
        // File removal
        document.getElementById('removeFile').addEventListener('click', () => this.removeSelectedFile());
        
        // Transcription
        document.getElementById('transcribeBtn').addEventListener('click', () => this.transcribeFile());
        
        // Microphone
        document.getElementById('micBtn').addEventListener('click', () => this.toggleRecording());
        
        // Result actions
        document.getElementById('copyBtn').addEventListener('click', () => this.copyTranscription());
        document.getElementById('downloadBtn').addEventListener('click', () => this.downloadTranscription());
        document.getElementById('clearBtn').addEventListener('click', () => this.clearTranscription());
        
        // Modal controls
        document.getElementById('closeErrorModal').addEventListener('click', () => this.hideModal('errorModal'));
        document.getElementById('closeErrorBtn').addEventListener('click', () => this.hideModal('errorModal'));
        
        // Prevent default drag behaviors
        document.addEventListener('dragover', (e) => e.preventDefault());
        document.addEventListener('drop', (e) => e.preventDefault());
    }
    
    // Theme Management
    loadThemePreference() {
        const savedTheme = localStorage.getItem('safesound-theme');
        const isDark = savedTheme === 'dark';
        document.getElementById('darkModeToggle').checked = isDark;
        this.applyTheme(isDark);
    }
    
    toggleTheme(isDark) {
        this.applyTheme(isDark);
        localStorage.setItem('safesound-theme', isDark ? 'dark' : 'light');
    }
    
    applyTheme(isDark) {
        if (isDark) {
            document.body.setAttribute('data-theme', 'dark');
        } else {
            document.body.removeAttribute('data-theme');
        }
    }
    
    // File Upload Management
    handleDragOver(e) {
        e.preventDefault();
        e.target.closest('.upload-area').classList.add('dragover');
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        e.target.closest('.upload-area').classList.remove('dragover');
    }
    
    handleDrop(e) {
        e.preventDefault();
        e.target.closest('.upload-area').classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.handleFileSelect(files[0]);
        }
    }
    
    handleFileSelect(file) {
        if (!file) return;
        
        // Validate file type
        const allowedTypes = ['.mp3', '.wav', '.m4a', '.flac', '.ogg'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowedTypes.includes(fileExtension)) {
            this.showError('Tipo de arquivo não suportado. Use: MP3, WAV, M4A, FLAC, OGG');
            return;
        }
        
        // Validate file size (100MB)
        const maxSize = 100 * 1024 * 1024;
        if (file.size > maxSize) {
            this.showError('Arquivo muito grande. Tamanho máximo: 100MB');
            return;
        }
        
        this.selectedFile = file;
        this.showSelectedFile(file);
    }
    
    showSelectedFile(file) {
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('fileSelected').style.display = 'flex';
        document.getElementById('transcribeBtn').disabled = false;
        document.getElementById('uploadArea').style.display = 'none';
    }
    
    removeSelectedFile() {
        this.selectedFile = null;
        document.getElementById('fileSelected').style.display = 'none';
        document.getElementById('transcribeBtn').disabled = true;
        document.getElementById('uploadArea').style.display = 'block';
        document.getElementById('fileInput').value = '';
    }
    
    // File Transcription
    async transcribeFile() {
        if (!this.selectedFile) return;
        
        const model = document.getElementById('modelSelect').value;
        const action = document.getElementById('actionSelect').value;
        
        const formData = new FormData();
        formData.append('file', this.selectedFile);
        formData.append('model', model);
        formData.append('action', action);
        
        this.showProgressModal();
        this.updateProgress(10, 'Enviando arquivo...');
        
        try {
            const response = await fetch('/api/upload_audio', {
                method: 'POST',
                body: formData
            });
            
            this.updateProgress(50, 'Processando áudio...');
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro no servidor');
            }
            
            this.updateProgress(90, 'Finalizando...');
            
            const result = await response.json();
            
            this.updateProgress(100, 'Concluído!');
            
            setTimeout(() => {
                this.hideProgressModal();
                this.displayTranscriptionResult(result);
                this.showSuccess('Transcrição realizada com sucesso!');
            }, 500);
            
        } catch (error) {
            this.hideProgressModal();
            this.showError(`Erro na transcrição: ${error.message}`);
        }
    }
    
    // Microphone Recording
    async toggleRecording() {
        if (this.isRecording) {
            this.stopRecording();
        } else {
            await this.startRecording();
        }
    }
    
    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true
                }
            });
            
            this.audioChunks = [];
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => {
                this.processRecordedAudio();
            };
            
            // Setup audio visualization
            this.setupAudioVisualization(stream);
            
            // Start real-time transcription WebSocket
            this.connectWebSocket();
            
            this.mediaRecorder.start(1000); // Collect chunks every second
            this.isRecording = true;
            this.updateRecordingUI(true);
            
        } catch (error) {
            console.error('Error accessing microphone:', error);
            this.showError('Erro ao acessar o microfone. Verifique as permissões.');
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.updateRecordingUI(false);
            
            // Stop all tracks
            if (this.mediaRecorder.stream) {
                this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            }
            
            // Close WebSocket
            if (this.websocket) {
                this.websocket.close();
                this.websocket = null;
            }
            
            // Stop visualization
            if (this.audioContext) {
                this.audioContext.close();
                this.audioContext = null;
            }
        }
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/api/transcribe_stream`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected');
            // Send configuration
            const config = {
                model: document.getElementById('modelSelect').value,
                action: document.getElementById('actionSelect').value
            };
            this.websocket.send(JSON.stringify(config));
        };
        
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showError('Erro na conexão de tempo real');
        };
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'transcription':
                this.appendRealtimeTranscription(data.text);
                break;
            case 'progress':
                // Handle progress updates if needed
                break;
            case 'error':
                this.showError(data.message);
                break;
        }
    }
    
    processRecordedAudio() {
        if (this.audioChunks.length === 0) return;
        
        // Send the last chunk via WebSocket for final processing
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        
        // Convert to ArrayBuffer and send
        audioBlob.arrayBuffer().then(buffer => {
            if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                this.websocket.send(buffer);
            }
        });
    }
    
    setupAudioVisualization(stream) {
        this.audioContext = new AudioContext();
        this.analyser = this.audioContext.createAnalyser();
        const source = this.audioContext.createMediaStreamSource(stream);
        source.connect(this.analyser);
        
        this.analyser.fftSize = 256;
        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        const canvas = document.getElementById('visualizerCanvas');
        const ctx = canvas.getContext('2d');
        
        const draw = () => {
            if (!this.isRecording) return;
            
            requestAnimationFrame(draw);
            
            this.analyser.getByteFrequencyData(dataArray);
            
            ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const barWidth = (canvas.width / bufferLength) * 2.5;
            let barHeight;
            let x = 0;
            
            for (let i = 0; i < bufferLength; i++) {
                barHeight = (dataArray[i] / 255) * canvas.height;
                
                const r = barHeight + 25 * (i / bufferLength);
                const g = 250 * (i / bufferLength);
                const b = 50;
                
                ctx.fillStyle = `rgb(${r},${g},${b})`;
                ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
                
                x += barWidth + 1;
            }
        };
        
        draw();
    }
    
    updateRecordingUI(isRecording) {
        const micBtn = document.getElementById('micBtn');
        const recordingIndicator = document.getElementById('recordingIndicator');
        const visualizer = document.getElementById('audioVisualizer');
        
        if (isRecording) {
            micBtn.classList.add('recording');
            micBtn.querySelector('span').textContent = 'Parar Gravação';
            micBtn.querySelector('i').className = 'fas fa-stop';
            recordingIndicator.style.display = 'flex';
            visualizer.style.display = 'block';
        } else {
            micBtn.classList.remove('recording');
            micBtn.querySelector('span').textContent = 'Iniciar Gravação';
            micBtn.querySelector('i').className = 'fas fa-microphone';
            recordingIndicator.style.display = 'none';
            visualizer.style.display = 'none';
        }
    }
    
    // Transcription Results
    displayTranscriptionResult(result) {
        const transcriptionText = document.getElementById('transcriptionText');
        transcriptionText.innerHTML = `<p>${result.text}</p>`;
        
        this.updateTranscriptionInfo(
            `Modelo: ${result.model_used} | ` +
            `Ação: ${result.action_performed} | ` +
            `Idioma: ${result.language || 'N/A'} | ` +
            `Tempo: ${result.processing_time.toFixed(2)}s`
        );
        
        this.enableResultActions();
    }
    
    appendRealtimeTranscription(text) {
        if (!text.trim()) return;
        
        const transcriptionText = document.getElementById('transcriptionText');
        
        // Remove placeholder if exists
        const placeholder = transcriptionText.querySelector('.placeholder-text');
        if (placeholder) {
            placeholder.remove();
        }
        
        // Append new text
        const existingText = transcriptionText.textContent || '';
        transcriptionText.innerHTML = `<p>${existingText} ${text}</p>`;
        
        this.updateTranscriptionInfo('Transcrição em tempo real ativa');
        this.enableResultActions();
    }
    
    updateTranscriptionInfo(info) {
        document.getElementById('transcriptionInfo').textContent = info;
    }
    
    enableResultActions() {
        document.getElementById('copyBtn').disabled = false;
        document.getElementById('downloadBtn').disabled = false;
        document.getElementById('clearBtn').disabled = false;
    }
    
    disableResultActions() {
        document.getElementById('copyBtn').disabled = true;
        document.getElementById('downloadBtn').disabled = true;
        document.getElementById('clearBtn').disabled = true;
    }
    
    copyTranscription() {
        const text = document.getElementById('transcriptionText').textContent;
        if (!text || text.includes('O texto transcrito aparecerá aqui')) {
            this.showError('Nenhum texto para copiar');
            return;
        }
        
        navigator.clipboard.writeText(text).then(() => {
            this.showSuccess('Texto copiado para a área de transferência!');
        }).catch(() => {
            this.showError('Erro ao copiar texto');
        });
    }
    
    downloadTranscription() {
        const text = document.getElementById('transcriptionText').textContent;
        if (!text || text.includes('O texto transcrito aparecerá aqui')) {
            this.showError('Nenhum texto para baixar');
            return;
        }
        
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `transcricao_${new Date().toISOString().slice(0, 10)}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showSuccess('Arquivo baixado com sucesso!');
    }
    
    clearTranscription() {
        const transcriptionText = document.getElementById('transcriptionText');
        transcriptionText.innerHTML = '<p class="placeholder-text">O texto transcrito aparecerá aqui...</p>';
        this.updateTranscriptionInfo('Aguardando transcrição...');
        this.disableResultActions();
    }
    
    // Progress Modal
    showProgressModal() {
        document.getElementById('progressModal').style.display = 'block';
    }
    
    hideProgressModal() {
        document.getElementById('progressModal').style.display = 'none';
    }
    
    updateProgress(percentage, status) {
        document.getElementById('progressFill').style.width = `${percentage}%`;
        document.getElementById('progressPercentage').textContent = `${percentage}%`;
        document.getElementById('progressStatus').textContent = status;
    }
    
    // Error Handling
    showError(message) {
        document.getElementById('errorMessage').textContent = message;
        this.showModal('errorModal');
    }
    
    showSuccess(message) {
        const notification = document.getElementById('successNotification');
        document.getElementById('successMessage').textContent = message;
        notification.style.display = 'flex';
        
        setTimeout(() => {
            notification.style.display = 'none';
        }, 4000);
    }
    
    showModal(modalId) {
        document.getElementById(modalId).style.display = 'block';
    }
    
    hideModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.safesound = new SafeSound();
});
