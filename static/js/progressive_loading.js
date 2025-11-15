/**
 * Progressive Loading Module for HAMMER-API
 * ===========================================
 *
 * Provides reusable functionality for Server-Sent Events (SSE) based
 * progressive loading with visual feedback and error handling.
 *
 * Features:
 * - SSE connection management with automatic reconnection
 * - Progress bar updates with smooth animations
 * - Status message display
 * - Error handling with retry capability
 * - Browser compatibility detection
 * - Graceful degradation fallback
 *
 * @version 1.0.0
 * @author HAMMER-API Team
 */

(function(window) {
    'use strict';

    /**
     * ProgressiveLoader class
     * Manages SSE connection and UI updates for progressive form submission
     */
    class ProgressiveLoader {
        /**
         * Initialize ProgressiveLoader
         *
         * @param {Object} options - Configuration options
         * @param {string} options.formSelector - CSS selector for form element
         * @param {string} options.submitUrl - URL for SSE endpoint
         * @param {string} options.fallbackUrl - URL for traditional form submission
         * @param {Function} options.onComplete - Callback when submission completes
         * @param {Function} options.onError - Callback when error occurs
         * @param {boolean} options.enableAutoRetry - Enable automatic retry on connection failure
         */
        constructor(options) {
            this.options = {
                formSelector: '#submit-form',
                submitUrl: '/submit-stream',
                fallbackUrl: '/submit',
                onComplete: null,
                onError: null,
                enableAutoRetry: false,
                retryDelay: 3000,
                maxRetries: 3,
                ...options
            };

            this.form = document.querySelector(this.options.formSelector);
            this.eventSource = null;
            this.retryCount = 0;
            this.isSubmitting = false;

            // UI elements (created dynamically)
            this.progressContainer = null;
            this.progressBar = null;
            this.progressText = null;
            this.statusMessage = null;
            this.errorContainer = null;

            this.init();
        }

        /**
         * Initialize the loader
         */
        init() {
            if (!this.form) {
                console.warn('[ProgressiveLoader] Form not found:', this.options.formSelector);
                return;
            }

            // Check browser compatibility
            if (!this.checkCompatibility()) {
                console.warn('[ProgressiveLoader] Browser does not support SSE, using fallback');
                return;
            }

            // Create UI elements
            this.createUI();

            // Attach form submit handler
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));

            console.log('[ProgressiveLoader] Initialized successfully');
        }

        /**
         * Check if browser supports Server-Sent Events
         *
         * @returns {boolean} True if SSE is supported
         */
        checkCompatibility() {
            return typeof(EventSource) !== 'undefined';
        }

        /**
         * Create UI elements for progress display
         */
        createUI() {
            // Create progress container
            this.progressContainer = document.createElement('div');
            this.progressContainer.id = 'progressive-loading-container';
            this.progressContainer.style.display = 'none';
            this.progressContainer.setAttribute('role', 'status');
            this.progressContainer.setAttribute('aria-live', 'polite');
            this.progressContainer.setAttribute('aria-atomic', 'true');

            // Progress bar wrapper
            const progressWrapper = document.createElement('div');
            progressWrapper.className = 'progress-wrapper';

            // Progress bar
            this.progressBar = document.createElement('div');
            this.progressBar.className = 'progress-bar';
            this.progressBar.setAttribute('role', 'progressbar');
            this.progressBar.setAttribute('aria-valuemin', '0');
            this.progressBar.setAttribute('aria-valuemax', '100');
            this.progressBar.setAttribute('aria-valuenow', '0');

            progressWrapper.appendChild(this.progressBar);

            // Progress text (percentage)
            this.progressText = document.createElement('div');
            this.progressText.className = 'progress-text';
            this.progressText.textContent = '0%';

            // Status message
            this.statusMessage = document.createElement('div');
            this.statusMessage.className = 'status-message';
            this.statusMessage.textContent = 'Preparing submission...';

            // Error container
            this.errorContainer = document.createElement('div');
            this.errorContainer.className = 'error-message';
            this.errorContainer.style.display = 'none';
            this.errorContainer.setAttribute('role', 'alert');

            // Assemble UI
            this.progressContainer.appendChild(this.statusMessage);
            this.progressContainer.appendChild(progressWrapper);
            this.progressContainer.appendChild(this.progressText);
            this.progressContainer.appendChild(this.errorContainer);

            // Insert before form
            this.form.parentNode.insertBefore(this.progressContainer, this.form);

            console.log('[ProgressiveLoader] UI elements created');
        }

        /**
         * Handle form submission
         *
         * @param {Event} e - Submit event
         */
        handleSubmit(e) {
            e.preventDefault();

            if (this.isSubmitting) {
                console.warn('[ProgressiveLoader] Submission already in progress');
                return;
            }

            // Get form data
            const formData = new FormData(this.form);

            // Show confirmation dialog
            const imeiText = formData.get('imei').trim();
            const imeiLines = imeiText.split('\n').filter(line => line.trim().length > 0);
            const count = imeiLines.length;
            const plural = count === 1 ? 'IMEI' : 'IMEIs';

            const serviceSelect = this.form.querySelector('[name="service_id"]');
            const serviceName = serviceSelect.options[serviceSelect.selectedIndex].text;

            if (!confirm(`Submit ${count} ${plural} for service:\n${serviceName}\n\nContinue?`)) {
                return;
            }

            // Start submission
            this.startSubmission(formData);
        }

        /**
         * Start SSE-based submission
         *
         * @param {FormData} formData - Form data to submit
         */
        startSubmission(formData) {
            this.isSubmitting = true;
            this.retryCount = 0;

            // Hide form, show progress
            this.form.style.display = 'none';
            this.progressContainer.style.display = 'block';
            this.errorContainer.style.display = 'none';

            console.log('[ProgressiveLoader] Starting SSE submission');

            // Convert FormData to URL-encoded string for EventSource
            // EventSource only supports GET, so we use fetch with SSE
            this.submitWithSSE(formData);
        }

        /**
         * Submit form using fetch with SSE
         *
         * @param {FormData} formData - Form data
         */
        async submitWithSSE(formData) {
            try {
                const response = await fetch(this.options.submitUrl, {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                // Read stream
                while (true) {
                    const {done, value} = await reader.read();

                    if (done) {
                        console.log('[ProgressiveLoader] Stream complete');
                        break;
                    }

                    // Decode chunk
                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\n');

                    // Process SSE events
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = line.substring(6);
                            try {
                                const event = JSON.parse(data);
                                this.handleEvent(event);
                            } catch (e) {
                                console.error('[ProgressiveLoader] Failed to parse event:', e);
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('[ProgressiveLoader] SSE error:', error);
                this.handleError('Connection error: ' + error.message);

                // Retry if enabled
                if (this.options.enableAutoRetry && this.retryCount < this.options.maxRetries) {
                    this.retryCount++;
                    console.log(`[ProgressiveLoader] Retrying (${this.retryCount}/${this.options.maxRetries})...`);
                    setTimeout(() => this.submitWithSSE(formData), this.options.retryDelay);
                }
            }
        }

        /**
         * Handle SSE event
         *
         * @param {Object} event - Event data
         */
        handleEvent(event) {
            console.log('[ProgressiveLoader] Event received:', event.type, event);

            switch (event.type) {
                case 'progress':
                    this.updateProgress(event.percent, event.message, event.warning);
                    break;

                case 'complete':
                    this.handleComplete(event);
                    break;

                case 'error':
                    this.handleError(event.message);
                    break;

                default:
                    console.warn('[ProgressiveLoader] Unknown event type:', event.type);
            }
        }

        /**
         * Update progress bar and message
         *
         * @param {number} percent - Progress percentage (0-100)
         * @param {string} message - Status message
         * @param {boolean} warning - Is this a warning message
         */
        updateProgress(percent, message, warning = false) {
            // Update progress bar
            this.progressBar.style.width = percent + '%';
            this.progressBar.setAttribute('aria-valuenow', percent);

            // Update text
            this.progressText.textContent = Math.round(percent) + '%';

            // Update message
            this.statusMessage.textContent = message;

            // Apply warning style if needed
            if (warning) {
                this.statusMessage.style.color = '#F9A825';
            } else {
                this.statusMessage.style.color = '';
            }

            console.log(`[ProgressiveLoader] Progress: ${percent}% - ${message}`);
        }

        /**
         * Handle successful completion
         *
         * @param {Object} event - Completion event data
         */
        handleComplete(event) {
            console.log('[ProgressiveLoader] Submission complete:', event);

            // Update to 100%
            this.updateProgress(100, event.message);

            // Show stats if available
            if (event.stats) {
                const statsMsg = `Completed in ${event.stats.duration}s: ${event.stats.successful} successful, ${event.stats.duplicates} duplicates, ${event.stats.errors} errors`;
                this.statusMessage.textContent += ` (${statsMsg})`;
            }

            // Call callback
            if (this.options.onComplete) {
                this.options.onComplete(event);
            }

            // Redirect after delay
            setTimeout(() => {
                if (event.redirect) {
                    window.location.href = event.redirect;
                }
            }, 1500);
        }

        /**
         * Handle error
         *
         * @param {string} message - Error message
         */
        handleError(message) {
            console.error('[ProgressiveLoader] Error:', message);

            this.isSubmitting = false;

            // Show error
            this.errorContainer.textContent = message;
            this.errorContainer.style.display = 'block';

            // Update status
            this.statusMessage.textContent = 'Submission failed';
            this.statusMessage.style.color = '#C62828';

            // Call callback
            if (this.options.onError) {
                this.options.onError(message);
            }

            // Show retry button
            this.showRetryButton();
        }

        /**
         * Show retry button in error container
         */
        showRetryButton() {
            const retryBtn = document.createElement('button');
            retryBtn.textContent = 'Retry Submission';
            retryBtn.className = 'btn btn-secondary';
            retryBtn.style.marginTop = '15px';
            retryBtn.onclick = () => {
                this.errorContainer.style.display = 'none';
                this.form.style.display = 'block';
                this.progressContainer.style.display = 'none';
                this.isSubmitting = false;
            };

            this.errorContainer.appendChild(retryBtn);
        }

        /**
         * Reset loader state
         */
        reset() {
            this.isSubmitting = false;
            this.retryCount = 0;
            this.form.style.display = 'block';
            this.progressContainer.style.display = 'none';
            this.errorContainer.style.display = 'none';
            this.updateProgress(0, 'Preparing submission...');
        }
    }

    // Export to global scope
    window.ProgressiveLoader = ProgressiveLoader;

    console.log('[ProgressiveLoader] Module loaded');

})(window);
