# Deployment Guide

This guide details how to deploy your **Frontend to Netlify** and **Backend to Render**.

## Prerequisites
1.  **GitHub Repository**: Ensure your project is pushed to GitHub.
2.  **MongoDB Atlas**: For a production database, you should use MongoDB Atlas. The in-memory database used in development will lose data every time the server restarts.

---

## Part 1: Database Setup (MongoDB Atlas)

1.  Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and create a free account.
2.  Create a new **Cluster** (Free Tier).
3.  Create a **Database User** (Username/Password) in the "Database Access" tab.
4.  Allow access from anywhere (`0.0.0.0/0`) in the "Network Access" tab.
5.  Go to "Database" > "Connect" > "Drivers" and copy the **Connection String**.
    *   It looks like: `mongodb+srv://<username>:<password>@cluster0.net/?retryWrites=true&w=majority`
    *   Replace `<password>` with your actual password.

---

## Part 2: Backend Deployment (Render)

1.  Log in to [Render](https://render.com/).
2.  Click **New +** and select **Web Service**.
3.  Connect your GitHub repository.
4.  **Configure the Service**:
    *   **Name**: `asvix-backend` (or similar)
    *   **Root Directory**: `backend` (IMPORTANT)
    *   **Runtime**: `Node`
    *   **Build Command**: `npm install`
    *   **Start Command**: `npm start`
5.  **Environment Variables**:
    Scroll down to "Environment Variables" and add:
    *   `MONGO_URI`: Your MongoDB Connection String from Part 1.
    *   `JWT_SECRET`: A long random string (e.g., `mysecretkey123`).
    *   `NODE_ENV`: `production`
6.  Click **Create Web Service**.
7.  Wait for the deployment to finish.
8.  **Copy the Backend URL**: Once deployed, you will see a URL at the top (e.g., `https://asvix-backend.onrender.com`). You will need this for the frontend.

---

## Part 3: Frontend Deployment (Netlify)

1.  Log in to [Netlify](https://www.netlify.com/).
2.  Click **Add new site** > **Import from Git**.
3.  Connect your GitHub repository.
4.  **Configure the Build**:
    *   **Base directory**: `.` (leave empty or default)
    *   **Build command**: `npm run build`
    *   **Publish directory**: `dist`
5.  **Environment Variables**:
    *   Click on **"Add environment variables"** (or go to Site Settings > Environment variables after creation).
    *   Key: `VITE_API_URL`
    *   Value: `<Your Backend URL>/api`  
        *   Example: `https://asvix-backend.onrender.com/api`
        *   **Important**: Make sure to include `/api` at the end if that matches your backend routes structure.
6.  Click **Deploy site**.

## Verification
- Open your Netlify URL.
- Try to Login/Register.
- If it works, your full stack app is live!
