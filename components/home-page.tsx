"use client";

import { SiteHeader } from "@/components/site-header";
import { useSitePreferences } from "@/components/site-preferences";

const copy = {
  zh: {
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

export function HomePageContent() {
  const { language } = useSitePreferences();
  const text = copy[language];

  return (
    <>
      <SiteHeader />
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
