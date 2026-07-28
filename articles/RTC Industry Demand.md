## Core Questions

1. What are the core demand scenarios for RTC?
2. How has demand for RTC changed over time?

### What Are the Main RTC Use Cases?

Estimated global RTC participant-minute mix in 2024:

| Downstream Use Case | Estimated Share of Global Minutes in 2024 | Reasonable Range | Midpoint Estimate of Minutes |
| --- | --- | --- | --- |
| Consumer social voice and video calling | **49%** | 42%–55% | Approximately 19.6 trillion minutes |
| Enterprise meetings, collaboration, and cloud communications | **20%** | 16%–25% | Approximately 8.0 trillion minutes |
| Gaming voice chat, community voice, and social entertainment | **15%** | 10%–20% | Approximately 6.0 trillion minutes |
| Interactive livestreaming, voice rooms, and livestream commerce | **7%** | 3%–12% | Approximately 2.8 trillion minutes |
| Online education and professional training | **4%** | 2%–7% | Approximately 1.6 trillion minutes |
| Customer service, contact centers, and customer engagement | **2.5%** | 1%–5% | Approximately 1.0 trillion minutes |
| Telemedicine and mental-health counseling | **0.2%** | 0.1%–0.8% | Approximately 80 billion minutes |
| Recruiting, finance, government services, remote assistance, and other use cases | **2.3%** | 1%–6% | Approximately 0.9 trillion minutes |
| **Total** | **100%** |  | **Approximately 40 trillion minutes** |

The measurement scope behind these estimates needs clarification. The estimates include:

- One-to-one and group voice and video calls;
- Video conferences and webinars;
- In-game voice chat, voice rooms, karaoke, dating, and similar use cases;
- Interactive livestreaming delivered through WebRTC, native RTC SDKs, SFUs, TURN, or similar low-latency paths;
- Online classes, telehealth consultations, and video customer service.

The estimates **exclude ordinary one-way video viewing over CDN/HLS**. Accordingly:

- Hosts, co-hosts, and users participating in live battles or PK sessions count as RTC participants;
- Ordinary livestream viewers are counted only when they actually use RTC or an ultra-low-latency interactive path;
- Watching Twitch, YouTube Live, or a livestream shopping broadcast does not mean that all viewing time qualifies as RTC minutes.

### How Has RTC Demand Changed Over Time?

Minutes are the metric that best represents actual real-world demand for RTC. However, very few industry organizations or companies systematically track this figure, so a comprehensive global dataset is not available. The best we can do is identify signals from selected company disclosures.

#### What RTC Demand Looks Like in Minutes

Agora has disclosed the following minutes-related figures publicly:

| Year | Available Data | Data Type |
| --- | --- | --- |
| 2018 | Monthly usage exceeded 12 billion minutes; the figure can also be back-calculated from the 2019 year-over-year growth rate | Monthly point-in-time figure; estimation anchor |
| 2019 | More than 20 billion minutes in December; full-year minutes grew 68.4% year over year | Monthly point-in-time figure; full-year growth rate |
| 2020 | More than 500 billion minutes | Actual annual figure |
| 2021 | More than 675 billion minutes | Actual annual figure |
| 2022 | More than 650 billion minutes | Actual annual figure |
| 2023 | Approximately 620 billion minutes | Actual annual figure |
| 2024 | More than 800 billion minutes | Actual annual figure |
| 2025 | A point-in-time disclosure of approximately 80 billion minutes per month; the annual report no longer provided full-year powered minutes, while a later public CEO speech disclosed more than 1 trillion minutes | Monthly run rate |

Zoom has disclosed the following figures for meeting minutes:

- 2013: Approximately 200 million annual meeting minutes;
- 2016: Approximately 6 billion annual meeting minutes;
- 2019: More than 5 billion meeting minutes per month;
- End of January 2020: An annualized run rate of approximately 100 billion minutes;
- April 2020: An annualized run rate of more than 2 trillion minutes;
- End of October 2020: An annualized run rate of more than 3.5 trillion minutes.

The COVID-19 pandemic spread globally in March 2020, marking a period of extremely rapid growth in RTC demand. Zoom stopped publishing its minutes figures afterward; the available evidence suggests that usage declined materially after the initial surge.

### Three Stages of Market Development

**2018–2021 — Pandemic-driven expansion:** Online education, remote meetings, and social co-streaming moved from offline settings to online platforms. Zoom's daily meeting participants grew from 10 million to 350 million; Agora's monthly minutes increased from 12 billion to more than 80 billion; and Twilio's revenue rose from $650 million to $2.84 billion. This was broad-based, mass-market growth driven by the rapid shift of nearly everything online.

**2021–2024 — Structural adjustment:** China's “double-reduction” policy eliminated the largest single source of RTC demand, as education had previously accounted for approximately 46% of Agora's demand. Zoom's growth rate fell from 326% to 3%, while Twilio's declined from 61% to 7%–8%.

**2024–2026 — Market reshaping:** Demand in areas such as livestream commerce continued to grow, while the supply side moved toward greater stability after a painful adjustment period. Usage of Agora's conversational AI engine doubled quarter over quarter. LiveKit reached a $1 billion valuation through an open-source and AI-agent orchestration strategy.
