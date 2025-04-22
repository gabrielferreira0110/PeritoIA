document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips do Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Funcionalidade para geração de seções com IA
    const gerarBotoes = document.querySelectorAll('.btn-gerar-secao');
    gerarBotoes.forEach(botao => {
        botao.addEventListener('click', function(e) {
            e.preventDefault();
            
            const secaoTipo = this.dataset.secao;
            const laudoId = this.dataset.laudo;
            const conteudoElement = document.getElementById(`conteudo-${secaoTipo}`);
            const spinner = this.querySelector('.spinner-border');
            const botaoTexto = this.querySelector('.btn-text');
            
            // Mostrar spinner e desabilitar botão
            spinner.classList.remove('d-none');
            botaoTexto.textContent = 'Gerando...';
            this.disabled = true;
            
            // Fazer requisição para gerar conteúdo
            fetch(`/laudos/${laudoId}/secoes/${secaoTipo}/gerar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Atualizar a área de conteúdo
                    if (conteudoElement) {
                        conteudoElement.value = data.content;
                    }
                    
                    // Notificar o usuário
                    showToast('Conteúdo gerado com sucesso!', 'success');
                } else {
                    showToast(`Erro: ${data.error}`, 'danger');
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                showToast('Ocorreu um erro ao tentar gerar o conteúdo.', 'danger');
            })
            .finally(() => {
                // Esconder spinner e habilitar botão
                spinner.classList.add('d-none');
                botaoTexto.textContent = 'Gerar com IA';
                this.disabled = false;
            });
        });
    });
    
    // Função para exibir toast de notificação
    function showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            // Criar container de toast se não existir
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
        }
        
        const toastId = `toast-${Date.now()}`;
        const toastHtml = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <strong class="me-auto">Perito IA</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Fechar"></button>
                </div>
                <div class="toast-body ${type ? `text-${type}` : ''}">
                    ${message}
                </div>
            </div>
        `;
        
        const toastContainer = document.getElementById('toast-container');
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 5000 });
        toast.show();
        
        // Remover o toast após fechado
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    }
    
    // Preview de upload de arquivo
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const filePreview = document.getElementById(`${this.id}-preview`);
            if (filePreview && this.files && this.files[0]) {
                const fileName = this.files[0].name;
                const fileSize = (this.files[0].size / 1024 / 1024).toFixed(2); // em MB
                
                filePreview.innerHTML = `
                    <div class="alert alert-info">
                        <i class="fas fa-file me-2"></i>
                        <strong>${fileName}</strong> (${fileSize} MB)
                    </div>
                `;
            }
        });
    });
    
    // Confirmação de ações importantes
    const confirmBtns = document.querySelectorAll('[data-confirm]');
    confirmBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm || 'Tem certeza que deseja realizar esta ação?')) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Progresso do laudo
    updateProgressBar();
    
    function updateProgressBar() {
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            const totalSteps = document.querySelectorAll('.progress-step').length;
            const completedSteps = document.querySelectorAll('.progress-step.completed').length;
            const percentage = Math.round((completedSteps / totalSteps) * 100);
            
            progressBar.style.width = `${percentage}%`;
            progressBar.setAttribute('aria-valuenow', percentage);
            progressBar.textContent = `${percentage}%`;
        }
    }
});
