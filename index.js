/**
 * GraphRAG Frontend - Pure JavaScript Version
 * This is the TypeScript file converted to regular JavaScript
 */

// --- DOM Element References ---
const articleInput = document.getElementById('article-input');
const processButton = document.getElementById('process-button');
const knowledgeBaseContainer = document.getElementById('knowledge-base-container');
const knowledgeList = document.getElementById('knowledge-list');
const fileInput = document.getElementById('file-input');
const fileNameDisplay = document.getElementById('file-name-display');

// Literature Review Section
const literatureReviewSection = document.getElementById('literature-review-section');
const reviewForm = document.getElementById('review-form');
const reviewTopicInput = document.getElementById('review-topic-input');
const generateReviewButton = document.getElementById('generate-review-button');
const reviewGenerationProgress = document.getElementById('review-generation-progress');
const reviewProgressLog = document.getElementById('review-progress-log');
const reviewDraftOutput = document.getElementById('review-draft-output');
const draftVersionControls = document.getElementById('draft-version-controls');

// Writing Assistant Section
const writingAssistantSection = document.getElementById('writing-assistant-section');
const writingEditor = document.getElementById('writing-editor');
const analyzeTextButton = document.getElementById('analyze-text-button');
const suggestionsPanel = document.getElementById('suggestions-panel');
const similarityCheckButton = document.getElementById('similarity-check-button');
const referencesContainer = document.getElementById('references-container');
const referencesList = document.getElementById('references-list');

// Q&A Section
const qaSection = document.getElementById('qa-section');
const chatContainer = document.getElementById('chat-container');
const chatForm = document.getElementById('chat-form');
const questionInput = document.getElementById('question-input');
const chatButton = chatForm.querySelector('button');

const loader = document.getElementById('loader');
const loaderText = loader.querySelector('p');

// --- App State ---
let isLoading = false;
let documents = [];
let currentFileName = '';
let draftHistory = [];

// GraphRAG API base URL
const API_BASE = '/api';

/**
 * Updates the UI based on the loading state.
 */
function setLoading(loading, text = 'Processing...') {
    isLoading = loading;
    loader.classList.toggle('hidden', !loading);
    loaderText.textContent = text;
    processButton.disabled = loading || !articleInput.value;
    fileInput.disabled = loading;
    generateReviewButton.disabled = loading || documents.length === 0;
    analyzeTextButton.disabled = loading;
    similarityCheckButton.disabled = loading;
    questionInput.disabled = loading || documents.length === 0;
    chatButton.disabled = loading || documents.length === 0;
}

/**
 * Makes API calls to the GraphRAG backend
 */
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    const response = await fetch(`${API_BASE}${endpoint}`, options);
    
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
        throw new Error(errorData.message || `HTTP ${response.status}`);
    }
    
    return response.json();
}

/**
 * Check if GraphRAG system is ready
 */
async function checkSystemStatus() {
    try {
        const result = await apiCall('/status');
        console.log('✅ GraphRAG system status:', result);
        
        if (result.status === 'ready') {
            await loadDocuments();
            return true;
        }
        return false;
    } catch (error) {
        console.error('❌ System not ready:', error);
        return false;
    }
}

/**
 * Load the list of processed documents from GraphRAG
 */
async function loadDocuments() {
    try {
        const result = await apiCall('/documents');
        documents = result.documents || [];
        renderDocuments();
        
        // Enable sections if we have documents
        if (documents.length > 0) {
            questionInput.disabled = false;
            chatButton.disabled = false;
            generateReviewButton.disabled = false;
            qaSection.classList.remove('hidden');
            literatureReviewSection.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error loading documents:', error);
    }
}

/**
 * Renders the list of processed documents
 */
function renderDocuments() {
    knowledgeList.innerHTML = '';
    
    if (documents.length > 0) {
        knowledgeBaseContainer.classList.remove('hidden');
        literatureReviewSection.classList.remove('hidden');
        qaSection.classList.remove('hidden');
    }

    documents.forEach(doc => {
        const card = document.createElement('div');
        card.className = 'knowledge-source-card';
        card.innerHTML = `
            <h4>${doc.filename}</h4>
            <p><strong>Chunks:</strong> ${doc.chunks} | <strong>Processed:</strong> ${new Date(doc.processed_at).toLocaleString()}</p>
            <p><strong>Path:</strong> ${doc.path}</p>
        `;
        knowledgeList.appendChild(card);
    });
}

/**
 * Handles adding a document to the GraphRAG system
 */
async function handleProcessArticle() {
    const articleText = articleInput.value.trim();
    if (!articleText) {
        alert('Please paste text into the text area or upload a file.');
        return;
    }

    const docName = currentFileName || `Manual_Entry_${Date.now()}.txt`;
    
    setLoading(true, `Adding ${docName} to GraphRAG...`);

    try {
        const result = await apiCall('/add_document', 'POST', {
            content: articleText,
            filename: docName
        });

        console.log('✅ Document added:', result);

        // Reload the documents list
        await loadDocuments();

        // Clear inputs after successful processing
        articleInput.value = '';
        fileInput.value = '';
        fileNameDisplay.textContent = '';
        currentFileName = '';

        alert(`✅ Successfully added "${docName}" to GraphRAG system!`);

    } catch (error) {
        console.error('Error adding document:', error);
        alert(`❌ Error adding document: ${error.message}`);
    } finally {
        setLoading(false);
    }
}

/**
 * Handles file selection and processing - supports TXT, PDF, and DOCX
 */
async function handleFileSelect(event) {
    const input = event.target;
    const files = input.files;
    if (!files || files.length === 0) {
        fileNameDisplay.textContent = '';
        currentFileName = '';
        return;
    }
    
    if (files.length === 1) {
        const file = files[0];
        fileNameDisplay.textContent = `Selected: ${file.name}`;
        currentFileName = file.name;
        articleInput.value = '';

        setLoading(true, `Reading ${file.name}...`);
        try {
            let fullText = '';
            
            // Check file type
            const fileExtension = file.name.split('.').pop().toLowerCase();
            
            if (file.type === 'application/pdf' || fileExtension === 'pdf') {
                // For PDF files, read as base64 and send to backend
                const reader = new FileReader();
                const base64 = await new Promise((resolve, reject) => {
                    reader.onload = () => resolve(reader.result);
                    reader.onerror = reject;
                    reader.readAsDataURL(file);
                });
                
                // Send PDF to backend for processing
                const result = await apiCall('/add_document', 'POST', {
                    content: base64,
                    filename: file.name,
                    file_type: 'pdf'
                });
                
                alert(`✅ PDF file "${file.name}" uploaded successfully!`);
                await loadDocuments();
                fileInput.value = '';
                fileNameDisplay.textContent = '';
                currentFileName = '';
                setLoading(false);
                return;
                
            } else if (fileExtension === 'docx' || fileExtension === 'doc') {
                // For DOCX files, read as base64 and send to backend
                const reader = new FileReader();
                const base64 = await new Promise((resolve, reject) => {
                    reader.onload = () => resolve(reader.result);
                    reader.onerror = reject;
                    reader.readAsDataURL(file);
                });
                
                // Send DOCX to backend for processing
                const result = await apiCall('/add_document', 'POST', {
                    content: base64,
                    filename: file.name,
                    file_type: 'docx'
                });
                
                alert(`✅ Word document "${file.name}" uploaded successfully!`);
                await loadDocuments();
                fileInput.value = '';
                fileNameDisplay.textContent = '';
                currentFileName = '';
                setLoading(false);
                return;
                
            } else {
                // For text files, read normally
                fullText = await file.text();
            }
            
            articleInput.value = fullText.trim();
        } catch (error) {
            console.error('Error processing file:', error);
            fileNameDisplay.textContent = 'Error processing file.';
            currentFileName = '';
            alert(`Error processing ${file.name}: ${error.message}`);
        } finally {
            setLoading(false);
        }
    } else {
        // Handle multiple files
        fileNameDisplay.textContent = `Processing ${files.length} files...`;
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            setLoading(true, `Processing ${i + 1}/${files.length}: ${file.name}`);

            try {
                const fileExtension = file.name.split('.').pop().toLowerCase();
                
                if (fileExtension === 'pdf' || fileExtension === 'docx' || fileExtension === 'doc') {
                    // Handle binary files
                    const reader = new FileReader();
                    const base64 = await new Promise((resolve, reject) => {
                        reader.onload = () => resolve(reader.result);
                        reader.onerror = reject;
                        reader.readAsDataURL(file);
                    });
                    
                    await apiCall('/add_document', 'POST', {
                        content: base64,
                        filename: file.name,
                        file_type: fileExtension === 'pdf' ? 'pdf' : 'docx'
                    });
                } else {
                    // Handle text files
                    const fullText = await file.text();
                    await apiCall('/add_document', 'POST', {
                        content: fullText.trim(),
                        filename: file.name,
                        file_type: 'text'
                    });
                }

            } catch (error) {
                console.error(`Error processing file ${file.name}:`, error);
                alert(`Error processing ${file.name}. Continuing with next file.`);
            }
        }
        
        await loadDocuments();
        setLoading(false);
        fileNameDisplay.textContent = `${files.length} file(s) processed.`;
        fileInput.value = '';
    }
}

/**
 * Handles generating a literature review using GraphRAG
 */
async function handleGenerateReview(event) {
    event.preventDefault();
    const topic = reviewTopicInput.value.trim();
    if (!topic) return;

    if (documents.length === 0) {
        alert('Please add some documents first!');
        return;
    }

    reviewGenerationProgress.classList.remove('hidden');
    reviewProgressLog.innerHTML = '';
    reviewDraftOutput.innerHTML = '';
    draftVersionControls.innerHTML = '';
    draftHistory = [];

    setLoading(true, 'Generating literature review...');

    try {
        const reviewLengthInput = document.querySelector('input[name="review-length"]:checked');
        const reviewLength = reviewLengthInput ? reviewLengthInput.value : 'detailed';
        
        let prompt = '';
        if (reviewLength === 'detailed') {
            prompt = `Generate a comprehensive literature review on the topic: "${topic}". 
                     Structure it with:
                     1. Introduction (define the topic and scope)
                     2. Main body sections (compare and contrast the sources, identify themes)
                     3. Conclusion (summarize key findings and gaps)
                     Use academic writing style and include proper citations.`;
        } else {
            prompt = `Generate a concise literature review (1-2 paragraphs) on the topic: "${topic}". 
                     Compare and contrast the key findings from the sources and include citations.`;
        }

        addProgressLog('<strong>Step 1:</strong> Querying GraphRAG system...');
        
        const result = await apiCall('/query', 'POST', {
            question: prompt
        });

        addProgressLog('<strong>Step 2:</strong> Literature review generated!');
        
        const draft = result.answer;
        draftHistory.push(draft);
        reviewDraftOutput.innerHTML = draft.replace(/\n/g, '<br>');
        
        renderDraftViewer();

        // Copy to writing assistant
        writingEditor.innerHTML = draft.replace(/\n/g, '<br>');
        writingAssistantSection.classList.remove('hidden');

        addProgressLog('<strong>Complete!</strong> Review ready for editing in Writing Assistant.');

    } catch (error) {
        console.error('Error generating review:', error);
        addProgressLog(`❌ Error: ${error.message}`);
        alert('Error generating literature review.');
    } finally {
        setLoading(false);
    }
}

function addProgressLog(html) {
    reviewProgressLog.innerHTML += `<div class="log-entry">${html}</div>`;
    reviewProgressLog.scrollTop = reviewProgressLog.scrollHeight;
}

/**
 * Renders the draft history buttons
 */
function renderDraftViewer() {
    draftVersionControls.innerHTML = '';
    if (draftHistory.length === 0) return;

    draftHistory.forEach((_, index) => {
        const button = document.createElement('button');
        button.className = 'version-button';
        button.dataset.index = index.toString();
        button.textContent = index === 0 ? 'Draft' : `Version ${index + 1}`;
        
        if (index === draftHistory.length - 1) {
            button.classList.add('active');
        }
        
        draftVersionControls.appendChild(button);
    });
}

/**
 * Handles Q&A queries to GraphRAG
 */
async function handleAskQuestion(event) {
    event.preventDefault();
    const userQuestion = questionInput.value.trim();
    if (!userQuestion || isLoading || documents.length === 0) return;

    setLoading(true, 'Asking GraphRAG...');
    addMessageToChat(userQuestion, 'user');
    questionInput.value = '';

    try {
        const result = await apiCall('/query', 'POST', {
            question: userQuestion
        });
        
        addMessageToChat(result.answer, 'model');

    } catch (error) {
        console.error('Error asking question:', error);
        addMessageToChat(`Sorry, I encountered an error: ${error.message}`, 'model');
    } finally {
        setLoading(false);
        questionInput.focus();
    }
}

/**
 * Simple text analysis using GraphRAG
 */
async function handleAnalyzeText() {
    const text = writingEditor.innerText.trim();
    if (!text) {
        alert('Please write some text first.');
        return;
    }

    setLoading(true, 'Analyzing text...');
    suggestionsPanel.innerHTML = '<div class="placeholder">Analyzing...</div>';

    try {
        const result = await apiCall('/query', 'POST', {
            question: `Please analyze this text for grammar, style, and clarity issues. Provide specific suggestions for improvement:

"${text}"`
        });

        suggestionsPanel.innerHTML = `
            <div class="suggestion-card">
                <div class="suggestion-card-header">
                    <span class="suggestion-category Style">GraphRAG Analysis</span>
                </div>
                <div class="suggestion-body">
                    ${result.answer.replace(/\n/g, '<br>')}
                </div>
            </div>
        `;

    } catch (error) {
        console.error('Error analyzing text:', error);
        suggestionsPanel.innerHTML = '<div class="placeholder">Failed to analyze text.</div>';
    } finally {
        setLoading(false);
    }
}

/**
 * Similarity check using GraphRAG
 */
async function handleSimilarityCheck() {
    const text = writingEditor.innerText.trim();
    if (!text) {
        alert('Please write some text first.');
        return;
    }

    setLoading(true, 'Checking for similarity...');

    try {
        const result = await apiCall('/query', 'POST', {
            question: `Check if this text has any similarities to the documents in the knowledge base. Identify any potential plagiarism or very similar passages:

"${text}"`
        });

        alert(`Similarity Check Results:\n\n${result.answer}`);

    } catch (error) {
        console.error('Error checking similarity:', error);
        alert('Error during similarity check.');
    } finally {
        setLoading(false);
    }
}

function addMessageToChat(text, sender) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('chat-message', sender);
    messageElement.textContent = text;
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// --- Event Listeners ---
processButton.addEventListener('click', handleProcessArticle);
fileInput.addEventListener('change', handleFileSelect);
reviewForm.addEventListener('submit', handleGenerateReview);
analyzeTextButton.addEventListener('click', handleAnalyzeText);
similarityCheckButton.addEventListener('click', handleSimilarityCheck);
chatForm.addEventListener('submit', handleAskQuestion);

// Version control for drafts
draftVersionControls.addEventListener('click', (event) => {
    const target = event.target;
    if (!target.classList.contains('version-button')) return;

    // Remove active class from all buttons
    const buttons = draftVersionControls.querySelectorAll('.version-button');
    buttons.forEach(btn => btn.classList.remove('active'));

    // Add active class to clicked button
    target.classList.add('active');

    const index = parseInt(target.dataset.index || '0');
    const draftText = draftHistory[index] || 'Could not load this version.';
    reviewDraftOutput.innerHTML = draftText.replace(/\n/g, '<br>');
});

// Simple toolbar for writing editor
const editorToolbar = document.querySelector('.editor-toolbar');
if (editorToolbar) {
    editorToolbar.addEventListener('click', (e) => {
        const target = e.target;
        const button = target.closest('button');
        if (button && button.dataset.command) {
            document.execCommand(button.dataset.command, false);
            writingEditor.focus();
        }
    });
}

// --- Initialize App ---
async function initializeApp() {
    console.log('🚀 Initializing GraphRAG Frontend...');
    setLoading(true, 'Connecting to GraphRAG system...');
    
    try {
        const isReady = await checkSystemStatus();
        if (isReady) {
            console.log('✅ GraphRAG system is ready!');
        } else {
            console.log('⚠️  GraphRAG system not ready, but you can still add documents');
        }
    } catch (error) {
        console.error('❌ Error connecting to GraphRAG:', error);
        alert('Could not connect to GraphRAG system. Make sure the backend is running on port 5001.');
    } finally {
        setLoading(false);
    }
}

// Start the app
initializeApp();