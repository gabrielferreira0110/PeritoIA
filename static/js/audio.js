document.addEventListener('DOMContentLoaded', function() {
    // Elementos de áudio
    const audioFileInput = document.getElementById('audio_file');
    const audioPreviewContainer = document.getElementById('audio-preview-container');
    const audioVisualElement = document.getElementById('audio-visual');
    
    // Verifica se os elementos existem na página
    if (!audioFileInput) return;
    
    // Evento de mudança do input de arquivo
    audioFileInput.addEventListener('change', function(e) {
        if (this.files && this.files[0]) {
            const file = this.files[0];
            
            // Verificar tipo de arquivo
            if (!file.type.match('audio.*')) {
                showAudioError('O arquivo selecionado não é um áudio válido.');
                return;
            }
            
            // Mostrar preview do áudio
            showAudioPreview(file);
        }
    });
    
    // Função para mostrar erro
    function showAudioError(message) {
        if (audioPreviewContainer) {
            audioPreviewContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    ${message}
                </div>
            `;
        }
    }
    
    // Função para mostrar preview do áudio
    function showAudioPreview(file) {
        if (!audioPreviewContainer) return;
        
        // Criar URL para o arquivo
        const audioURL = URL.createObjectURL(file);
        
        // Gerar visualização do áudio
        audioPreviewContainer.innerHTML = `
            <div class="card mt-3">
                <div class="card-body">
                    <h5 class="card-title">
                        <i class="fas fa-file-audio me-2"></i>
                        ${file.name}
                    </h5>
                    <p class="card-text text-muted">
                        Tamanho: ${(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                    <div id="audio-visual" class="audio-visualization mb-3"></div>
                    <audio id="audio-player" controls class="w-100">
                        <source src="${audioURL}" type="${file.type}">
                        Seu navegador não suporta o elemento de áudio.
                    </audio>
                </div>
                <div class="card-footer bg-transparent">
                    <small class="text-muted">
                        Após o upload, o áudio será transcrito automaticamente.
                        Este processo pode levar alguns minutos dependendo do tamanho do arquivo.
                    </small>
                </div>
            </div>
        `;
        
        // Referência ao novo player
        const audioPlayer = document.getElementById('audio-player');
        const audioVisual = document.getElementById('audio-visual');
        
        // Adicionar visualização simples de onda de áudio (simulada)
        if (audioVisual) {
            createSimpleAudioWaveform(audioVisual);
        }
        
        // Adicionar eventos ao player
        if (audioPlayer) {
            audioPlayer.addEventListener('play', function() {
                // Animação ao reproduzir (opcional)
                if (audioVisual) {
                    audioVisual.classList.add('playing');
                }
            });
            
            audioPlayer.addEventListener('pause', function() {
                // Parar animação
                if (audioVisual) {
                    audioVisual.classList.remove('playing');
                }
            });
        }
    }
    
    // Função para criar uma forma de onda simples para o áudio (apenas visual)
    function createSimpleAudioWaveform(container) {
        if (!container) return;
        
        container.innerHTML = '';
        
        // Criar barras para simulação visual
        const barCount = 40;
        for (let i = 0; i < barCount; i++) {
            const height = Math.random() * 80 + 20; // Altura aleatória entre 20% e 100%
            const bar = document.createElement('div');
            bar.style.cssText = `
                position: absolute;
                bottom: 0;
                background: var(--bs-primary);
                width: 2%;
                height: ${height}%;
                left: ${(i * 100 / barCount)}%;
                opacity: 0.7;
                border-radius: 2px 2px 0 0;
            `;
            container.appendChild(bar);
        }
    }
});
