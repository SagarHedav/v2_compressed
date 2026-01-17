import { motion, useScroll, useTransform } from "framer-motion";
import { Link } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { PageTransition } from "../components/ui/PageTransition";
import {
  ArrowRight,
  BookOpen,
  BrainCircuit,
  Sparkles,
  Zap,
  Star,
  StarOff,
} from "lucide-react";
import { useUI } from "../context/UIContext";

export function HomePage() {
  const { scrollY } = useScroll();
  const y = useTransform(scrollY, [0, 500], [0, 200]);
  const opacity = useTransform(scrollY, [0, 300], [1, 0]);
  const {
    isShootingStarsEnabled,
    toggleShootingStars,
    isBubblesEnabled,
    toggleBubbles,
  } = useUI();
  const { t } = useLanguage();

  return (
    <PageTransition className="flex flex-col space-y-32 pb-24">
      {/* ================= HERO SECTION ================= */}
      <section className="relative flex min-h-[80vh] flex-col items-center justify-center text-center">
        <motion.div
          style={{ y, opacity }}
          className="z-10 flex flex-col items-center space-y-8"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center rounded-full border border-accent/30 bg-accent/10 px-3 py-1 text-xs font-mono text-accent-bright backdrop-blur-md"
          >
            <Sparkles className="mr-2 h-3 w-3" />
            {t("home.hero.badge")}
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="max-w-4xl text-5xl font-semibold tracking-tight sm:text-7xl lg:text-8xl"
          >
            <span className="bg-gradient-to-b from-foreground via-foreground/90 to-foreground/70 dark:from-white dark:via-white/95 dark:to-white/70 bg-clip-text text-transparent">
              {t("home.hero.title1")}
            </span>
            <br />
            <span className="bg-gradient-to-r from-[#5E6AD2] via-indigo-400 to-[#5E6AD2] bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient">
              {t("home.hero.title2")}
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="max-w-2xl text-lg text-foreground-muted sm:text-xl"
          >
            {t("home.hero.description")}
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <Link to="/signup">
              <Button size="lg" className="h-12 px-8 text-base">
                <Sparkles className="mr-2 h-5 w-5" />
                Get Started
              </Button>
            </Link>
          </motion.div>

          {/* Dark mode toggle */}
          <div className="mt-8 hidden dark:block">
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleShootingStars}
              className="text-xs text-foreground-muted hover:text-white"
            >
              {isShootingStarsEnabled ? (
                <>
                  <StarOff className="mr-2 h-3 w-3" />
                  {t("home.hero.starsOff")}
                </>
              ) : (
                <>
                  <Star className="mr-2 h-3 w-3" />
                  {t("home.hero.starsOn")}
                </>
              )}
            </Button>
          </div>

          {/* Light mode toggle */}
          <div className="mt-8 block dark:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleBubbles}
              className="text-xs text-foreground-muted hover:text-foreground"
            >
              {isBubblesEnabled ? (
                <>
                  <StarOff className="mr-2 h-3 w-3" />
                  {t("home.hero.3dOff")}
                </>
              ) : (
                <>
                  <Star className="mr-2 h-3 w-3" />
                  {t("home.hero.3dOn")}
                </>
              )}
            </Button>
          </div>
        </motion.div>
      </section>

      {/* ================= FEATURES SECTION ================= */}
      <section className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-semibold sm:text-4xl">
            {t("home.features.title")}
          </h2>
          <p className="mt-4 text-foreground-muted">
            {t("home.features.subtitle")}
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-6 md:auto-rows-[180px]">
          <Card className="col-span-1 md:col-span-4 md:row-span-2 p-8 flex flex-col justify-end">
            <BookOpen className="h-12 w-12 text-accent mb-4" />
            <h3 className="text-2xl font-semibold">
              {t("home.features.card1.title")}
            </h3>
            <p className="mt-2 text-foreground-muted max-w-md">
              {t("home.features.card1.desc")}
            </p>
          </Card>

          <Card className="col-span-1 md:col-span-2 p-6">
            <Zap className="h-8 w-8 text-yellow-500" />
            <h3 className="mt-4 text-lg font-medium">
              {t("home.features.card2.title")}
            </h3>
            <p className="text-sm text-foreground-muted">
              {t("home.features.card2.desc")}
            </p>
          </Card>

          <Card className="col-span-1 md:col-span-2 p-6">
            <BrainCircuit className="h-8 w-8 text-purple-500" />
            <h3 className="mt-4 text-lg font-medium">
              {t("home.features.card3.title")}
            </h3>
            <p className="text-sm text-foreground-muted">
              {t("home.features.card3.desc")}
            </p>
          </Card>

          <Card className="col-span-1 md:col-span-6 p-8 flex items-center justify-between">
            <div>
              <h3 className="text-xl font-semibold">
                {t("home.features.card4.title")}
              </h3>
              <p className="text-foreground-muted">
                {t("home.features.card4.desc")}
              </p>
            </div>
            <Button variant="ghost">
              {t("home.features.card4.btn")}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Card>
        </div>
      </section>
    </PageTransition>
  );
}
