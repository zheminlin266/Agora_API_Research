import { NextRequest, NextResponse } from "next/server";

import { searchArticles, type SearchLanguage } from "@/lib/site-search";

const MAX_QUERY_LENGTH = 80;
const SUCCESS_HEADERS = {
  "Cache-Control": "public, max-age=60, stale-while-revalidate=300",
};
const ERROR_HEADERS = { "Cache-Control": "no-store" };

function languageFromParam(value: string | null): SearchLanguage {
  return value === "en" ? "en" : "zh";
}

export async function GET(request: NextRequest) {
  const query = request.nextUrl.searchParams.get("q")?.trim() ?? "";
  const language = languageFromParam(request.nextUrl.searchParams.get("lang"));

  if (query.length > MAX_QUERY_LENGTH) {
    return NextResponse.json(
      {
        error: "Search query is too long.",
        code: "QUERY_TOO_LONG",
        maxLength: MAX_QUERY_LENGTH,
      },
      { status: 400, headers: ERROR_HEADERS },
    );
  }

  if (!query) {
    return NextResponse.json({ results: [] }, { headers: SUCCESS_HEADERS });
  }

  try {
    const results = await searchArticles(query, language);
    return NextResponse.json({ results }, { headers: SUCCESS_HEADERS });
  } catch (error) {
    console.error("Search index unavailable.", error);
    return NextResponse.json(
      { error: "Search is temporarily unavailable.", code: "SEARCH_UNAVAILABLE" },
      { status: 503, headers: ERROR_HEADERS },
    );
  }
}
