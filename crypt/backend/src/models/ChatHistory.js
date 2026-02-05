const { getFirestore } = require('../config/db');

class ChatHistory {
    static async getSessionsByUserId(userId) {
        const db = getFirestore();
        const chatHistoryCollection = db.collection('chat_history');

        try {
            const snapshot = await chatHistoryCollection
                .where('userId', '==', userId)
                .orderBy('updatedAt', 'desc')
                .get();

            if (snapshot.empty) return [];

            return snapshot.docs.map(doc => ({
                id: doc.id,
                ...doc.data()
            }));
        } catch (error) {
            console.error('Error getting sessions:', error);
            // Fallback if index is not created yet
            const snapshot = await chatHistoryCollection
                .where('userId', '==', userId)
                .get();
            return snapshot.docs.map(doc => ({
                id: doc.id,
                ...doc.data()
            })).sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
        }
    }

    static async getSessionById(sessionId) {
        const db = getFirestore();
        const chatHistoryCollection = db.collection('chat_history');

        const doc = await chatHistoryCollection.doc(sessionId).get();
        if (!doc.exists) return null;

        return { id: doc.id, ...doc.data() };
    }

    static async saveSession(userId, sessionId, messages, title) {
        const db = getFirestore();
        const chatHistoryCollection = db.collection('chat_history');

        const data = {
            userId,
            messages,
            title: title || (messages.length > 0 ? messages[0].content.substring(0, 40) + '...' : 'New Chat'),
            updatedAt: new Date().toISOString()
        };

        if (sessionId && sessionId !== 'new') {
            await chatHistoryCollection.doc(sessionId).set(data, { merge: true });
            return { id: sessionId, ...data };
        } else {
            const docRef = await chatHistoryCollection.add({
                ...data,
                createdAt: new Date().toISOString()
            });
            return { id: docRef.id, ...data };
        }
    }

    static async deleteSession(sessionId) {
        const db = getFirestore();
        const chatHistoryCollection = db.collection('chat_history');

        await chatHistoryCollection.doc(sessionId).delete();
        return { success: true };
    }

    static async clearAllSessions(userId) {
        const db = getFirestore();
        const chatHistoryCollection = db.collection('chat_history');

        const snapshot = await chatHistoryCollection.where('userId', '==', userId).get();
        if (snapshot.empty) return { success: true };

        const batch = db.batch();
        snapshot.docs.forEach(doc => {
            batch.delete(doc.ref);
        });

        await batch.commit();
        return { success: true };
    }
}

module.exports = ChatHistory;
