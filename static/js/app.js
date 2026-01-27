/**
 * MasterFlow - App Dashboard JavaScript
 * Handles file upload, mastering settings, and API interactions
 */

class MasterFlowApp {
    constructor() {
        this.currentTrack = null;
        this.currentJob = null;
        this.settings = {
            preset: 'balanced',
            genre: '',
            targetLufs: -14,
            outputFormat: 'wav',
            eqLow: 0,
            eqMid: 0,
            eqHigh: 0,
            stereoWidth: 1
        };

        this.init();
    }

    init() {
        this.bindElements();
        this.bindEvents();
        console.log('🎵 MasterFlow App initialized');
    }

    bindElements() {
        // Upload
        this.uploadZone = document.getElementById('uploadZone');
        this.fileInput = document.getElementById('fileInput');

        // Sections
        this.trackSection = document.getElementById('trackSection');
        this.settingsSection = document.getElementById('settingsSection');
        this.processingSection = document.getElementById('processingSection');
        this.resultsSection = document.getElementById('resultsSection');

        // Track info
        this.trackTitle = document.getElementById('trackTitle');
        this.trackDuration = document.getElementById('trackDuration');
        this.trackSampleRate = document.getElementById('trackSampleRate');
        this.trackChannels = document.getElementById('trackChannels');

        // Analysis
        this.analysisLufs = document.getElementById('analysisLufs');
        this.analysisPeak = document.getElementById('analysisPeak');
        this.analysisDR = document.getElementById('analysisDR');
        this.analysisBalance = document.getElementById('analysisBalance');
        this.recommendationText = document.getElementById('recommendationText');

        // Settings
        this.genreSelect = document.getElementById('genreSelect');
        this.lufsSlider = document.getElementById('lufsSlider');
        this.lufsValue = document.getElementById('lufsValue');
        this.advancedToggle = document.getElementById('advancedToggle');
        this.advancedSettings = document.getElementById('advancedSettings');

        // EQ
        this.eqLow = document.getElementById('eqLow');
        this.eqMid = document.getElementById('eqMid');
        this.eqHigh = document.getElementById('eqHigh');
        this.eqLowValue = document.getElementById('eqLowValue');
        this.eqMidValue = document.getElementById('eqMidValue');
        this.eqHighValue = document.getElementById('eqHighValue');
        this.stereoWidth = document.getElementById('stereoWidth');
        this.stereoWidthValue = document.getElementById('stereoWidthValue');

        // Buttons
        this.masterBtn = document.getElementById('masterBtn');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.newTrackBtn = document.getElementById('newTrackBtn');

        // Processing
        this.processingStatus = document.getElementById('processingStatus');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');

        // Results
        this.resultInputLufs = document.getElementById('resultInputLufs');
        this.resultOutputLufs = document.getElementById('resultOutputLufs');
        this.resultGain = document.getElementById('resultGain');
    }

    bindEvents() {
        // Upload zone
        if (this.uploadZone) {
            this.uploadZone.addEventListener('click', () => this.fileInput.click());
            this.uploadZone.addEventListener('dragover', (e) => this.handleDragOver(e));
            this.uploadZone.addEventListener('dragleave', (e) => this.handleDragLeave(e));
            this.uploadZone.addEventListener('drop', (e) => this.handleDrop(e));
        }

        if (this.fileInput) {
            this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }

        // Preset buttons
        document.querySelectorAll('.preset-btn').forEach(btn => {
            btn.addEventListener('click', () => this.selectPreset(btn));
        });

        // Genre select
        if (this.genreSelect) {
            this.genreSelect.addEventListener('change', (e) => {
                this.settings.genre = e.target.value;
            });
        }

        // Loudness buttons
        document.querySelectorAll('.loudness-btn').forEach(btn => {
            btn.addEventListener('click', () => this.selectLoudness(btn));
        });

        // LUFS slider
        if (this.lufsSlider) {
            this.lufsSlider.addEventListener('input', (e) => {
                this.settings.targetLufs = parseFloat(e.target.value);
                this.lufsValue.textContent = `${e.target.value} LUFS`;
                this.updateLoudnessButtons();
            });
        }

        // Format buttons
        document.querySelectorAll('.format-btn').forEach(btn => {
            btn.addEventListener('click', () => this.selectFormat(btn));
        });

        // Advanced toggle
        if (this.advancedToggle) {
            this.advancedToggle.addEventListener('click', () => this.toggleAdvanced());
        }

        // EQ sliders
        if (this.eqLow) {
            this.eqLow.addEventListener('input', (e) => {
                this.settings.eqLow = parseFloat(e.target.value);
                this.eqLowValue.textContent = `${e.target.value} dB`;
            });
        }
        if (this.eqMid) {
            this.eqMid.addEventListener('input', (e) => {
                this.settings.eqMid = parseFloat(e.target.value);
                this.eqMidValue.textContent = `${e.target.value} dB`;
            });
        }
        if (this.eqHigh) {
            this.eqHigh.addEventListener('input', (e) => {
                this.settings.eqHigh = parseFloat(e.target.value);
                this.eqHighValue.textContent = `${e.target.value} dB`;
            });
        }
        if (this.stereoWidth) {
            this.stereoWidth.addEventListener('input', (e) => {
                this.settings.stereoWidth = parseFloat(e.target.value);
                this.stereoWidthValue.textContent = `${Math.round(e.target.value * 100)}%`;
            });
        }

        // Master button
        if (this.masterBtn) {
            this.masterBtn.addEventListener('click', () => this.startMastering());
        }

        // Download button
        if (this.downloadBtn) {
            this.downloadBtn.addEventListener('click', () => this.downloadMaster());
        }

        // New track button
        if (this.newTrackBtn) {
            this.newTrackBtn.addEventListener('click', () => this.resetApp());
        }

        // Compare buttons
        document.querySelectorAll('.compare-btn').forEach(btn => {
            btn.addEventListener('click', () => this.switchCompare(btn));
        });

        // Play button
        const playBtn = document.getElementById('playBtn');
        if (playBtn) {
            playBtn.addEventListener('click', () => this.togglePlay());
        }
    }

    // Drag and drop handlers
    handleDragOver(e) {
        e.preventDefault();
        this.uploadZone.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.uploadZone.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        this.uploadZone.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    async processFile(file) {
        // Validate file type
        const validTypes = ['.wav', '.mp3', '.flac', '.aiff', '.ogg', '.m4a'];
        const ext = '.' + file.name.split('.').pop().toLowerCase();

        if (!validTypes.includes(ext)) {
            alert('Unsupported file format. Please upload a WAV, MP3, FLAC, AIFF, OGG, or M4A file.');
            return;
        }

        // Validate file size (500MB max)
        if (file.size > 500 * 1024 * 1024) {
            alert('File too large. Maximum size is 500MB.');
            return;
        }

        // Show loading state
        this.uploadZone.innerHTML = `
            <div class="upload-content">
                <div class="processing-ring" style="width:60px;height:60px;border-width:3px;margin:0 auto 16px;"></div>
                <h2>Uploading...</h2>
                <p>${file.name}</p>
            </div>
        `;

        try {
            // Create form data
            const formData = new FormData();
            formData.append('file', file);
            formData.append('title', file.name.replace(/\.[^/.]+$/, ''));

            // Upload file
            const response = await fetch('/api/v1/tracks/upload', {
                method: 'POST',
                body: formData,
                headers: {
                    'Authorization': 'Bearer demo-token' // In production, use real token
                }
            });

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const track = await response.json();
            this.currentTrack = track;

            // Update UI
            this.showTrackInfo(track, file);

            // Analyze track
            await this.analyzeTrack(track.id);

        } catch (error) {
            console.error('Upload error:', error);
            // For demo, simulate successful upload
            this.simulateUpload(file);
        }
    }

    simulateUpload(file) {
        // Simulate track data for demo
        this.currentTrack = {
            id: 1,
            original_filename: file.name,
            title: file.name.replace(/\.[^/.]+$/, ''),
            duration: 180 + Math.random() * 120,
            sample_rate: 44100,
            channels: 2,
            file_size: file.size
        };

        this.showTrackInfo(this.currentTrack, file);
        this.simulateAnalysis();
    }

    showTrackInfo(track, file) {
        // Hide upload, show track section
        this.uploadZone.style.display = 'none';
        this.trackSection.style.display = 'block';
        this.settingsSection.style.display = 'block';

        // Update track info
        this.trackTitle.textContent = track.title || file.name;
        this.trackDuration.textContent = this.formatDuration(track.duration || 180);
        this.trackSampleRate.textContent = `${(track.sample_rate || 44100) / 1000} kHz`;
        this.trackChannels.textContent = track.channels === 2 ? 'Stereo' : 'Mono';
    }

    async analyzeTrack(trackId) {
        try {
            const response = await fetch(`/api/v1/tracks/${trackId}/analyze`, {
                method: 'POST',
                headers: {
                    'Authorization': 'Bearer demo-token'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.updateAnalysis(data.analysis, data.recommendations);
            }
        } catch (error) {
            console.error('Analysis error:', error);
            this.simulateAnalysis();
        }
    }

    simulateAnalysis() {
        // Simulate analysis results
        const analysis = {
            lufs: -18.5 + Math.random() * 6,
            peak_db: -3.2 + Math.random() * 2,
            dynamic_range: 10 + Math.random() * 8,
            spectral_balance: ['Balanced', 'Bass-heavy', 'Bright'][Math.floor(Math.random() * 3)]
        };

        const recommendations = {
            preset: ['balanced', 'warm', 'bright', 'punchy'][Math.floor(Math.random() * 4)],
            target_lufs: -14
        };

        this.updateAnalysis(analysis, recommendations);
    }

    updateAnalysis(analysis, recommendations) {
        this.analysisLufs.textContent = `${analysis.lufs.toFixed(1)} LUFS`;
        this.analysisPeak.textContent = `${analysis.peak_db.toFixed(1)} dB`;
        this.analysisDR.textContent = `${analysis.dynamic_range.toFixed(1)} dB`;
        this.analysisBalance.textContent = analysis.spectral_balance;

        if (recommendations) {
            this.recommendationText.innerHTML = `Recommended preset: <strong>${recommendations.preset.charAt(0).toUpperCase() + recommendations.preset.slice(1)}</strong>`;

            // Auto-select recommended preset
            const presetBtn = document.querySelector(`[data-preset="${recommendations.preset}"]`);
            if (presetBtn) {
                this.selectPreset(presetBtn);
            }
        }
    }

    selectPreset(btn) {
        document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.settings.preset = btn.dataset.preset;
    }

    selectLoudness(btn) {
        document.querySelectorAll('.loudness-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const lufs = parseFloat(btn.dataset.lufs);
        this.settings.targetLufs = lufs;
        this.lufsSlider.value = lufs;
        this.lufsValue.textContent = `${lufs} LUFS`;
    }

    updateLoudnessButtons() {
        document.querySelectorAll('.loudness-btn').forEach(btn => {
            const lufs = parseFloat(btn.dataset.lufs);
            btn.classList.toggle('active', lufs === this.settings.targetLufs);
        });
    }

    selectFormat(btn) {
        document.querySelectorAll('.format-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.settings.outputFormat = btn.dataset.format;
    }

    toggleAdvanced() {
        const isOpen = this.advancedSettings.style.display !== 'none';
        this.advancedSettings.style.display = isOpen ? 'none' : 'block';
        this.advancedToggle.classList.toggle('open', !isOpen);
    }

    async startMastering() {
        if (!this.currentTrack) {
            alert('Please upload a track first');
            return;
        }

        // Show processing section
        this.trackSection.style.display = 'none';
        this.settingsSection.style.display = 'none';
        this.processingSection.style.display = 'block';

        // Simulate processing
        await this.simulateProcessing();
    }

    async simulateProcessing() {
        const stages = [
            { text: 'Analyzing audio...', progress: 10 },
            { text: 'Applying EQ...', progress: 25 },
            { text: 'Compressing dynamics...', progress: 45 },
            { text: 'Enhancing stereo image...', progress: 60 },
            { text: 'Normalizing loudness...', progress: 80 },
            { text: 'Applying final limiter...', progress: 90 },
            { text: 'Rendering output...', progress: 100 }
        ];

        for (const stage of stages) {
            this.processingStatus.textContent = stage.text;
            this.progressFill.style.width = `${stage.progress}%`;
            this.progressText.textContent = `${stage.progress}%`;
            await this.sleep(800 + Math.random() * 400);
        }

        // Show results
        this.showResults();
    }

    showResults() {
        this.processingSection.style.display = 'none';
        this.resultsSection.style.display = 'block';

        // Simulate results
        const inputLufs = -18.5 + Math.random() * 4;
        const outputLufs = this.settings.targetLufs;
        const gain = outputLufs - inputLufs;

        this.resultInputLufs.textContent = inputLufs.toFixed(1);
        this.resultOutputLufs.textContent = outputLufs.toFixed(1);
        this.resultGain.textContent = `${gain > 0 ? '+' : ''}${gain.toFixed(1)} dB`;

        this.currentJob = {
            id: 1,
            output_path: '/outputs/mastered.wav'
        };
    }

    switchCompare(btn) {
        document.querySelectorAll('.compare-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        // In production, switch audio source
    }

    togglePlay() {
        const playBtn = document.getElementById('playBtn');
        const isPlaying = playBtn.textContent === '⏸';
        playBtn.textContent = isPlaying ? '▶' : '⏸';
        // In production, control audio playback
    }

    downloadMaster() {
        if (this.currentJob) {
            // In production, trigger download from API
            alert('Download started! (Demo mode)');
        }
    }

    resetApp() {
        // Reset state
        this.currentTrack = null;
        this.currentJob = null;

        // Reset UI
        this.resultsSection.style.display = 'none';
        this.uploadZone.style.display = 'block';
        this.uploadZone.innerHTML = `
            <div class="upload-content">
                <div class="upload-icon">📁</div>
                <h2>Drop your track here</h2>
                <p>or click to browse</p>
                <p class="upload-formats">Supports WAV, MP3, FLAC, AIFF, OGG, M4A (up to 500MB)</p>
            </div>
        `;

        // Reset file input
        this.fileInput.value = '';
    }

    // Utility functions
    formatDuration(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    window.masterFlowApp = new MasterFlowApp();
});
