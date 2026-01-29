document.addEventListener("DOMContentLoaded", () => {
    const API = "http://127.0.0.1:8000";

    // --- DOM Elements ---
    const chatWindow = document.getElementById("chat-window");
    const chatForm = document.getElementById("chat-form");
    const messageInput = document.getElementById("message-input");
    const ragToggle = document.getElementById("rag-toggle");
    const uploadBtn = document.getElementById("upload_btn");
    const pdfFileInput = document.getElementById("pdf_file");
    const uploadStatus = document.getElementById("upload_status");

    // --- State Management ---
    let messages = [
        { role: 'assistant', content: 'Hello! Ask me anything, or upload a PDF to ask questions about a specific document.' }
    ];

    // --- Functions ---

    /**
     * Renders a single message object to the chat window.
     * @param {object} message - The message object { role, content }.
     */
    function displayMessage(message) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", message.role);
        
        const paragraph = document.createElement("p");
        paragraph.textContent = message.content;
        messageDiv.appendChild(paragraph);

        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
    
    /**
     * Handles the chat form submission.
     * @param {Event} e - The form submission event.
     */
    async function handleChatSubmit(e) {
        e.preventDefault();
        const userInput = messageInput.value.trim();
        if (!userInput) return;

        // 1. Add user message to state and display it
        const userMessage = { role: 'user', content: userInput };
        messages.push(userMessage);
        displayMessage(userMessage);
        
        messageInput.value = "";
        chatForm.querySelector("button").disabled = true;

        // 2. Display loading indicator
        const loadingDiv = document.createElement("div");
        loadingDiv.classList.add("message", "assistant", "loading");
        loadingDiv.innerHTML = "<p>...</p>";
        chatWindow.appendChild(loadingDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;

        try {
            // 3. Send history to backend
            const response = await fetch(`${API}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    history: messages,
                    use_rag: ragToggle.checked
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            
            // 4. Add assistant response to state and display it
            const assistantMessage = { role: 'assistant', content: data.answer };
            messages.push(assistantMessage);
            displayMessage(assistantMessage);

        } catch (error) {
            displayMessage({ role: 'assistant', content: `Sorry, an error occurred: ${error.message}` });
        } finally {
            // 5. Clean up
            chatWindow.removeChild(loadingDiv);
            chatForm.querySelector("button").disabled = false;
            messageInput.focus();
        }
    }
    
    /**
     * Handles the PDF upload process.
     */
    async function uploadPDF() {
        const file = pdfFileInput.files[0];
        if (!file) {
            uploadStatus.innerText = "Please select a PDF file first.";
            uploadStatus.className = 'status error';
            setTimeout(() => { uploadStatus.innerText = ''; uploadStatus.className = 'status'; }, 5000);
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        uploadStatus.innerText = "Processing PDF... this may take a moment.";
        uploadStatus.className = 'status';
        uploadBtn.disabled = true;

        try {
            const response = await fetch(`${API}/upload_pdf`, {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            uploadStatus.innerText = data.message;
            uploadStatus.classList.add('success');

        } catch (error) {
            uploadStatus.innerText = `Error: ${error.message}`;
            uploadStatus.classList.add('error');
        } finally {
            uploadBtn.disabled = false;
            pdfFileInput.value = ""; // Clear the file input
            setTimeout(() => { 
                uploadStatus.innerText = ''; 
                uploadStatus.className = 'status';
            }, 5000); // Clear status after 5 seconds
        }
    }

    // --- Initial Setup ---
    chatForm.addEventListener("submit", handleChatSubmit);
    uploadBtn.addEventListener("click", uploadPDF);
    
    // Clear initial placeholder message before rendering history
    chatWindow.innerHTML = ''; 
    messages.forEach(displayMessage);
});
