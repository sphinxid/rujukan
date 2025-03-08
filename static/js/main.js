// Main JavaScript file for Pastebin application

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    if (flashMessages.length > 0) {
        setTimeout(function() {
            flashMessages.forEach(function(message) {
                message.style.opacity = '0';
                setTimeout(function() {
                    message.style.display = 'none';
                }, 300);
            });
        }, 5000);
    }

    // Add line highlighting on paste view
    const codeLines = document.querySelectorAll('.code-line');
    if (codeLines.length > 0) {
        codeLines.forEach(function(line) {
            line.addEventListener('mouseenter', function() {
                this.style.backgroundColor = '#f0f0f0';
            });
            line.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });
    }

    // Add copy functionality for paste content
    const viewContainer = document.querySelector('.paste-view-container');
    if (viewContainer) {
        // Create copy button
        const copyBtn = document.createElement('button');
        copyBtn.className = 'btn btn-secondary';
        copyBtn.textContent = 'Copy to Clipboard';
        copyBtn.style.marginLeft = '10px';
        
        // Insert button into view options
        const viewOptions = document.querySelector('.view-options');
        if (viewOptions) {
            viewOptions.appendChild(copyBtn);
            
            // Add click event
            copyBtn.addEventListener('click', function() {
                const content = Array.from(document.querySelectorAll('.line-content'))
                    .map(line => line.textContent)
                    .join('\n');
                
                navigator.clipboard.writeText(content).then(function() {
                    copyBtn.textContent = 'Copied!';
                    setTimeout(function() {
                        copyBtn.textContent = 'Copy to Clipboard';
                    }, 2000);
                }).catch(function(err) {
                    console.error('Could not copy text: ', err);
                });
            });
        }
    }
});
