# Agora's Competitive Space and Migration Cases

### Core Questions

1. Which specific workloads generate Agora's business, and what technical constraints do those workloads impose?
2. At what stage of scale do customers shift from buying a solution to building in-house?
3. Are there documented cases of customers migrating to Agora from competitors? What prompted those migrations?
4. Are there documented cases of customers migrating away from Agora? What prompted those migrations?

### Workloads Served by Agora's Business

| Workload | Revenue and expansion drivers | Retention mechanism | Key technical constraints | Directional impact on gross margin |
| --- | --- | --- | --- | --- |
| Social voice chat rooms and multi-party audio rooms | Audio minutes, concurrent-user growth, cross-room interaction, recording, and content safety | Social connections among users and room-based features embed RTC deeply into the product | Large-room fan-out, poor network conditions, echo cancellation, push-to-talk contention, support for low-end devices, and global latency | Audio-only bandwidth costs are low, but a large always-on user base and steep discounts can reduce per-unit gross margin |
| 1:1 audio and video, companionship, and dating | Call minutes, growth in paying users, and add-on features such as beauty filters, noise suppression, and moderation | Calling, push notifications, billing, risk controls, and matching systems are coupled to the SDK | Call-connect rate, NAT traversal, time to first frame, background wake-up on mobile, privacy, and security | Usually relatively standardized; geography and video quality determine bandwidth costs |
| Interactive livestreaming, co-hosting, and PK battles | Number of hosts and viewers, cross-room PK, stream-out, recording, and transcoding | Livestreaming businesses are highly sensitive to reliability and peak capacity, making replacement risky | Extremely high concurrency, host uplink quality, CDN stream-out, audio-video synchronization, and sudden traffic spikes | CDN, transcoding, recording, and peak-capacity redundancy add costs; adjacent products can increase revenue density |
| Online education and training | Classroom minutes, whiteboards, recording, replay, and content processing | Teaching workflows, course materials, whiteboards, and classroom management create integration stickiness | Screen sharing, poor network conditions, low-end devices, teacher/student permissions, and traceable recordings | Classroom demand is concentrated around peak periods; capacity redundancy and discounts for large customers can compress margins |
| Telehealth and remote services | Consultation minutes, recording, transcription, and compliance capabilities | Compliance, auditability, and workflow integration raise switching costs | Data residency, encryption, access control, reliability, and browser compatibility | Compliance requirements and dedicated deployments increase delivery costs, but customers may have greater willingness to pay |
| Enterprise collaboration and remote meetings | Seats or minutes, recording, transcription, and meeting controls | Integration with identity, calendars, documents, and administrative systems | Multi-party meetings, screen sharing, enterprise firewalls, TURN coverage, and SLAs | Enterprise service and support costs are higher; scale and contract pricing determine margins |
| IoT doorbells, cameras, and hardware intercoms | Device count, call frequency, cloud recording, and device management | Once the SDK is embedded in firmware and the hardware lifecycle, replacement costs are high | ARM resource constraints, power consumption, unstable networks, long product lifecycles, firmware updates, and echo | Usage per device may be low, but lifecycles are long; customization and support affect margins |
| In-game voice and metaverse spatial audio | DAU, time spent online, spatial audio, and other advanced features | Deep integration with the game engine, room system, and social features | Ultra-low latency, positional audio, cross-platform support, CPU usage, and the number of simultaneous speakers | Audio bandwidth costs are low, but high concurrency, global points of presence, and engine integration add costs |
| Conversational AI voice agents | Conversation minutes, plus STT/LLM/TTS orchestration or value-added capabilities | Real-time interruption, transcription, model routing, and business workflows create a new layer of integration | End-to-end latency, interruptibility, audio quality, model jitter, and cost-aware routing | If Agora provides only audio transport, revenue density is limited; if it handles orchestration and value-added services, revenue potential is higher, but compute costs rise as well |

The gross-margin observations above are workload-level analysis, not product-level gross-margin data disclosed by Agora. Agora does not disclose revenue and gross margin separately for each of these use cases, so the table cannot be directly converted into segment figures in the financial statements.

### When Customers Shift from Buying to Building In-House

**A significant portion of the information available for this question comes from Trembit and Forasoft. Both organizations have businesses that help customers develop RTC services, including services for migrating away from Agora. Their analysis and views are therefore connected to their own commercial interests. They can be used as reference points, but should be given less weight.**

There is no universal user-count, revenue, or concurrency threshold. A company should consider building in-house when the following conditions start to appear together:

- **Cost conditions**: RTC billing has become a significant and stable part of the product's unit economics, and the fully loaded cost of building infrastructure, paying for bandwidth, and staffing a team is clearly below the vendor's pricing.
- **Workload conditions**: Traffic is large enough and predictable enough to continuously amortize the cost of media servers, global points of presence, monitoring, and SRE; when traffic is highly volatile, the elasticity of a cloud service remains valuable.
- **Strategic conditions**: The audio and video experience has become a core competitive advantage rather than an ancillary feature, and the company needs to customize congestion control, routing, codecs, mixing, or spatial audio.
- **Organizational conditions**: The company already has the capabilities for WebRTC/SFU, client-side media, networking, SRE, quality measurement, and 24/7 incident response.
- **Compliance conditions**: Data sovereignty, private deployment, government requirements, or regulatory requirements cannot be met through a standard public-cloud product.
- **Migration conditions**: The business layer is decoupled from the media layer, enabling dual-stack operation, gradual traffic migration, and rapid rollback.

The more common path is not a sudden jump from “buy” to “build everything in-house,” but a gradual progression:

Buy a complete solution → Build in-house business signaling and room orchestration → Build in-house audio effects/mixing/moderation → Self-host selected high-volume or highly regulated routes → Replace the full stack only when the payoff is clear enough.

#### A Full Technical Architecture for Building RTC In-House

Building a production-grade RTC system in-house requires four core components:

**Signaling server**: Handles session setup, ICE candidate exchange, and room management; [typically built on WebSocket or Socket.io](http://通常基于WebSocket或Socket.io) ([Agora build-vs-buy analysis](https://www.agora.io/en/blog/what-it-takes-to-build-a-real-time-voice-and-video-infrastructure/));

**STUN/TURN traversal servers**: Approximately 15%–40% of users cannot connect directly because of firewall/NAT restrictions and must use a TURN relay. TURN bandwidth costs are the largest hidden expense in a self-built solution ([Trembit 2026 cost analysis](https://trembit.com/blog/webrtc-costs-in-2026-what-ctos-actually-pay-and-what-they-miss-until-its-too-late/));

**SFU media servers**: In multi-party calls, selectively forward audio and video streams without decoding or mixing them; this is I/O-intensive ([free4chat evolution analysis](https://zhichai.net/t/177620443));

**Cross-platform client SDKs**: Must support iOS, Android, Web, Windows, macOS, and frameworks such as Flutter and React Native, while continuously adapting to operating-system and browser updates ([Agora build-vs-buy analysis](https://www.agora.io/en/blog/what-it-takes-to-build-a-real-time-voice-and-video-infrastructure/)).

It is important to note that each of these four layers can cause operational complexity to grow exponentially at scale. For example, in production, TURN servers face non-obvious failure modes such as Linux kernel netfilter connection-tracking table overflow (conntrack table overflow), SoftIRQ bottlenecks, and memory exhaustion caused by the OOM Killer ([TrueSight production crash case](https://tsight.io/articles/10557154)). As one experienced WebRTC engineer put it: “Most WebRTC projects don't die at 10,000 concurrent users; they die at 300 users—in real network conditions such as hotel Wi-Fi, parking-lot phone hotspots, and cross-border NAT” ([Most WebRTC Projects Fail at 300 Users](https://dev.to/jackmorris10/most-webrtc-projects-dont-fail-at-scale-they-fail-at-300-users-45l3)).

#### TCO Model: Build In-House vs. Buy

Based on actual 2025 deployment data, Trembit provides TCO benchmarks at different scales (720p video, an average 20-minute call, a 25% TURN relay rate, excluding recording) ([Trembit 2026 cost analysis](https://trembit.com/blog/webrtc-costs-in-2026-what-ctos-actually-pay-and-what-they-miss-until-its-too-late/)):

| **Monthly usage** | **Managed cloud (Agora/Twilio)** | **LiveKit Cloud** | **Self-hosted SFU (AWS)** | **Hybrid P2P + self-hosted** |
| --- | --- | --- | --- | --- |
| 500,000 participant-minutes | $1,500–$4,000 | $800–$2,000 | $600–$1,200 | $400–$800 |
| 2 million participant-minutes | $6,000–$16,000 | $3,000–$7,000 | $1,800–$3,500 | $1,200–$2,400 |
| 10 million participant-minutes | $30,000–$70,000 | $12,000–$25,000 | $6,000–$12,000 | $4,000–$8,000 |

Using a real-world case with 1,000 peak concurrent users (four-person rooms, 90-minute sessions, and approximately 18 million minutes per month), Forasoft produced a more specific estimate: Agora would cost approximately $17,820 per month ($0.99 per 1,000 HD minutes), exceeding $20,000 per month after recording fees were added. A self-hosted LiveKit setup (four Hetzner AX102 servers + a TURN cluster + 20% of an SRE's time allocated to the service) would cost only about $3,500–$4,000 per month, making self-hosting four to five times cheaper than managed hosting ([Forasoft Agora alternative analysis](https://forasoft.com/blog/article/agora-io-alternative)).

**Hidden costs are the key variable**: Trembit notes that the fully loaded cost of WebRTC infrastructure is typically 1.6–2.2 times the initial compute and bandwidth estimate. The difference includes recording infrastructure (an additional 20%–35%), global geographic distribution, monitoring and observability tools (Grafana plus custom metrics or commercial products such as Callstats/Cyara), and idle compute capacity reserved for peak periods ([Trembit 2026 cost analysis](https://trembit.com/blog/webrtc-costs-in-2026-what-ctos-actually-pay-and-what-they-miss-until-its-too-late/)). In addition, the median annual salary for a senior WebRTC engineer in the United States is $133,000 ([OrbytJobs 2026 salary data](https://www.orbytjobs.ai/salaries/webrtc-engineer)); in China, annual compensation for senior roles can also reach RMB 420,000–600,000 ([Beilie senior WebRTC engineer](https://www.beilie.com/positionDetail?positionId=959822060408799232)), and an in-house effort requires at least two to three engineers at this level.

#### Quantifying the In-House-Build Inflection Point: It Is Not a Single Number

The central conclusion is that the in-house-build inflection point is a range, not a single number.

- **Below 500,000 participant-minutes per month**: Managed cloud has an overwhelming TCO advantage. The engineering team should focus on the product rather than infrastructure. At this stage, the fixed engineering cost of self-hosting (at least one WebRTC engineer plus a baseline infrastructure investment) far exceeds the managed-service bill ([Trembit 2026 cost analysis](https://trembit.com/blog/webrtc-costs-in-2026-what-ctos-actually-pay-and-what-they-miss-until-its-too-late/)).
- **500,000–1 million participant-minutes per month**: This is a gray area. Self-hosting begins to become cost-competitive, but only if the team has the capability to operate WebRTC infrastructure ([Trembit 2026 cost analysis](https://trembit.com/blog/webrtc-costs-in-2026-what-ctos-actually-pay-and-what-they-miss-until-its-too-late/)).
- **5–15 million participant-minutes per month**: In most scenarios, self-hosting is materially more economical than managed cloud. Forasoft's decision framework suggests that below 5 million minutes per month, PaaS is almost always cheaper; between 5 million and 15 million, the answer depends on the engineering team's capabilities; above 15 million, self-hosting is highly likely to win ([Forasoft Agora alternative analysis](https://forasoft.com/blog/article/agora-io-alternative)).
- **More than 15 million participant-minutes per month**: A self-hosted or hybrid solution is the only economically rational choice ([Trembit 2026 cost analysis](https://trembit.com/blog/webrtc-costs-in-2026-what-ctos-actually-pay-and-what-they-miss-until-its-too-late/)).

**The inflection point varies by use case**: For audio-only calls, bandwidth consumption is low (approximately 50 kbps), so managed-cloud costs are minimal and the self-hosting inflection point moves much farther to the right. High-definition video (1080p+) consumes more bandwidth (2–4 Mbps), moving the inflection point to the left. Interactive livestreaming is more complicated because it requires CDN streaming and recording. If 1:1 calls make up a large share of the product, as in telehealth or online tutoring, a hybrid P2P + SFU architecture can reduce total infrastructure spending by 30%–45%, shifting the inflection point further ([Trembit 2026 cost analysis](https://trembit.com/blog/webrtc-costs-in-2026-what-ctos-actually-pay-and-what-they-miss-until-its-too-late/)).

### Public Community Cases of Migrating to Agora from Competitors

Some migration cases involving small teams can be confirmed from public GitHub records:

- Teamhapp/socialcall migrated from `flutter_webrtc` and LiveKit to Agora. The commit messages cite motivations including no longer having to handle STUN/TURN themselves, improving 1:1 audio and video, livestreaming, FCM offline push notifications, and mobile calling workflows. [Client commit](https://github.com/Teamhapp/socialcall_app/commit/a005ce0f428de35bacd0852060fda80b6220fa2a); [server commit](https://github.com/Teamhapp/socialcall_backend/commit/b3a3e5ec896838fe51378009a5078a7176ea12b8)
- Broadfi-music/Bario migrated from Daily, LiveKit, and Jitsi to Agora audio streaming, but the commit notes that live testing had not yet been completed, so this should be treated only as a record of a development-stage migration. [GitHub commit](https://github.com/Broadfi-music/Bario/commit/26d4e3501ce94c5219f6006f64687a388453bb06)
- Vatekeh/talk-stream-connect switched its audio rooms from LiveKit to Agora. The commit history indicates that the main work involved tokens, room controls, and SDK integration. [GitHub commit](https://github.com/Vatekeh/talk-stream-connect/commit/123d0658245e867c7ae37a1cd0bce5dcd5066021)

None of these records is sufficient to demonstrate that a mid-sized or large enterprise migrated to Agora. Public materials suggest that small teams primarily move to Agora for technical delivery and operational simplicity, rather than because of capacity limitations or sales support.

### Public Community Cases of Migrating Away from Agora

The public records that can be confirmed mainly involve individuals and small teams:

- A Flutter project reported crashes and extensive workarounds with Agora and switched to GetStream. This is a developer account and cannot be verified as a migration by a mid-sized or large enterprise. [Reddit discussion](https://www.reddit.com/r/FlutterDev/comments/1jprtrz/agora_vs_100ms_for_11_video_chat_which_one_to/)
- A voice app planned to switch from Agora to LiveKit Cloud, citing cost as the public motivation, but the discussion demonstrates intent only, not a completed migration. [Reddit discussion](https://www.reddit.com/r/WebRTC/comments/1jbut57/can_we_use_mediasoup_in_native_android/)
- After evaluating Agora, Daily, and Twilio, Hyperbeam chose to build its own P2P system. The company said that at approximately 150,000 MAUs, the expected cost of managed APIs could exceed $50,000 per month. [Reddit discussion](https://www.reddit.com/r/WebRTC/comments/sc55f5/audiovideo_calling_apis_like_agora_are_too/)

Hyperbeam did not reject Agora because Agora's product was poor. Its core technical requirement—streaming from server-side Chromium instances—called for WebRTC media streaming, not multi-party audio and video calls. In substance, Hyperbeam was not Agora's target customer.
- OnAir switched from Agora to LiveKit before its formal launch, making it a reverse case. It shows that early technology choices can still change easily, but it is not a migration by a large enterprise during production. [Hacker News discussion](https://news.ycombinator.com/item?id=42145419)

GitHub cases:

- The iCare project switched to Jitsi because of a null-pointer issue in its Agora bridge for Flutter Web. [GitHub commit](https://github.com/testingicare50-alt/icare-latest/commit/189158aaa9b159f3ec098fac7360988c159d8cf0)
  The current Web client uses Jitsi, while the mobile client uses ZegoCloud.
- The Mixy project reported approximately 60-second timeouts during Agora Web's WASM cold start, so the Web client switched to browser-native WebRTC and Firestore signaling. The mobile client still uses Agora. [GitHub commit](https://github.com/larrybesant-dev/mixy/commit/274c884cdb3e5d1963f0a9391db6f8b9277861a1)
- Bin-Aoun Study Office switched its voice service from Agora to LiveKit. [GitHub commit](https://github.com/Abdulmalek111/Bin-Aoun-Study-Office/commit/4efa77bf49f7c02967464698404f8cbb89411258)
- The Tropia livestreaming project migrated from Agora to LiveKit, replacing the backend token logic as well as the Flutter and Web implementations. [GitHub commit](https://github.com/VanNguyen100103/tropia_livestream/commit/80e9ee1b6e71203dac7d11dcab4ad3f10c9d0b73)

#### Agora SDK Fingerprints in Large Apps

AppBrain's Android SDK statistics as of July 2026 show:

- Agora code appears in more than 800 Android apps;
- Those apps have more than 10 billion cumulative installs;
- Identified leading apps include Netflix, Ludo King, Litmatch, Astrotalk, Binance, Getcontact, Talkie, FRND, and Ludo Club;
- Agora appears in 0.39% of all apps covered by AppBrain, representing 0.60% of installs; among leading apps, it appears in 1.69%, representing 1.54% of installs;
- The share of “new apps” for the period is shown as 0.00%, but this may reflect rounding, recognition lag, or a sampling issue. It should not be used to conclude that the number of new customers is zero.

These figures can be used only to build a pool of candidate companies. The presence of Agora in the APK of Netflix or Binance could reflect an actual RTC feature, a regional feature, an indirect dependency, dormant code, or a recognition error.

Source: [AppBrain Agora Android SDK statistics](https://www.appbrain.com/stats/libraries/details/agora/agora). The page states that its data comes from code-fingerprint identification in APKs.

### Reasons for Migration

| Reason | How it appears when migrating to Agora | How it appears when migrating away from Agora |
| --- | --- | --- |
| Capacity and global coverage | Avoid deploying SFUs/TURN and managing cross-region networks in-house | Once a company has its own global media infrastructure, the marginal value of a managed network declines |
| Reliability and SDK maturity | More complete mobile calling, push notification, poor-network, and cross-platform integrations | A platform-specific SDK failure, crash, cold start, or compatibility issue triggers replacement |
| Cost | Reduces early-stage team and operations costs | Per-minute charges exceed the cost of self-hosting or a competing solution as usage scales |
| Control and differentiation | Buying is prioritized for a faster launch | Once RTC becomes core to the experience, the company wants to customize routing, codecs, audio effects, and scheduling |
| Compliance and data sovereignty | Select a managed service that meets regional and certification requirements | Private deployment, data residency, or government-project requirements mandate self-hosting |
| Sales and service | Account support, migration assistance, and price discounts can help close the deal | Changes in support responsiveness, contract terms, or discounts can trigger a new vendor selection process |
| Vendor lock-in | A unified SDK reduces early complexity | Private tokens, signaling, and client APIs increase migration costs, encouraging companies to build an abstraction layer in advance |
