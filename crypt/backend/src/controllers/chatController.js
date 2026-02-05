const ChatHistory = require('../models/ChatHistory');

// @desc    Get all chat sessions for user
// @route   GET /api/chat/sessions
// @access  Private
const getSessions = async (req, res) => {
    try {
        const sessions = await ChatHistory.getSessionsByUserId(req.user.id);
        res.json(sessions);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// @desc    Get specific chat session messages
// @route   GET /api/chat/sessions/:id
// @access  Private
const getSession = async (req, res) => {
    try {
        const session = await ChatHistory.getSessionById(req.params.id);
        if (!session || session.userId !== req.user.id) {
            return res.status(404).json({ message: 'Session not found' });
        }
        res.json(session);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// @desc    Create or update a chat session
// @route   POST /api/chat/sessions
// @access  Private
const saveSession = async (req, res) => {
    const { sessionId, messages, title } = req.body;

    if (!messages || !Array.isArray(messages)) {
        return res.status(400).json({ message: 'Please provide messages array' });
    }

    try {
        const session = await ChatHistory.saveSession(req.user.id, sessionId, messages, title);
        res.json(session);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// @desc    Delete a specific chat session
// @route   DELETE /api/chat/sessions/:id
// @access  Private
const deleteSession = async (req, res) => {
    try {
        const session = await ChatHistory.getSessionById(req.params.id);
        if (!session || session.userId !== req.user.id) {
            return res.status(404).json({ message: 'Session not found' });
        }

        await ChatHistory.deleteSession(req.params.id);
        res.json({ message: 'Session deleted successfully' });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// @desc    Clear all chat sessions for user
// @route   DELETE /api/chat/sessions
// @access  Private
const clearAllSessions = async (req, res) => {
    try {
        await ChatHistory.clearAllSessions(req.user.id);
        res.json({ message: 'All chat history cleared' });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

module.exports = {
    getSessions,
    getSession,
    saveSession,
    deleteSession,
    clearAllSessions
};
