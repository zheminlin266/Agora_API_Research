"use client";

export function BackToTop({ label }: { label: string }) {
  function handleClick(event: React.MouseEvent<HTMLAnchorElement>) {
    event.preventDefault();
    window.scrollTo({ top: 0, behavior: "smooth" });
    window.history.replaceState(null, "", `${window.location.pathname}${window.location.search}#top`);
  }

  return (
    <a href="#top" onClick={handleClick}>
      {label}
    </a>
  );
}
