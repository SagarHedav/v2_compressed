const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');

const connectDB = async () => {
    try {
        // Try connecting to the provided URI first
        if (process.env.MONGO_URI && !process.env.MONGO_URI.includes('<db_password>')) {
            const conn = await mongoose.connect(process.env.MONGO_URI);
            console.log(`MongoDB Connected: ${conn.connection.host}`);
            return;
        }

        // Fallback to In-Memory Database
        console.log("External MongoDB not configured or failed. Starting In-Memory MongoDB...");
        const mongod = await MongoMemoryServer.create();
        const uri = mongod.getUri();

        const conn = await mongoose.connect(uri);
        console.log(`In-Memory MongoDB Connected: ${conn.connection.host}`);

    } catch (error) {
        console.error(`Error: ${error.message}`);
        // If even in-memory fails, then exit
        process.exit(1);
    }
};

module.exports = connectDB;
