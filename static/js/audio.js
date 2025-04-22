/**
 * Perito IA - Audio Processing JavaScript
 * Handles audio file preview and upload functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const audioUploadForm = document.getElementById('audioUploadForm');
    const audioInput = document.getElementById('audio');
    const audioPreview = document.getElementById('audioPreview');
    const audioPlayer = document.getElementById('audioPlayer');
    const uploadBtn = document.getElementById('uploadBtn');
    
    // Loading modal instance
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    
    // Setup audio file input change handler
    if (audioInput && audioPreview && audioPlayer) {
        audioInput.addEventListener('change', function() {
            // Reset previous preview
            audioPlayer.src = '';
            audioPreview.classList.add('d-none');
            
            if (this.files && this.files[0]) {
                const file = this.files[0];
                
                // Validate file size and type
                const fileSize = file.size / 1024 / 1024; // Convert to MB
                const fileType = file.type;
                
                // Check file type
                if (!fileType.startsWith('audio/')) {
                    showAudioError('O arquivo selecionado não é um arquivo de áudio válido.');
                    this.value = '';
                    return;
                }
                
                // Check file size (max 16MB)
                if (fileSize > 16) {
                    showAudioError('O arquivo de áudio é muito grande (máximo 16MB).');
                    this.value = '';
                    return;
                }
                
                // Create object URL for audio preview
                const objectURL = URL.createObjectURL(file);
                audioPlayer.src = objectURL;
                audioPreview.classList.remove('d-none');
                
                // Enable upload button
                if (uploadBtn) {
                    uploadBtn.disabled = false;
                }
            } else {
                // Disable upload button if no file selected
                if (uploadBtn) {
                    uploadBtn.disabled = true;
                }
            }
        });
    }
    
    // Setup form submission handler
    if (audioUploadForm) {
        audioUploadForm.addEventListener('submit', function(e) {
            // Check if file is selected
            if (!audioInput.files || audioInput.files.length === 0) {
                e.preventDefault();
                showAudioError('Por favor, selecione um arquivo de áudio para enviar.');
                return;
            }
            
            // Show loading modal
            loadingModal.show();
        });
    }
    
    // Function to show audio error message
    function showAudioError(message) {
        // Remove any existing alert
        const existingAlert = audioInput.parentNode.parentNode.querySelector('.alert');
        if (existingAlert) {
            existingAlert.remove();
        }
        
        // Create new alert
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger mt-2';
        alertDiv.innerHTML = `<i class="bi bi-exclamation-triangle"></i> ${message}`;
        
        // Insert alert after input group
        audioInput.parentNode.parentNode.appendChild(alertDiv);
        
        // Scroll to error
        alertDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    // Add audio waveform visualization if Web Audio API is available
    if (window.AudioContext || window.webkitAudioContext) {
        setupAudioVisualization();
    }
    
    // Function to setup audio visualization
    function setupAudioVisualization() {
        if (!audioPlayer) return;
        
        // Create audio context
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        const audioContext = new AudioContext();
        
        // Create analyzer node
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        
        // Connect audio element to analyzer
        let source = null;
        
        // Setup visualization when audio starts playing
        audioPlayer.addEventListener('play', function() {
            if (!source) {
                source = audioContext.createMediaElementSource(audioPlayer);
                source.connect(analyser);
                analyser.connect(audioContext.destination);
            }
            
            // Create visualization container if it doesn't exist
            let visualizer = document.getElementById('audio-visualizer');
            if (!visualizer) {
                visualizer = document.createElement('div');
                visualizer.id = 'audio-visualizer';
                visualizer.style.height = '60px';
                visualizer.style.marginTop = '10px';
                visualizer.style.display = 'flex';
                visualizer.style.alignItems = 'center';
                visualizer.style.justifyContent = 'center';
                
                // Create bars for visualization
                for (let i = 0; i < 32; i++) {
                    const bar = document.createElement('div');
                    bar.className = 'visualizer-bar';
                    bar.style.width = '8px';
                    bar.style.margin = '0 2px';
                    bar.style.backgroundColor = 'var(--bs-primary)';
                    bar.style.height = '5px';
                    bar.style.borderRadius = '2px';
                    bar.style.transition = 'height 0.05s ease';
                    visualizer.appendChild(bar);
                }
                
                // Add to the DOM
                audioPreview.appendChild(visualizer);
            }
            
            // Start visualization
            visualize();
        });
        
        // Visualization function
        function visualize() {
            if (!document.getElementById('audio-visualizer')) return;
            
            const bufferLength = analyser.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);
            
            function draw() {
                // Stop if audio is paused or ended
                if (audioPlayer.paused || audioPlayer.ended) return;
                
                // Request next animation frame
                requestAnimationFrame(draw);
                
                // Get frequency data
                analyser.getByteFrequencyData(dataArray);
                
                // Update visualizer bars
                const bars = document.querySelectorAll('.visualizer-bar');
                const step = Math.floor(bufferLength / bars.length);
                
                for (let i = 0; i < bars.length; i++) {
                    const value = dataArray[i * step];
                    const height = (value / 255) * 50 + 5; // Scale to 5-55px
                    bars[i].style.height = height + 'px';
                }
            }
            
            // Start drawing
            draw();
        }
    }
});
