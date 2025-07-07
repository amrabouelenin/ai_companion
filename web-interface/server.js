/**
 * Simple Express server to serve the AI Companion web interface
 */

const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;

// Enable CORS for API requests
app.use(cors({
    origin: '*',  // In production, you might want to restrict this
    methods: ['GET', 'POST', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    credentials: true
}));

// Serve static files
app.use(express.static(__dirname));

// Send the main HTML file for all routes
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Start server
app.listen(PORT, () => {
    console.log(`Web interface server running on http://localhost:${PORT}`);
    console.log(`Make sure the AI Companion API is running on port 8000`);
});
