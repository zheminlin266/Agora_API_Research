import assert from "node:assert/strict";
import { access } from "node:fs/promises";

import {
  contentManifest,
  getNavigationMenu,
  getSearchArticles,
} from "../lib/content-manifest.ts";

const articles = contentManifest.filter((entry) => entry.kind === "article");
assert.equal(contentManifest.length, 14);
assert.equal(articles.length, 11);
assert.equal(new Set(contentManifest.map((entry) => entry.id)).size, contentManifest.length);
assert.equal(new Set(contentManifest.map((entry) => entry.href)).size, contentManifest.length);

for (const article of articles) {
  await access(`articles/${article.files.zh}`);
  await access(`articles/${article.files.en}`);
}

const zhNavigation = getNavigationMenu("zh");
assert.deepEqual(zhNavigation.demand.map((item) => item.href), [
  "/Demand/RTC_industry_demand/",
  "/Demand/US_Livestream_Commerce_Growth/",
  "/Demand/AI_Voice_Infrastructure/",
  "/Demand/Dev_npm_downloads/",
]);
assert.deepEqual(zhNavigation.supply.map((item) => item.href), [
  "/Supply/RTC_supply/",
  "/Supply/AI_RTC_moats/",
  "/Supply/OpenAI_LiveKit_Relationship/",
]);
assert.deepEqual(zhNavigation.agora.map((item) => item.href), [
  "/Agora/Customer_Scenarios_Competitive_Analysis/",
  "/Agora/Whatnot_Agora_Partnership/",
  "/Agora/Equity_Ownership_Share_Repurchase_Analysis/",
  "/Agora/Employee_Headcount_Changes/",
  "/Agora/Shanghai_Headquarters_Construction_Analysis/",
]);

const enNavigation = getNavigationMenu("en");
assert.equal(enNavigation.resources[0]?.href, "/Resources/Agora_Key_Metrics/");
assert.equal(enNavigation.resources[1]?.href, "https://github.com/zheminlin266/Agora_Research/tree/main/Resources");
assert.deepEqual(getSearchArticles().map((article) => article.href), articles.map((article) => article.href));

console.log("content manifest checks passed");
