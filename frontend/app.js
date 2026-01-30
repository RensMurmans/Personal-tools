// ============================================
// STATE MANAGEMENT
// ============================================

const API_BASE_URL = 'http://localhost:5001/api';

let currentDirection = 'docx-to-pdf'; // 'docx-to-pdf' or 'pdf-to-docx'
let fileQueue = []; // Files waiting to be converted
let convertedFiles = []; // Successfully converted files

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    updateFileInputAccept();
});

function initializeEventListeners() {
    // Conversion direction toggle
    document.getElementById('toggle-docx-to-pdf').addEventListener('click', () => {
        setConversionDirection('docx-to-pdf');
    });

    document.getElementById('toggle-pdf-to-docx').addEventListener('click', () => {
        setConversionDirection('pdf-to-docx');
    });

    // File input
    const fileInput = document.getElementById('file-input');
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    const dropZone = document.getElementById('drop-zone');

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');

        const files = Array.from(e.dataTransfer.files);
        addFilesToQueue(files);
    });

    // Convert all button
    document.getElementById('convert-all-btn').addEventListener('click', convertAllFiles);

    // Download all button
    document.getElementById('download-all-btn').addEventListener('click', downloadAllFiles);
}

// ============================================
// CONVERSION DIRECTION
// ============================================

function setConversionDirection(direction) {
    currentDirection = direction;

    // Update button states
    const buttons = document.querySelectorAll('.toggle-btn');
    buttons.forEach(btn => {
        if (btn.dataset.direction === direction) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Update file input accept attribute
    updateFileInputAccept();

    // Update hint text
    const hint = document.getElementById('file-type-hint');
    if (direction === 'docx-to-pdf') {
        hint.textContent = 'Supported format: .docx';
    } else {
        hint.textContent = 'Supported format: .pdf';
    }

    // Clear existing queue
    fileQueue = [];
    updateFileQueueUI();
}

function updateFileInputAccept() {
    const fileInput = document.getElementById('file-input');
    if (currentDirection === 'docx-to-pdf') {
        fileInput.setAttribute('accept', '.docx');
    } else {
        fileInput.setAttribute('accept', '.pdf');
    }
}

// ============================================
// FILE HANDLING
// ============================================

function handleFileSelect(event) {
    const files = Array.from(event.target.files);
    addFilesToQueue(files);

    // Reset input so same file can be selected again
    event.target.value = '';
}

function addFilesToQueue(files) {
    const validFiles = files.filter(file => {
        const extension = file.name.split('.').pop().toLowerCase();

        if (currentDirection === 'docx-to-pdf') {
            return extension === 'docx';
        } else {
            return extension === 'pdf';
        }
    });

    if (validFiles.length === 0) {
        alert(`Please select valid ${currentDirection === 'docx-to-pdf' ? '.docx' : '.pdf'} files`);
        return;
    }

    validFiles.forEach(file => {
        const fileObj = {
            id: generateId(),
            file: file,
            name: file.name,
            size: formatFileSize(file.size),
            status: 'queued'
        };

        fileQueue.push(fileObj);
    });

    updateFileQueueUI();
}

function removeFileFromQueue(fileId) {
    fileQueue = fileQueue.filter(f => f.id !== fileId);
    updateFileQueueUI();
}

function updateFileQueueUI() {
    const queueSection = document.getElementById('file-queue-section');
    const queueContainer = document.getElementById('file-queue');

    if (fileQueue.length === 0) {
        queueSection.style.display = 'none';
        return;
    }

    queueSection.style.display = 'block';
    queueContainer.innerHTML = '';

    fileQueue.forEach(fileObj => {
        const fileItem = createFileItem(fileObj, 'queue');
        queueContainer.appendChild(fileItem);
    });
}

// Optimized function to only update progress bars without rebuilding DOM
function updateProgressOnly(fileObj) {
    const fileItem = document.querySelector(`.file-item[data-file-id="${fileObj.id}"]`);
    if (!fileItem) return;

    const progressFill = fileItem.querySelector('.progress-fill');
    const progressText = fileItem.querySelector('.progress-text');

    if (progressFill) {
        progressFill.style.width = `${Math.round(fileObj.progress)}%`;
    }
    if (progressText) {
        progressText.textContent = `Converting... ${Math.round(fileObj.progress)}%`;
    }
}

function createFileItem(fileObj, type) {
    const div = document.createElement('div');
    div.className = 'file-item';
    div.dataset.fileId = fileObj.id;

    const icon = currentDirection === 'docx-to-pdf' ? '📄' : '📑';

    let progressHTML = '';
    if (fileObj.status === 'processing') {
        progressHTML = `
            <div class="progress-container">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${fileObj.progress || 0}%"></div>
                </div>
                <div class="progress-text">Converting... ${fileObj.progress || 0}%</div>
            </div>
        `;
    }

    let actionsHTML = '';
    if (type === 'queue') {
        actionsHTML = `
            <div class="file-actions">
                <button class="btn btn-danger btn-sm" onclick="removeFileFromQueue('${fileObj.id}')">
                    <span class="btn-icon">🗑️</span>
                    Remove
                </button>
            </div>
        `;
    } else if (type === 'converted') {
        actionsHTML = `
            <div class="file-actions">
                <button class="btn btn-success btn-sm" onclick="downloadFile('${fileObj.fileId}', '${fileObj.name}')">
                    <span class="btn-icon">📥</span>
                    Download
                </button>
            </div>
        `;
    }

    div.innerHTML = `
        <div class="file-icon">${icon}</div>
        <div class="file-info">
            <div class="file-name">${fileObj.name}</div>
            <div class="file-size">${fileObj.size}</div>
            ${progressHTML}
        </div>
        ${actionsHTML}
    `;

    return div;
}

// ============================================
// CONVERSION
// ============================================

async function convertAllFiles() {
    if (fileQueue.length === 0) return;

    const convertBtn = document.getElementById('convert-all-btn');
    convertBtn.disabled = true;
    convertBtn.innerHTML = '<span class="btn-icon">⏳</span> Converting...';

    // Convert files in parallel
    const promises = fileQueue.map(fileObj => convertFile(fileObj));
    await Promise.all(promises);

    convertBtn.disabled = false;
    convertBtn.textContent = 'Convert All';

    // Clear queue
    fileQueue = [];
    updateFileQueueUI();
    updateConvertedFilesUI();
}

async function convertFile(fileObj) {
    fileObj.status = 'processing';
    fileObj.progress = 0;
    updateFileQueueUI();

    const formData = new FormData();
    formData.append('file', fileObj.file);

    const endpoint = currentDirection === 'docx-to-pdf'
        ? `${API_BASE_URL}/convert/docx-to-pdf`
        : `${API_BASE_URL}/convert/pdf-to-docx`;

    try {
        // Smooth progress simulation with easing
        // Starts fast, slows down as it approaches 90%
        const progressInterval = setInterval(() => {
            if (fileObj.progress < 90) {
                // Easing: bigger jumps at start, smaller near the end
                const remaining = 90 - fileObj.progress;
                const increment = Math.max(0.3, remaining * 0.02);
                fileObj.progress = Math.min(90, fileObj.progress + increment);
                updateProgressOnly(fileObj);  // Only update progress bar, not entire DOM
            }
        }, 50);

        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });

        clearInterval(progressInterval);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Conversion failed');
        }

        const result = await response.json();

        fileObj.progress = 100;
        fileObj.status = 'completed';
        updateFileQueueUI();

        // Add to converted files
        const outputExtension = currentDirection === 'docx-to-pdf' ? 'pdf' : 'docx';
        convertedFiles.push({
            id: generateId(),
            fileId: result.file_id,
            name: result.original_name, // This is the CONVERTED filename from backend with correct extension
            size: fileObj.size,
            status: 'completed'
        });

    } catch (error) {
        console.error('Conversion error:', error);
        fileObj.status = 'error';
        fileObj.error = error.message;
        alert(`Error converting ${fileObj.name}: ${error.message}`);
    }
}

// ============================================
// DOWNLOAD
// ============================================

async function downloadFile(fileId, filename) {
    // Direct navigation to download URL
    // Server sends Content-Disposition: attachment which forces download
    // NOT using target=_blank to avoid opening in new tab
    window.location.href = `${API_BASE_URL}/download/${fileId}`;
}

async function downloadAllFiles() {
    if (convertedFiles.length === 0) return;

    const fileIds = convertedFiles.map(f => f.fileId);

    // Create a hidden form to submit POST request
    // This allows the browser to handle Content-Disposition properly
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `${API_BASE_URL}/download/bulk`;
    form.style.display = 'none';

    // Add file_ids as a hidden input (JSON encoded)
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'file_ids';
    input.value = JSON.stringify(fileIds);
    form.appendChild(input);

    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}

// ============================================
// CONVERTED FILES UI
// ============================================

function updateConvertedFilesUI() {
    const convertedSection = document.getElementById('converted-files-section');
    const convertedContainer = document.getElementById('converted-files');

    if (convertedFiles.length === 0) {
        convertedSection.style.display = 'none';
        return;
    }

    convertedSection.style.display = 'block';
    convertedContainer.innerHTML = '';

    convertedFiles.forEach(fileObj => {
        const fileItem = createFileItem(fileObj, 'converted');
        convertedContainer.appendChild(fileItem);
    });
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function generateId() {
    return `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
