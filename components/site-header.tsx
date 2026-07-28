"use client";

import Image from "next/image";
import { useEffect, useRef, useState } from "react";

import agoraLogo from "@/assets/Agora_Logo.png";
import { useSitePreferences } from "@/components/site-preferences";

type MenuKey = "home" | "demand" | "supply" | "agora";

const navigation: Array<{ key: MenuKey; zh: string; en: string }> = [
  { key: "home", zh: "首页", en: "Home" },
  { key: "demand", zh: "行业需求", en: "Demand" },
  { key: "supply", zh: "行业供给", en: "Supply" },
  { key: "agora", zh: "声网", en: "Agora" },
];

const menuItems = {
  zh: {
    home: [],
    demand: [
      { title: "RTC行业需求", href: "/Demand/RTC_industry_demand/" },
      { title: "RTC Dev npm Download", href: "/Demand/Dev_npm_downloads/" },
    ],
    supply: [
      { title: "RTC 行业供给", href: "/Supply/RTC_supply/" },
      { title: "AI对RTC业务护城河的影响", href: "/Supply/AI_RTC_moats/" },
    ],
    agora: [
      { title: "声网客户场景和竞争分析", href: "/Agora/Customer_Scenarios_Competitive_Analysis/" },
      { title: "Whatnot & Agora直播合作", href: "/Agora/Whatnot_Agora_Partnership/" },
      { title: "声网员工人数变化", href: "/Agora/Employee_Headcount_Changes/" },
    ],
  },
  en: {
    home: [],
    demand: [
      { title: "RTC Industry Demand", href: "/Demand/RTC_industry_demand/" },
      { title: "RTC Dev npm Download", href: "/Demand/Dev_npm_downloads/" },
    ],
    supply: [
      { title: "RTC Industry Supply", href: "/Supply/RTC_supply/" },
      { title: "Impact of AI on RTC Business Moats", href: "/Supply/AI_RTC_moats/" },
    ],
    agora: [
      { title: "Agora Customer Scenarios & Competitive Analysis", href: "/Agora/Customer_Scenarios_Competitive_Analysis/" },
      { title: "Whatnot & Agora Livestream Partnership", href: "/Agora/Whatnot_Agora_Partnership/" },
      { title: "Agora Employee Headcount Changes", href: "/Agora/Employee_Headcount_Changes/" },
    ],
  },
} as const;

const labels = {
  zh: {
    brand: "Agora Equity Research 首页",
    navigation: "主导航",
    settings: "页面设置",
    switchLanguage: "切换为英文",
    switchToLight: "切换为浅色模式",
    switchToDark: "切换为深色模式",
  },
  en: {
    brand: "Agora Equity Research home",
    navigation: "Primary navigation",
    settings: "Page settings",
    switchLanguage: "Switch to Chinese",
    switchToLight: "Switch to light mode",
    switchToDark: "Switch to dark mode",
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

export function SiteHeader() {
  const { language, theme, toggleLanguage, toggleTheme } = useSitePreferences();
  const [openMenu, setOpenMenu] = useState<MenuKey | null>(null);
  const [headerHidden, setHeaderHidden] = useState(false);
  const navRef = useRef<HTMLElement>(null);
  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const hoverOpenedMenu = useRef<MenuKey | null>(null);
  const lastScrollY = useRef(0);
  const text = labels[language];

  function cancelClose() {
    if (closeTimer.current) {
      clearTimeout(closeTimer.current);
      closeTimer.current = null;
    }
  }

  function closeMenu() {
    cancelClose();
    hoverOpenedMenu.current = null;
    setOpenMenu(null);
  }

  function scheduleClose() {
    cancelClose();
    closeTimer.current = setTimeout(() => {
      hoverOpenedMenu.current = null;
      setOpenMenu(null);
      closeTimer.current = null;
    }, 280);
  }

  useEffect(() => {
    let animationFrame = 0;
    lastScrollY.current = window.scrollY;

    function handleScroll() {
      if (animationFrame) return;
      animationFrame = window.requestAnimationFrame(() => {
        const current = window.scrollY;
        const delta = current - lastScrollY.current;

        if (current <= 16) setHeaderHidden(false);
        else if (Math.abs(delta) >= 8) setHeaderHidden(delta > 0 && openMenu === null);

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

  return (
    <header
      className={`site-header${headerHidden ? " site-header--hidden" : ""}`}
      onFocus={() => setHeaderHidden(false)}
    >
      <div className="site-header__inner">
        <a className="site-brand" href="/" aria-label={text.brand}>
          <span className="site-brand__mark">
            <Image alt="" aria-hidden="true" height={32} priority src={agoraLogo} width={32} />
          </span>
          <span>Agora Equity Research</span>
        </a>

        <nav aria-label={text.navigation} className="site-nav" ref={navRef}>
          {navigation.map((item) => {
            const isOpen = openMenu === item.key;
            const panelId = `${item.key}-menu-panel`;
            const items = menuItems[language][item.key];
            const hasPanel = items.length > 0;

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
                    hoverOpenedMenu.current = item.key;
                    setOpenMenu(item.key);
                  }
                }}
                onPointerLeave={(event) => {
                  if (event.pointerType === "mouse") scheduleClose();
                }}
              >
                {item.key === "home" ? (
                  <a
                    className="nav-menu__trigger"
                    href="/"
                    onClick={closeMenu}
                  >
                    {item[language]}
                  </a>
                ) : (
                  <button
                    aria-controls={hasPanel ? panelId : undefined}
                    aria-expanded={hasPanel ? isOpen : undefined}
                    className="nav-menu__trigger"
                    onClick={() => {
                      cancelClose();
                      if (hoverOpenedMenu.current === item.key) {
                        hoverOpenedMenu.current = null;
                        setOpenMenu(item.key);
                        return;
                      }
                      setOpenMenu((current) => current === item.key ? null : item.key);
                    }}
                    type="button"
                  >
                    {item[language]}
                  </button>
                )}
                {hasPanel && <div className="nav-menu__panel" id={panelId}>
                  {items.map((menuItem) => (
                    <a className="nav-menu__item" href={menuItem.href} key={menuItem.title}>
                      <span>{menuItem.title}</span>
                    </a>
                  ))}
                </div>}
              </div>
            );
          })}
        </nav>

        <div className="site-controls" aria-label={text.settings}>
          <button
            aria-label={text.switchLanguage}
            className="control-button language-button"
            onClick={() => {
              closeMenu();
              toggleLanguage();
            }}
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
  );
}
