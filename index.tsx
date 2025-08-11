/**
 * Complete Frontend for GraphRAG Integration
 * Replace your entire index.tsx with this code
 */

import * as pdfjsLib from 'pdfjs-dist';

// Configure the PDF.js worker to enable PDF parsing
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://esm.sh/pdfjs-dist@4.4.168/build/pdf.worker.mjs';

// --- DOM Element References ---
const articleInput = document.getElementById('article-input') as HTMLTextAreaElement;
const processButton = document.getElementById('process-button') as HTMLButtonElement;
const knowledgeBaseContainer = document.getElementById('knowledge-base-container') as HTMLElement;
const knowledgeList = document.getElementById('knowledge-list') as HTMLElement;
const fileInput = document.getElementById('file-input') as HTMLInputElement;
const fileNameDisplay = document.getElementById('file-name-display') as HTMLSpanElement;

// Literature Review Section
const literatureReviewSection = document.getElementById('literature-review-section') as HTMLElement;
const reviewForm = document.getElementById('review-form') as HTMLFormElement;
const reviewTopicInput = document.getElementById('review-topic-input') as HTMLInputElement;
const generateReviewButton = document.getElementById('generate-review-button') as HTMLButtonElement;
const reviewGenerationProgress = document.getElementById('review-generation-progress') as HTMLElement;
const reviewProgressLog = document.getElementById('review-progress-log') as HTMLElement;
const reviewDraftOutput = document.getElementById('review-draft-output') as HTMLElement;
const draftVersionControls = document.getElementById('draft-version-controls') as HTMLElement;

// Writing Assistant Section
const writingAssistantSection = document.getElementById('writing-assistant-section') as HTMLElement;
const writingEditor = document.getElementById('writing-editor') as HTMLElement;
const analyzeTextButton = document.getElementById('analyze-text-button') as HTMLButtonElement;
const suggestionsPanel = document.getElementById('suggestions-panel') as HTMLElement;
const similarityCheckButton = document.getElementById('similarity-check-button') as HTMLButtonElement;
const referencesContainer = document.getElementById('references-container') as HTMLElement;
const referencesList = document.getElementById('references-list') as HTMLElement;

// Q&A Section
const qaSection = document.getElementById('qa-section') as HTMLElement;
const chatContainer = document.getElementById('chat-container') as HTMLElement;
const chatForm = document.getElementById('chat-form') as HTMLFormElement;
const questionInput = document.getElementById('question-input') as HTMLInputElement;
const chatButton = chatForm.querySelector('button') as HTMLButtonElement;

const loader = document.getElementById('loader') as HTMLElement;
const loaderText = loader.querySelector('p') as HTMLParagraphElement;

// --- App State ---
interface GraphRAGDocument {
    filename: string;
    path: string;
    chunks: number;
    processed_at: string;
}

let isLoading = false;
let documents: GraphRAGDocument[] = [];
let currentFileName = '';
let draftHistory: string[] = [];

// GraphRAG API base URL
const API_BASE = '/api';

/**
 * Updates the UI based on the loading state.
 */
function setLoading(loading: boolean, text = 'Processing...') {
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
async function apiCall(endpoint: string, method: string = 'GET', data?: any) {
    const options: RequestInit = {
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
 * Handles file selection and processing
 */
async function handleFileSelect(event: Event) {
    const input = event.target as HTMLInputElement;
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
            if (file.type === 'application/pdf') {
                const arrayBuffer = await file.arrayBuffer();
                const pdf = await (pdfjsLib.getDocument(arrayBuffer).promise as Promise<any>);
                for (let i = 1; i <= pdf.numPages; i++) {
                    const page = await pdf.getPage(i);
                    const textContent = await page.getTextContent();
                    fullText += textContent.items.map((item: any) => item.str ?? '').join(' ') + '\n\n';
                }
            } else {
                fullText = await file.text();
            }
            articleInput.value = fullText.trim();
        } catch (error) {
            console.error('Error processing file:', error);
            fileNameDisplay.textContent = 'Error processing file.';
            currentFileName = '';
            alert(`Error processing ${file.name}.`);
        } finally {
            setLoading(false);
        }
    } else {
        // Handle multiple files
        const fileNames = Array.from(files).map(f => f.name).join(', ');
        fileNameDisplay.textContent = `Processing ${files.length} files...`;
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            setLoading(true, `Processing ${i + 1}/${files.length}: ${file.name}`);

            try {
                let fullText = '';
                if (file.type === 'application/pdf') {
                    const arrayBuffer = await file.arrayBuffer();
                    const pdf = await (pdfjsLib.getDocument(arrayBuffer).promise as Promise<any>);
                    for (let j = 1; j <= pdf.numPages; j++) {
                        const page = await pdf.getPage(j);
                        const textContent = await page.getTextContent();
                        fullText += textContent.items.map((item: any) => item.str ?? '').join(' ') + '\n\n';
                    }
                } else {
                    fullText = await file.text();
                }
                
                await apiCall('/add_document', 'POST', {
                    content: fullText.trim(),
                    filename: file.name
                });

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
async function handleGenerateReview(event: SubmitEvent) {
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
        const reviewLength = (document.querySelector('input[name="review-length"]:checked') as HTMLInputElement).value;
        
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

function addProgressLog(html: string) {
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
async function handleAskQuestion(event: SubmitEvent) {
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

function addMessageToChat(text: string, sender: 'user' | 'model') {
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
    const target = event.target as HTMLElement;
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
document.querySelector('.editor-toolbar')?.addEventListener('click', (e) => {
    const target = e.target as HTMLElement;
    const button = target.closest('button');
    if (button && button.dataset.command) {
        document.execCommand(button.dataset.command, false);
        writingEditor.focus();
    }
});

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
        alert('Could not connect to GraphRAG system. Make sure the backend is running on port 5000.');
    } finally {
        setLoading(false);
    }
}

// Start the app
initializeApp();