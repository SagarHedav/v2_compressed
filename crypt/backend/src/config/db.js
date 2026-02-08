const admin = require('firebase-admin');
const path = require('path');
const fs = require('fs');

let db;

const initializeFirebase = () => {
    try {
        // Check if Firebase is already initialized
        if (admin.apps.length > 0) {
            db = admin.firestore();
            console.log('Firebase already initialized');
            return db;
        }

        let serviceAccount;
        const keyFilePath = path.join(__dirname, '../../firebase-key.json');

        // Log environment for debugging
        console.log('NODE_ENV:', process.env.NODE_ENV);
        console.log('Checking for firebase-key.json at:', keyFilePath);
        console.log('File exists:', fs.existsSync(keyFilePath));
        console.log('FIREBASE_PROJECT_ID set:', !!process.env.FIREBASE_PROJECT_ID);

        // Prefer environment variables in production
        if (process.env.NODE_ENV === 'production' && process.env.FIREBASE_PROJECT_ID && process.env.FIREBASE_PRIVATE_KEY && process.env.FIREBASE_CLIENT_EMAIL) {
            console.log('Using environment variables for Firebase authentication (production)');
            // Handle both escaped and unescaped newlines
            let privateKey = process.env.FIREBASE_PRIVATE_KEY;
            if (privateKey.includes('\\n')) {
                privateKey = privateKey.replace(/\\n/g, '\n');
            }
            serviceAccount = {
                type: 'service_account',
                project_id: process.env.FIREBASE_PROJECT_ID,
                private_key: privateKey,
                client_email: process.env.FIREBASE_CLIENT_EMAIL
            };
        }
        // Check if firebase-key.json exists (local development)
        else if (fs.existsSync(keyFilePath)) {
            console.log('Using firebase-key.json for authentication');
            serviceAccount = require(keyFilePath);
        }
        // Fallback to environment variables
        else if (process.env.FIREBASE_PROJECT_ID && process.env.FIREBASE_PRIVATE_KEY && process.env.FIREBASE_CLIENT_EMAIL) {
            console.log('Using environment variables for Firebase authentication');
            let privateKey = process.env.FIREBASE_PRIVATE_KEY;
            if (privateKey.includes('\\n')) {
                privateKey = privateKey.replace(/\\n/g, '\n');
            }
            serviceAccount = {
                type: 'service_account',
                project_id: process.env.FIREBASE_PROJECT_ID,
                private_key: privateKey,
                client_email: process.env.FIREBASE_CLIENT_EMAIL
            };
        } else {
            throw new Error('No Firebase credentials found. Provide firebase-key.json or set FIREBASE_PROJECT_ID, FIREBASE_PRIVATE_KEY, FIREBASE_CLIENT_EMAIL environment variables.');
        }

        admin.initializeApp({
            credential: admin.credential.cert(serviceAccount),
            databaseURL: `https://${serviceAccount.project_id}.firebaseio.com`
        });

        db = admin.firestore();
        console.log('Firebase initialized successfully');
        return db;

    } catch (error) {
        console.error(`Firebase initialization error: ${error.message}`);
        console.error('Full error:', error);
        process.exit(1);
    }
};

const getFirestore = () => {
    if (!db) {
        initializeFirebase();
    }
    return db;
};

module.exports = { initializeFirebase, getFirestore };
