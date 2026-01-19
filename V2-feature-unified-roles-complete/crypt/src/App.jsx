import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { AnimatePresence } from "framer-motion";

import { Layout } from "./layouts/Layout";

import { HomePage } from "./pages/HomePage";
import { DashboardPage } from "./pages/DashboardPage";
import { ProfilePage } from "./pages/ProfilePage";
import { DocumentsPage } from "./pages/DocumentsPage";
import { ChatPage } from "./pages/ChatPage";
import { TermsAndConditions } from "./pages/TermsAndConditions";

import { LoginPage } from "./pages/auth/LoginPage";
import { SignupPage } from "./pages/auth/SignupPage";
import { PrivacyPolicy } from "./pages/PrivacyPolicy";

import { UIProvider } from "./context/UIContext";
import { LanguageProvider } from "./context/LanguageContext";
import { DocumentProvider } from "./context/DocumentContext";

function AnimatedRoutes() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        {/* Auth routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />

        {/* Standalone routes */}
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/terms" element={<TermsAndConditions />} />

        {/* Main layout routes */}
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/privacy-policy" element={<PrivacyPolicy />} />
        </Route>
      </Routes>
    </AnimatePresence>
  );
}

function App() {
  return (
    <UIProvider>
      <LanguageProvider>
        <DocumentProvider>
          <BrowserRouter>
            <AnimatedRoutes />
          </BrowserRouter>
        </DocumentProvider>
      </LanguageProvider>
    </UIProvider>
  );
}

export default App;
