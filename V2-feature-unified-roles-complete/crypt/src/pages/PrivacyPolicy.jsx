import { Link } from "react-router-dom";
import { Card } from "../components/ui/Card";
import { Button } from "../components/ui/Button";

export function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-white py-16 px-4">
      <div className="container mx-auto max-w-4xl">
        <Card className="p-8">
          <h1 className="text-3xl font-semibold text-gray-900 mb-2">
            Privacy Policy
          </h1>

          <p className="text-sm text-gray-500 mb-8">
            Last updated: {new Date().toLocaleDateString()}
          </p>

          <div className="space-y-6 text-gray-700 text-sm leading-relaxed">
            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                1. Introduction
              </h2>
              <p>
                This Privacy Policy explains how Asvix Academic AI collects,
                uses, and protects your personal information when you use our
                platform.
              </p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                2. Information We Collect
              </h2>
              <ul className="list-disc list-inside space-y-1">
                <li>Name</li>
                <li>Email address</li>
                <li>Account credentials (encrypted)</li>
                <li>Basic usage data for improving the platform</li>
              </ul>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                3. How We Use Your Information
              </h2>
              <ul className="list-disc list-inside space-y-1">
                <li>To create and manage user accounts</li>
                <li>To provide access to platform features</li>
                <li>To improve user experience and performance</li>
                <li>To communicate important updates</li>
              </ul>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                4. Data Security
              </h2>
              <p>
                We implement appropriate security measures to protect your
                personal data. Passwords are encrypted and never stored in
                plain text.
              </p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                5. Data Sharing
              </h2>
              <p>
                We do not sell or share your personal information with third
                parties except when required by law or to protect our legal
                rights.
              </p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                6. User Rights
              </h2>
              <p>
                You have the right to access, update, or delete your personal
                information. You may also request account deletion at any time.
              </p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                7. Changes to This Policy
              </h2>
              <p>
                We may update this Privacy Policy from time to time. Changes
                will be posted on this page with an updated date.
              </p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                8. Contact Us
              </h2>
              <p>
                If you have any questions about this Privacy Policy, please
                contact us through the platform.
              </p>
            </section>
          </div>

          <div className="mt-10 flex justify-end">
            <Link to="/">
              <Button>Back to Home</Button>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
