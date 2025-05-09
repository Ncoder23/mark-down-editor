document.addEventListener('DOMContentLoaded', function() {
    const markdownInput = document.getElementById('markdown-input');
    const outputContent = document.getElementById('output-content');
    const exportBtn = document.getElementById('export-btn');
    const copyBtn = document.getElementById('copy-btn');
    const pdfNotice = document.getElementById('pdf-notice');

    // Show PDF notice by default
    pdfNotice.style.display = 'block';
    
    // Hide notice after 10 seconds
    setTimeout(() => {
        if (pdfNotice.style.display !== 'none') {
            pdfNotice.style.opacity = '0.7';
        }
    }, 10000);

    // Function to render markdownx
    function renderMarkdown() {
        try {
            const markdownText = markdownInput.value;
            const html = marked.parse(markdownText);
            outputContent.innerHTML = html;
        } catch (error) {
            console.error('Error rendering markdown:', error);
            outputContent.innerHTML = '<p style="color: red;">Error rendering markdown</p>';
        }
    }

    // Initial render with sample text
    markdownInput.value = "# Welcome to Markdown Editor\n\nThis is a **real-time** markdown editor.\n\n## Features\n\n- Type markdown on the left\n- See rendered output on the right\n- Export as PDF\n- Copy to clipboard\n\n```python\nprint('Hello, world!')\n```";
    renderMarkdown();

    // Real-time rendering
    markdownInput.addEventListener('input', renderMarkdown);

    // Export functionality
    exportBtn.addEventListener('click', function() {
        const htmlContent = outputContent.innerHTML;
        
        // Show loading indicator
        const loadingIndicator = document.createElement('div');
        loadingIndicator.id = 'loading-indicator';
        loadingIndicator.innerHTML = 'Generating PDF...';
        document.body.appendChild(loadingIndicator);
        
        // Use relative URL in production
        const baseUrl = '';
        
        fetch(baseUrl + '/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/pdf,text/html'
            },
            body: JSON.stringify({ html: htmlContent }),
            credentials: 'same-origin'
        })
        .then(response => {
            // Remove loading indicator
            document.body.removeChild(loadingIndicator);
            
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.status);
            }
            
            // Check if the response is PDF or HTML
            const contentType = response.headers.get('Content-Type');
            const filename = contentType.includes('pdf') ? 'rendered.pdf' : 'rendered.html';
            
            return {
                blob: response.blob(),
                filename: filename
            };
        })
        .then(data => {
            return data.blob.then(blob => {
                return {
                    blob: blob,
                    filename: data.filename
                };
            });
        })
        .then(data => {
            const url = window.URL.createObjectURL(data.blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = data.filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            
            if (data.filename.endsWith('.html')) {
                // Show the PDF notice if HTML was downloaded instead of PDF
                pdfNotice.style.display = 'block';
                pdfNotice.style.opacity = '1';
                alert('PDF generation is not available. HTML file has been downloaded instead.');
            }
        })
        .catch(error => {
            // Remove loading indicator if still present
            if (document.getElementById('loading-indicator')) {
                document.body.removeChild(loadingIndicator);
            }
            
            console.error('Error exporting document:', error);
            alert('Error exporting document: ' + error.message + '\nCheck console for details.');
        });
    });

    // Copy functionality
    copyBtn.addEventListener('click', function() {
        const range = document.createRange();
        range.selectNode(outputContent);
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);
        
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                alert('Copied to clipboard!');
            } else {
                alert('Unable to copy');
            }
        } catch (err) {
            console.error('Error copying text:', err);
            alert('Error copying text');
        }
        
        window.getSelection().removeAllRanges();
    });
}); 