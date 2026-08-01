"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";

export type Language = "zh" | "en";
export type Theme = "light" | "dark";

type SitePreferencesValue = {
  language: Language;
  theme: Theme;
  toggleLanguage: () => void;
  toggleTheme: () => void;
};

const SitePreferencesContext = createContext<SitePreferencesValue | null>(null);

export function SitePreferencesProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguage] = useState<Language>("zh");
  const [theme, setTheme] = useState<Theme>("light");

  useEffect(() => {
    let savedLanguage: string | null = null;
    let savedTheme: string | null = null;

    try {
      savedLanguage = window.localStorage.getItem("agora-research-language");
      savedTheme = window.localStorage.getItem("agora-research-theme");
    } catch {
      // The site remains usable when storage is unavailable.
    }

    const requestedLanguage = new URLSearchParams(window.location.search).get("lang");
    const initialLanguage: Language = requestedLanguage === "en" || requestedLanguage === "zh"
      ? requestedLanguage
      : savedLanguage === "en" ? "en" : "zh";
    const systemTheme: Theme = window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
    const initialTheme: Theme = savedTheme === "dark" || savedTheme === "light"
      ? savedTheme
      : systemTheme;

    if (requestedLanguage === "en" || requestedLanguage === "zh") {
      try {
        window.localStorage.setItem("agora-research-language", requestedLanguage);
      } catch {
        // The active language still works without persistence.
      }
    }

    setLanguage(initialLanguage);
    setTheme(initialTheme);
    document.documentElement.lang = initialLanguage === "zh" ? "zh-CN" : "en";
    document.documentElement.dataset.theme = initialTheme;
  }, []);

  const value = useMemo<SitePreferencesValue>(() => ({
    language,
    theme,
    toggleLanguage() {
      const next: Language = language === "zh" ? "en" : "zh";
      setLanguage(next);
      document.documentElement.lang = next === "zh" ? "zh-CN" : "en";
      try {
        window.localStorage.setItem("agora-research-language", next);
      } catch {
        // The active language still works without persistence.
      }
    },
    toggleTheme() {
      const next: Theme = theme === "light" ? "dark" : "light";
      setTheme(next);
      document.documentElement.dataset.theme = next;
      try {
        window.localStorage.setItem("agora-research-theme", next);
      } catch {
        // The active theme still works without persistence.
      }
    },
  }), [language, theme]);

  return (
    <SitePreferencesContext.Provider value={value}>
      {children}
    </SitePreferencesContext.Provider>
  );
}

export function useSitePreferences() {
  const context = useContext(SitePreferencesContext);
  if (!context) throw new Error("useSitePreferences must be used inside SitePreferencesProvider");
  return context;
}
