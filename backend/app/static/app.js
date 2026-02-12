const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileStatus = document.getElementById('fileStatus');
const fileNameDisplay = document.getElementById('fileName');
const statusDot = document.getElementById('statusDot');
const docIdDisplay = document.getElementById('docId');
const chunkCountDisplay = document.getElementById('chunkCount');
const processingOverlay = document.getElementById('processingOverlay');

const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');

const extractBtn = document.getElementById('extractBtn');
const autoSchemaBtn = document.getElementById('autoSchemaBtn');
const schemaInput = document.getElementById('schemaInput');
const extractionOutput = document.getElementById('extractionOutput');

// State
let currentDocId = null;

// Tab Switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

        btn.classList.add('active');
        document.getElementById(btn.dataset.tab).classList.add('active');
    });
});

// File Upload Handling
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        handleUpload(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', () => {
    if (fileInput.files.length) {
        handleUpload(fileInput.files[0]);
    }
});

async function handleUpload(file) {
    // UI Update
    fileStatus.style.display = 'flex';
    fileNameDisplay.textContent = file.name;
    statusDot.className = 'status-indicator status-processing';
    processingOverlay.classList.add('active');

    // Disable inputs during upload
    setInteractivity(false);

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Upload failed');

        const data = await response.json();

        // Success State
        currentDocId = data.document_id;
        docIdDisplay.textContent = currentDocId.substring(0, 8) + '...';
        chunkCountDisplay.textContent = data.chunks_count;

        statusDot.className = 'status-indicator status-ready';
        setInteractivity(true);
        addBotMessage(`Document "${file.name}" processed successfully. You can now chat or extract structured data.`);

        // Render Chunks
        renderChunks(data.chunks);

        // Auto-fill Schema and Extraction
        if (data.proposed_schema) {
            schemaInput.value = JSON.stringify(data.proposed_schema, null, 2);
        }
        if (data.extraction) {
            extractionOutput.textContent = JSON.stringify(data.extraction, null, 2);
        }

    } catch (error) {
        console.error(error);
        statusDot.className = 'status-indicator status-error';
        docIdDisplay.textContent = 'Error';
        alert('Failed to upload document. Please try again.');
    } finally {
        processingOverlay.classList.remove('active');
    }
}

function setInteractivity(enabled) {
    chatInput.disabled = !enabled;
    sendBtn.disabled = !enabled;
    extractBtn.disabled = !enabled;
    autoSchemaBtn.disabled = !enabled;
}

// Chat Handling
async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text || !currentDocId) return;

    addUserMessage(text);
    chatInput.value = '';

    // Loading state for chat could be a spinner, but we'll just wait
    const loadingId = addBotMessage('Analyzing document...', null, true);

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: text,
                document_id: currentDocId
            })
        });

        const data = await response.json();

        // Remove loading message and add real response
        removeMessage(loadingId);

        addBotMessage(data.answer, data);

    } catch (error) {
        removeMessage(loadingId);
        addBotMessage('Sorry, I encountered an error answering that.');
    }
}

sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

function addUserMessage(text) {
    const div = document.createElement('div');
    div.className = 'message user';
    div.textContent = text;
    chatMessages.appendChild(div);
    scrollToBottom();
}

/**
 * Adds a bot message to the chat.
 * @param {string} text - The main answer text.
 * @param {object} intelligence - Optional data containing metrics, mappings, and sources.
 * @param {boolean} isLoading - Whether this is a placeholder loading message.
 */
function addBotMessage(text, intelligence = null, isLoading = false) {
    const div = document.createElement('div');
    div.className = 'message bot';
    if (isLoading) div.id = 'loading-' + Date.now();

    // Main Answer
    const answerEl = document.createElement('div');
    answerEl.className = 'answer-text';
    answerEl.innerText = text;
    div.appendChild(answerEl);

    // Intelligence Dropdown
    if (intelligence && (intelligence.confidence_metrics || intelligence.mappings || intelligence.sources)) {
        const container = document.createElement('div');
        container.className = 'intelligence-container';

        const toggle = document.createElement('div');
        toggle.className = 'intelligence-toggle';
        toggle.innerHTML = '<i class="fa-solid fa-chevron-down"></i> Intelligence Details';

        const details = document.createElement('div');
        details.className = 'intelligence-details';

        let detailsHtml = '';

        // Metrics
        if (intelligence.confidence_metrics) {
            const m = intelligence.confidence_metrics;
            detailsHtml += `
                <div style="margin-bottom: 1rem;">
                    <strong>System Confidence: ${Math.round(m.final_confidence * 100)}%</strong>
                    <div style="display: flex; gap: 10px; margin-top: 5px;">
                        <span style="font-size: 0.8rem; opacity: 0.8;">Schema: ${Math.round(m.schema_score * 100)}%</span>
                        <span style="font-size: 0.8rem; opacity: 0.8;">Vector: ${Math.round(m.semantic_score * 100)}%</span>
                    </div>
                </div>
            `;
        }

        // Mappings
        if (intelligence.mappings && intelligence.mappings.length > 0) {
            detailsHtml += '<div style="margin-bottom: 1rem;"><strong>Mapped Fields:</strong>';
            intelligence.mappings.forEach(map => {
                detailsHtml += `<div style="margin-top: 3px;">• ${map.field} (${Math.round(map.confidence * 100)}% match)</div>`;
            });
            detailsHtml += '</div>';
        }

        // Sources
        if (intelligence.sources && intelligence.sources.length > 0) {
            detailsHtml += '<div><strong>Top Sources:</strong>';
            intelligence.sources.slice(0, 3).forEach(s => {
                detailsHtml += `<div style="margin-top: 3px;">• Page ${s.metadata.page_number} (${s.metadata.section_type})</div>`;
            });
            detailsHtml += '</div>';
        }

        details.innerHTML = detailsHtml;

        toggle.onclick = () => {
            toggle.classList.toggle('active');
            details.classList.toggle('show');
        };

        container.appendChild(toggle);
        container.appendChild(details);
        div.appendChild(container);
    }

    chatMessages.appendChild(div);
    scrollToBottom();
    return div.id;
}

function removeMessage(id) {
    if (id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Extraction Handling
extractBtn.addEventListener('click', async () => {
    if (!currentDocId) return;

    let schema;
    try {
        schema = JSON.parse(schemaInput.value);
    } catch (e) {
        alert('Invalid JSON schema');
        return;
    }

    extractionOutput.textContent = 'Extracting... This may take a moment.';

    try {
        const response = await fetch('/extract', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                document_id: currentDocId,
                schema_definition: schema
            })
        });

        const data = await response.json();
        extractionOutput.textContent = JSON.stringify(data, null, 2);

    } catch (error) {
        extractionOutput.textContent = 'Error during extraction: ' + error.message;
    }
});

// Auto-Schema Generation
autoSchemaBtn.addEventListener('click', async () => {
    if (!currentDocId) return;

    // UI Feedback
    const originalText = autoSchemaBtn.innerHTML;
    autoSchemaBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating...';
    autoSchemaBtn.disabled = true;

    try {
        const response = await fetch('/propose_schema', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                document_id: currentDocId
            })
        });

        if (!response.ok) throw new Error('Failed to generate schema');

        const schema = await response.json();
        schemaInput.value = JSON.stringify(schema, null, 2);

        addBotMessage("I've generated a schema based on the document. You can review and edit it in the Extraction tab.");

    } catch (error) {
        console.error(error);
        alert('Failed to auto-generate schema: ' + error.message);
    } finally {
        autoSchemaBtn.innerHTML = originalText;
        autoSchemaBtn.disabled = false;
    }
});

function renderChunks(chunks) {
    const list = document.getElementById('chunksList');
    list.innerHTML = '';

    if (!chunks || chunks.length === 0) {
        list.innerHTML = '<div style="color: var(--text-secondary); text-align: center; margin-top: 2rem;">No chunks found.</div>';
        return;
    }

    chunks.forEach((chunk, index) => {
        const item = document.createElement('div');
        item.className = 'chunk-card';

        // chunk.section_type might be null if not set
        const type = chunk.metadata?.section_type || chunk.section_type || 'misc';
        const pageNum = chunk.metadata?.page_number || chunk.page_number || '?';

        item.innerHTML = `
            <div class="chunk-meta">
                <span>${type}</span>
                <span>Page ${pageNum} • Chunk ${index + 1}</span>
            </div>
            <div style="font-size: 0.95rem; white-space: pre-wrap; color: var(--text-primary);">${chunk.text || chunk.page_content || ''}</div>
        `;
        list.appendChild(item);
    });
}
