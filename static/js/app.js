// Universal Toolkit - Main JavaScript
class UniversalToolkit {
    constructor() {
        this.initializeEventListeners();
        this.setupFileUpload();
        this.setupProgressTracking();
    }

    initializeEventListeners() {
        // Mobile menu toggle
        const menuToggle = document.getElementById('menuToggle');
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.getElementById('mainContent');

        if (menuToggle) {
            menuToggle.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
                mainContent.classList.toggle('expanded');
            });
        }

        // Form submissions
        document.addEventListener('submit', this.handleFormSubmit.bind(this));
        
        // Progress updates
        this.progressCheckers = new Map();
    }

    setupFileUpload() {
        // Drag and drop functionality
        const uploadAreas = document.querySelectorAll('.file-upload-area');
        
        uploadAreas.forEach(area => {
            const fileInput = area.querySelector('.file-input');
            
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                area.addEventListener(eventName, this.preventDefaults, false);
                document.body.addEventListener(eventName, this.preventDefaults, false);
            });

            ['dragenter', 'dragover'].forEach(eventName => {
                area.addEventListener(eventName, () => area.classList.add('dragover'), false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                area.addEventListener(eventName, () => area.classList.remove('dragover'), false);
            });

            area.addEventListener('drop', (e) => {
                const files = e.dataTransfer.files;
                if (files.length > 0 && fileInput) {
                    fileInput.files = files;
                    this.updateFileUploadDisplay(area, files[0]);
                }
            });

            if (fileInput) {
                fileInput.addEventListener('change', (e) => {
                    if (e.target.files.length > 0) {
                        this.updateFileUploadDisplay(area, e.target.files[0]);
                    }
                });
            }

            area.addEventListener('click', () => {
                if (fileInput) fileInput.click();
            });
        });
    }

    setupProgressTracking() {
        // Initialize progress containers
        const progressContainers = document.querySelectorAll('.progress-container');
        progressContainers.forEach(container => {
            container.style.display = 'none';
        });
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    updateFileUploadDisplay(area, file) {
        const textElement = area.querySelector('.file-upload-text');
        const hintElement = area.querySelector('.file-upload-hint');
        
        if (textElement) {
            textElement.textContent = file.name;
        }
        if (hintElement) {
            hintElement.textContent = `${this.formatFileSize(file.size)} - Ready to upload`;
        }
        
        area.classList.add('file-selected');
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async handleFormSubmit(e) {
        const form = e.target;
        if (!form.classList.contains('toolkit-form')) return;
        
        e.preventDefault();
        
        const submitButton = form.querySelector('button[type="submit"], .btn');
        const progressContainer = form.querySelector('.progress-container');
        const resultContainer = form.querySelector('.result-container');
        
        // Reset UI
        if (progressContainer) {
            progressContainer.style.display = 'block';
            progressContainer.classList.add('active');
        }
        if (resultContainer) {
            resultContainer.style.display = 'none';
            resultContainer.className = 'result-container';
        }
        
        // Disable submit button
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = `
                <svg class="spin" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M11.251.068a.5.5 0 0 1 .227.58L9.677 6.5H13a.5.5 0 0 1 .364.843l-8 8.5a.5.5 0 0 1-.842-.49L6.323 9.5H3a.5.5 0 0 1-.364-.843l8-8.5a.5.5 0 0 1 .615-.09z"/>
                </svg>
                Processing...
            `;
        }

        try {
            let response;
            const formData = new FormData(form);
            const action = form.action || form.dataset.action;
            
            if (form.classList.contains('url-form')) {
                // Handle URL-based forms (downloader)
                const data = Object.fromEntries(formData.entries());
                response = await fetch(action, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
            } else {
                // Handle file upload forms
                response = await fetch(action, {
                    method: 'POST',
                    body: formData
                });
            }

            const result = await response.json();
            
            if (result.task_id) {
                this.trackProgress(result.task_id, progressContainer, resultContainer);
            } else if (result.error) {
                this.showResult(resultContainer, 'error', 'Error', result.error);
            } else {
                this.showResult(resultContainer, 'success', 'Success', result.message || 'Operation completed successfully!');
            }

        } catch (error) {
            console.error('Form submission error:', error);
            this.showResult(resultContainer, 'error', 'Error', 'An unexpected error occurred. Please try again.');
        } finally {
            // Re-enable submit button
            if (submitButton) {
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.innerHTML = submitButton.dataset.originalText || 'Submit';
                }, 1000);
            }
        }
    }

    trackProgress(taskId, progressContainer, resultContainer) {
        if (this.progressCheckers.has(taskId)) {
            clearInterval(this.progressCheckers.get(taskId));
        }

        const checkProgress = async () => {
            try {
                const response = await fetch(`/api/progress/${taskId}`);
                const progress = await response.json();
                
                this.updateProgress(progressContainer, progress);
                
                if (progress.status === 'completed') {
                    clearInterval(this.progressCheckers.get(taskId));
                    this.progressCheckers.delete(taskId);
                    
                    this.showResult(resultContainer, 'success', 'Completed!', progress.message);
                    this.showDownloadButton(resultContainer, taskId);
                    
                    if (progressContainer) {
                        setTimeout(() => {
                            progressContainer.style.display = 'none';
                        }, 2000);
                    }
                } else if (progress.status === 'error') {
                    clearInterval(this.progressCheckers.get(taskId));
                    this.progressCheckers.delete(taskId);
                    
                    this.showResult(resultContainer, 'error', 'Error', progress.message);
                    
                    if (progressContainer) {
                        progressContainer.style.display = 'none';
                    }
                }
            } catch (error) {
                console.error('Progress check error:', error);
            }
        };

        const interval = setInterval(checkProgress, 1000);
        this.progressCheckers.set(taskId, interval);
        
        // Initial check
        checkProgress();
    }

    updateProgress(progressContainer, progress) {
        if (!progressContainer) return;
        
        const progressBar = progressContainer.querySelector('.progress-fill');
        const progressText = progressContainer.querySelector('.progress-text');
        
        if (progressBar) {
            progressBar.style.width = `${progress.progress}%`;
        }
        
        if (progressText) {
            progressText.textContent = progress.message || `${progress.progress}% complete`;
        }
    }

    showResult(resultContainer, type, title, message) {
        if (!resultContainer) return;
        
        resultContainer.className = `result-container ${type}`;
        resultContainer.style.display = 'block';
        
        const titleElement = resultContainer.querySelector('.result-title');
        const messageElement = resultContainer.querySelector('.result-message');
        
        if (titleElement) titleElement.textContent = title;
        if (messageElement) messageElement.textContent = message;
        
        resultContainer.classList.add('fade-in');
    }

    showDownloadButton(resultContainer, taskId) {
        if (!resultContainer) return;
        
        const existingButton = resultContainer.querySelector('.download-btn');
        if (existingButton) return;
        
        const downloadButton = document.createElement('a');
        downloadButton.href = `/download/${taskId}`;
        downloadButton.className = 'btn btn-success download-btn';
        downloadButton.innerHTML = `
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
                <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/>
            </svg>
            Download File
        `;
        
        resultContainer.appendChild(downloadButton);
    }

    // Utility functions
    showAlert(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;
        
        document.body.insertBefore(alert, document.body.firstChild);
        
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    // QR Code generation
    async generateQRCode(text) {
        try {
            const response = await fetch('/api/qr/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            
            const result = await response.json();
            return result;
        } catch (error) {
            console.error('QR generation error:', error);
            throw error;
        }
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.toolkit = new UniversalToolkit();
    
    // Store original button text for forms
    document.querySelectorAll('.btn[type="submit"]').forEach(button => {
        button.dataset.originalText = button.innerHTML;
    });
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UniversalToolkit;
}