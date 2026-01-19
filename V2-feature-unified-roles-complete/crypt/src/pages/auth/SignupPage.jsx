import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Background } from "../../components/ui/Background";
import { BookOpen, X } from "lucide-react";
import api from "../../lib/api";

export function SignupPage() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [showPolicy, setShowPolicy] = useState(false);
  const [hasScrolled, setHasScrolled] = useState(false);

  const performSignup = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.post("/auth/register", formData);
      localStorage.setItem("user", JSON.stringify(data));
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setShowPolicy(true);
  };

  const handleScroll = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.target;
    if (scrollTop + clientHeight >= scrollHeight - 5) {
      setHasScrolled(true);
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center p-4">
      <Background />

      <Card className="w-full max-w-md p-8 z-10">
        <div className="flex flex-col items-center mb-8 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent/20 mb-4">
            <BookOpen className="h-6 w-6 text-accent" />
          </div>
          <h1 className="text-2xl font-semibold">Create an account</h1>
          <p className="text-sm text-gray-500">
            Get started with your free account
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 rounded-md bg-red-100 text-xs text-red-600 border border-red-300">
              {error}
            </div>
          )}

          <div className="space-y-1">
            <label className="text-xs font-medium uppercase text-gray-600">
              Name
            </label>
            <Input
              placeholder="John Doe"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              required
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-medium uppercase text-gray-600">
              Email
            </label>
            <Input
              type="email"
              placeholder="name@university.edu"
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
              required
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-medium uppercase text-gray-600">
              Password
            </label>
            <Input
              type="password"
              placeholder="••••••••"
              value={formData.password}
              onChange={(e) =>
                setFormData({ ...formData, password: e.target.value })
              }
              required
            />
          </div>

          <Button className="w-full" size="lg" disabled={loading}>
            {loading ? "Creating Account..." : "Create Account"}
          </Button>
        </form>

        <p className="mt-8 text-center text-sm text-gray-500">
          Already have an account?{" "}
          <Link
            to="/login"
            className="text-accent font-medium hover:underline"
          >
            Sign in
          </Link>
        </p>
      </Card>

      {/* ================= Terms & Privacy Modal ================= */}
      {showPolicy && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl w-full max-w-lg p-6 relative shadow-lg">
            <button
              onClick={() => setShowPolicy(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              <X size={18} />
            </button>

            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Terms & Conditions
            </h2>
            <p className="text-sm text-gray-500 mb-4">
              Please read and accept before creating your account.
            </p>

            <div
              className="h-64 overflow-y-auto border rounded-md p-4 text-sm text-gray-700 space-y-4"
              onScroll={handleScroll}
            >
              <section>
                <h3 className="font-semibold text-gray-900 mb-1">
                  1. Data Collection
                </h3>
                <p>
                  We collect your name, email address, and password solely for
                  account creation and authentication purposes.
                </p>
              </section>

              <section>
                <h3 className="font-semibold text-gray-900 mb-1">
                  2. Data Security
                </h3>
                <p>
                  Your password is encrypted and stored securely. We never store
                  passwords in plain text.
                </p>
              </section>

              <section>
                <h3 className="font-semibold text-gray-900 mb-1">
                  3. Data Usage
                </h3>
                <p>
                  Your personal data will not be shared with third parties
                  without your consent, except when legally required.
                </p>
              </section>

              <section>
                <h3 className="font-semibold text-gray-900 mb-1">
                  4. User Responsibilities
                </h3>
                <p>
                  You agree to use this platform responsibly and not engage in
                  any unlawful or harmful activities.
                </p>
              </section>

              <section>
                <h3 className="font-semibold text-gray-900 mb-1">
                  5. Account Termination
                </h3>
                <p>
                  Violation of our policies may result in suspension or
                  termination of your account.
                </p>
              </section>

              <p className="text-xs text-gray-500">
                Scroll to the bottom to enable the “I Agree” button.
              </p>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button
                variant="ghost"
                onClick={() => setShowPolicy(false)}
              >
                I Disagree
              </Button>

              <Button
                disabled={!hasScrolled || loading}
                onClick={() => {
                  setShowPolicy(false);
                  performSignup();
                }}
              >
                I Agree
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
