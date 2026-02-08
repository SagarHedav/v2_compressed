const express = require('express');
const dotenv = require('dotenv');
const cors = require('cors');
const helmet = require('helmet');
const { initializeFirebase } = require('./config/db');

// Load env vars
dotenv.config();

// Initialize Firebase
initializeFirebase();

const app = express();

// Middleware
app.use(express.json());       // Parse JSON body
app.use(express.urlencoded({ extended: false })); // Parse URL-encoded body

// CORS configuration with dynamic origin matching
const corsOptions = {
    origin: function (origin, callback) {
        const allowedOrigins = [
            'https://v2-compressed.vercel.app',
            'https://sagarhedav-asvix-fastapi.hf.space',
            'http://localhost:5173',
            'http://localhost:3000'
        ];
        // Allow requests with no origin (mobile apps, curl, etc)
        if (!origin) return callback(null, true);
        // Allow all Vercel preview deployments
        if (origin.includes('vercel.app') || origin.includes('sagarhedavs-projects.vercel.app')) {
            return callback(null, true);
        }
        // Allow explicitly listed origins
        if (allowedOrigins.includes(origin)) {
            return callback(null, true);
        }
        // Log and reject other origins
        console.log('CORS blocked origin:', origin);
        callback(new Error('Not allowed by CORS'));
    },
    credentials: true
};
app.use(cors(corsOptions));    // Enable CORS
app.use(helmet());             // Security headers

// Routes
app.use('/api/auth', require('./routes/authRoutes'));
app.use('/api/dashboard', require('./routes/dashboardRoutes'));
app.use('/api/chat', require('./routes/chatRoutes'));
app.use('/api/roadmaps', require('./routes/roadmapRoutes'));

// Serve Static Uploads
app.use('/uploads', express.static('uploads'));

// Base Route
app.get('/', (req, res) => {
    res.send('Asvix API is running...');
});

// Error Handler
app.use((err, req, res, next) => {
    const statusCode = res.statusCode ? res.statusCode : 500;
    res.status(statusCode);
    res.json({
        message: err.message,
        stack: process.env.NODE_ENV === 'production' ? null : err.stack,
    });
});

const PORT = process.env.PORT || 5001;

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
