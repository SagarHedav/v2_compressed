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

        // Check if firebase-key.json exists (local development)
        if (fs.existsSync(keyFilePath)) {
            console.log('Using firebase-key.json for authentication');
            serviceAccount = require(keyFilePath);
        } 
        // Use environment variables (production/Render)
        else if (process.env.FIREBASE_PROJECT_ID && process.env.FIREBASE_PRIVATE_KEY && process.env.FIREBASE_CLIENT_EMAIL) {
            console.log('Using environment variables for Firebase authentication');
            serviceAccount = {
                type: 'service_account',
                project_id: process.env.FIREBASE_PROJECT_ID,
                private_key: process.env.FIREBASE_PRIVATE_KEY.replace(/\\n/g, '\n'),
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
