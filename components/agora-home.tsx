"use client";

import Image from "next/image";
import { useEffect, useRef, useState } from "react";

import agoraLogo from "@/assets/Agora_Logo.png";

type Language = "zh" | "en";
type Theme = "light" | "dark";
type MenuKey = "home" | "demand" | "supply" | "agora";

const navigation: Array<{ key: MenuKey; zh: string; en: string }> = [
  { key: "home", zh: "首页", en: "Home" },
  { key: "demand", zh: "行业需求", en: "Demand" },
  { key: "supply", zh: "行业供给", en: "Supply" },
  { key: "agora", zh: "声网", en: "Agora" },
];

const menuItems = {
  zh: {
    home: [
      { title: "标题 1" },
      { title: "标题 2" },
      { title: "标题 3" },
    ],
    demand: [
      { title: "RTC Dev npm downloads", href: "/Demand/Dev_npm_downloads/" },
      { title: "标题 2" },
      { title: "标题 3" },
    ],
    supply: [{ title: "标题 1" }, { title: "标题 2" }, { title: "标题 3" }],
    agora: [{ title: "标题 1" }, { title: "标题 2" }, { title: "标题 3" }],
  },
  en: {
    home: [{ title: "Title 1" }, { title: "Title 2" }, { title: "Title 3" }],
    demand: [
      { title: "RTC Dev npm downloads", href: "/Demand/Dev_npm_downloads/" },
      { title: "Title 2" },
      { title: "Title 3" },
    ],
    supply: [{ title: "Title 1" }, { title: "Title 2" }, { title: "Title 3" }],
    agora: [{ title: "Title 1" }, { title: "Title 2" }, { title: "Title 3" }],
  },
} as const;

const copy = {
  zh: {
    brandLabel: "Agora Research 首页",
    navLabel: "主导航",
    settings: "页面设置",
    switchLanguage: "切换为英文",
    switchToLight: "切换为浅色模式",
    switchToDark: "切换为深色模式",
    title: "从需求、供给与公司护城河理解实时互动",
    lead: "Agora Research 关注实时音视频与实时互动基础设施，沿着行业需求、供给格局与公司竞争力三条主线建立长期研究框架。",
    intro: "研究以公开资料和一手证据为基础，持续跟踪开发者生态、客户工作负载、技术演进与竞争动态。",
    frameworkTitle: "研究框架",
    pillars: [
      {
        index: "01",
        title: "行业需求",
        description: "观察社交娱乐、在线协作与 Voice AI 等场景如何改变实时互动的使用深度与市场空间。",
        note: "场景 · 工作负载 · 采用曲线",
      },
      {
        index: "02",
        title: "行业供给",
        description: "比较 RTC PaaS、通信云与开源方案的产品边界、技术路线和竞争格局。",
        note: "技术 · 生态 · 竞争",
      },
      {
        index: "03",
        title: "声网",
        description: "围绕 SD-RTN、开发者生态、客户迁移与单位经济性，评估声网的长期竞争优势。",
        note: "网络 · 产品 · 商业模式",
      },
    ],
    methodEyebrow: "Method",
    methodTitle: "让证据先于结论",
    methodBody: "将公司披露、开发者数据、客户案例与技术资料交叉验证，区分短期信号和结构性变化。",
    footer: "独立研究 · 信息不构成投资建议",
  },
  en: {
    brandLabel: "Agora Research home",
    navLabel: "Primary navigation",
    settings: "Page settings",
    switchLanguage: "Switch to Chinese",
    switchToLight: "Switch to light mode",
    switchToDark: "Switch to dark mode",
    title: "Understanding real-time engagement through demand, supply, and durable advantage",
    lead: "Agora Research studies real-time audio, video, and engagement infrastructure through three enduring lenses: industry demand, the supply landscape, and company competitiveness.",
    intro: "The work is grounded in public information and primary evidence, with ongoing attention to developer ecosystems, customer workloads, technical change, and competitive dynamics.",
    frameworkTitle: "Research framework",
    pillars: [
      {
        index: "01",
        title: "Industry demand",
        description: "Track how social entertainment, online collaboration, and Voice AI reshape usage intensity and market opportunity.",
        note: "Use cases · workloads · adoption",
      },
      {
        index: "02",
        title: "Industry supply",
        description: "Compare the product boundaries, technical paths, and competitive positions of RTC PaaS, communications clouds, and open-source alternatives.",
        note: "Technology · ecosystem · competition",
      },
      {
        index: "03",
        title: "Agora",
        description: "Assess Agora’s durable advantage through SD-RTN, its developer ecosystem, customer migration, and unit economics.",
        note: "Network · product · business model",
      },
    ],
    methodEyebrow: "Method",
    methodTitle: "Evidence before conclusions",
    methodBody: "Triangulate company disclosures, developer data, customer cases, and technical sources to distinguish short-lived signals from structural change.",
    footer: "Independent research · Not investment advice",
  },
} as const;

function MoonIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M20.2 15.2A8.5 8.5 0 0 1 8.8 3.8 8.5 8.5 0 1 0 20.2 15.2Z" />
    </svg>
  );
}

function SunIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="3.5" />
      <path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42M17.65 17.65l1.42 1.42M2 12h2M20 12h2M4.93 19.07l1.42-1.42M17.65 6.35l1.42-1.42" />
    </svg>
  );
}

export function AgoraHome() {
  const [language, setLanguage] = useState<Language>("zh");
  const [theme, setTheme] = useState<Theme>("light");
  const [openMenu, setOpenMenu] = useState<MenuKey | null>(null);
  const [headerHidden, setHeaderHidden] = useState(false);
  const navRef = useRef<HTMLElement>(null);
  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastScrollY = useRef(0);
  const text = copy[language];

  function cancelClose() {
    if (closeTimer.current) {
      clearTimeout(closeTimer.current);
      closeTimer.current = null;
    }
  }

  function closeMenu() {
    cancelClose();
    setOpenMenu(null);
  }

  function scheduleClose() {
    cancelClose();
    closeTimer.current = setTimeout(() => {
      setOpenMenu(null);
      closeTimer.current = null;
    }, 280);
  }

  useEffect(() => {
    let savedLanguage: string | null = null;
    let savedTheme: string | null = null;

    try {
      savedLanguage = window.localStorage.getItem("agora-research-language");
      savedTheme = window.localStorage.getItem("agora-research-theme");
    } catch {
      // Preferences remain usable when storage is unavailable.
    }

    const initialLanguage: Language = savedLanguage === "en" ? "en" : "zh";
    const systemTheme: Theme = window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
    const initialTheme: Theme = savedTheme === "dark" || savedTheme === "light"
      ? savedTheme
      : systemTheme;

    setLanguage(initialLanguage);
    setTheme(initialTheme);
    document.documentElement.lang = initialLanguage === "zh" ? "zh-CN" : "en";
    document.documentElement.dataset.theme = initialTheme;
  }, []);

  useEffect(() => {
    let animationFrame = 0;
    lastScrollY.current = window.scrollY;

    function handleScroll() {
      if (animationFrame) return;
      animationFrame = window.requestAnimationFrame(() => {
        const current = window.scrollY;
        const delta = current - lastScrollY.current;

        if (current <= 16) {
          setHeaderHidden(false);
        } else if (Math.abs(delta) >= 8) {
          setHeaderHidden(delta > 0 && openMenu === null);
        }

        lastScrollY.current = current;
        animationFrame = 0;
      });
    }

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", handleScroll);
      window.cancelAnimationFrame(animationFrame);
    };
  }, [openMenu]);

  useEffect(() => {
    if (!openMenu) return;

    function handlePointerDown(event: PointerEvent) {
      if (!navRef.current?.contains(event.target as Node)) closeMenu();
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") closeMenu();
    }

    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [openMenu]);

  useEffect(() => () => cancelClose(), []);

  function toggleLanguage() {
    const next: Language = language === "zh" ? "en" : "zh";
    setLanguage(next);
    closeMenu();
    document.documentElement.lang = next === "zh" ? "zh-CN" : "en";
    try {
      window.localStorage.setItem("agora-research-language", next);
    } catch {
      // The active language still works without persistence.
    }
  }

  function toggleTheme() {
    const next: Theme = theme === "light" ? "dark" : "light";
    setTheme(next);
    document.documentElement.dataset.theme = next;
    try {
      window.localStorage.setItem("agora-research-theme", next);
    } catch {
      // The active theme still works without persistence.
    }
  }

  return (
    <>
      <header
        className={`site-header${headerHidden ? " site-header--hidden" : ""}`}
        onFocus={() => setHeaderHidden(false)}
      >
        <div className="site-header__inner">
          <a className="site-brand" href="#top" aria-label={text.brandLabel}>
            <span className="site-brand__mark">
              <Image alt="" aria-hidden="true" height={32} priority src={agoraLogo} width={32} />
            </span>
            <span>Agora Research</span>
          </a>

          <nav aria-label={text.navLabel} className="site-nav" ref={navRef}>
            {navigation.map((item) => {
              const isOpen = openMenu === item.key;
              const panelId = `${item.key}-menu-panel`;

              return (
                <div
                  className={`nav-menu${isOpen ? " nav-menu--open" : ""}`}
                  key={item.key}
                  onBlur={(event) => {
                    if (!event.currentTarget.contains(event.relatedTarget)) closeMenu();
                  }}
                  onFocus={() => {
                    cancelClose();
                    setOpenMenu(item.key);
                  }}
                  onPointerEnter={(event) => {
                    if (event.pointerType === "mouse") {
                      cancelClose();
                      setOpenMenu(item.key);
                    }
                  }}
                  onPointerLeave={(event) => {
                    if (event.pointerType === "mouse") scheduleClose();
                  }}
                >
                  <button
                    aria-controls={panelId}
                    aria-expanded={isOpen}
                    aria-haspopup="true"
                    className="nav-menu__trigger"
                    onClick={() => {
                      cancelClose();
                      setOpenMenu((current) => current === item.key ? null : item.key);
                    }}
                    type="button"
                  >
                    {item[language]}
                  </button>
                  <div className="nav-menu__panel" id={panelId}>
                    {menuItems[language][item.key].map((menuItem) =>
                      "href" in menuItem ? (
                        <a className="nav-menu__item" href={menuItem.href} key={menuItem.title}>
                          <span>{menuItem.title}</span>
                        </a>
                      ) : (
                        <button className="nav-menu__item" key={menuItem.title} type="button">
                          <span>{menuItem.title}</span>
                        </button>
                      ),
                    )}
                  </div>
                </div>
              );
            })}
          </nav>

          <div className="site-controls" aria-label={text.settings}>
            <button
              aria-label={text.switchLanguage}
              className="control-button language-button"
              onClick={toggleLanguage}
              type="button"
            >
              <span className="control-swap" key={language}>{language === "zh" ? "En" : "文"}</span>
            </button>
            <button
              aria-label={theme === "light" ? text.switchToDark : text.switchToLight}
              className="control-button icon-button"
              onClick={toggleTheme}
              type="button"
            >
              <span className="control-icon" key={theme}>
                {theme === "light" ? <MoonIcon /> : <SunIcon />}
              </span>
            </button>
          </div>
        </div>
      </header>

      <main className="site-main" id="top">
        <header className="hero rise delay-1">
          <h1>{text.title}</h1>
          <div className="hero-copy">
            <p>{text.lead}</p>
            <p>{text.intro}</p>
          </div>
        </header>

        <section className="research-section rise delay-2" aria-labelledby="research-framework">
          <div className="section-heading">
            <h2 id="research-framework">{text.frameworkTitle}</h2>
          </div>
          <div className="pillar-list">
            {text.pillars.map((pillar) => (
              <article className="pillar" key={pillar.index}>
                <span className="pillar__index">{pillar.index}</span>
                <div className="pillar__copy">
                  <h3>{pillar.title}</h3>
                  <p>{pillar.description}</p>
                  <small>{pillar.note}</small>
                </div>
                <span className="pillar__arrow" aria-hidden="true">↗</span>
              </article>
            ))}
          </div>
        </section>

        <aside className="method rise delay-3">
          <p className="eyebrow">{text.methodEyebrow}</p>
          <h2>{text.methodTitle}</h2>
          <p>{text.methodBody}</p>
        </aside>

        <footer className="page-footer rise delay-4">
          <span>Agora Research</span>
          <span>{text.footer}</span>
        </footer>
      </main>
    </>
  );
}
