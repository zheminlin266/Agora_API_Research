# RTC、Voice AI 与 Agora 技术护城河研究

日期：2026-06-17

## 0. 先给结论

给非业内人士的核心判断是：RTC 的难，不在于“让两个人能打电话”这个演示，而在于“让全球不同设备、不同网络、不同场景下的人和 AI 都能低延迟、不中断、可打断、可观测、可扩容地实时交互”。这是一套跨网络传输、音视频编解码、弱网算法、多端 SDK、实时运维和客户场景理解的系统工程。

AI 会明显降低 RTC/Voice AI 创业的前 20% 难度：开发者可以更快做出演示、更快接入 ASR/LLM/TTS、更快处理降噪、转写、翻译、语音合成和 Agent 编排。但 AI 不会自动消灭后 80% 的生产级难度：端到端延迟、弱网、回声、噪声、打断、电话/SIP/WebRTC 互通、质量监控、成本控制、全球可用性和企业级 SLA 仍然很硬。

Agora 有机会成为 Voice AI 基础设施中的重要供应商，尤其是在弱网、全球实时路由、移动端/IoT 设备、低延迟语音交互和质量诊断场景中。但“Agora 成为绕不过去的供给瓶颈点”不是默认结论。反面证据很强：OpenAI Realtime 已支持 WebRTC/WebSocket/SIP，Twilio 控制电话入口并支持 Media Streams，LiveKit Agents 和开源 WebRTC/SFU 生态增长很快，Pion/Jitsi/mediasoup 等开源项目降低了自建门槛。Voice AI 的瓶颈也可能更多在模型、ASR/TTS、语音交互设计、垂直数据、电话分发和工作流集成，而不是单纯 RTC 网络。

因此，本报告的判断是：

1. RTC 基础能力会继续商品化，普通 SDK/标准 WebRTC 很难形成强护城河。
2. 高端 RTC 的护城河主要来自全球实时传输网络、弱网 QoE 算法、多端兼容、真实流量数据和实时运维体系。
3. AI 会提升 RTC 需求，也会把部分 RTC 能力抽象进模型平台和 Agent 框架，从而同时“做大蛋糕”和“压缩中间层议价权”。
4. Agora 可能成为重要供给方，但要成为瓶颈点，需要证明自己在 Voice AI 规模化生产中具有不可替代的 QoE、成本、生态和入口优势。

## 1. 资料覆盖范围

本次阅读和整理覆盖四类材料。

本地资料：

- `Agora_API_Research/Research_Report/agora_rtc_technical_moat.md`
- `Agora_API_Research/Resources/Agora_WP_SD-RTN-Delivers-RealTime-Internet-Advantages.pdf`
- `Agora_API_Research/Resources/Real-Time Communication with WebRTC.pdf`
- `Agora_API_Research/Resources/WebRTC 零基础开发者教程（中文）.pdf`
- `公告/2025FY 20-F.pdf`
- 2025 Q1 至 2026 Q1 的 Agora 季度公告和业绩材料
- 本地 npm/PyPI 下载量数据，包括 Agora、LiveKit、Twilio、Bandwidth 和中国 RTC 竞品包

GitHub 仓库：

- [0voice/audio_video_streaming](https://github.com/0voice/audio_video_streaming)

该仓库包含音视频开发书籍、协议 RFC、面试题、50 篇技术文章、开源项目索引、论文和实践项目。重点阅读了 WebRTC、RTP/RTCP、RTSP、RTMP、HLS、ICE、STUN、SDP、SRTP、UDP/TCP、码率控制、回声消除、音视频同步、Android 音视频、H264/AAC/FLV/PCM/YUV、直播链路和 WebRTC 连接建立相关资料。

外部资料：

- [WebRTC 官方概览](https://webrtc.org/getting-started/overview)
- [W3C WebRTC Recommendation](https://www.w3.org/TR/webrtc/)
- [Agora Conversational AI Engine](https://www.agora.io/en/products/conversational-ai-engine/)
- [LiveKit Agents 文档](https://docs.livekit.io/agents/)
- [LiveKit GitHub](https://github.com/livekit/livekit)
- [Twilio Voice Media Streams](https://www.twilio.com/docs/voice/media-streams)
- [OpenAI Realtime API 文档](https://platform.openai.com/docs/guides/realtime)
- [Jitsi Meet GitHub](https://github.com/jitsi/jitsi-meet)
- [mediasoup GitHub](https://github.com/versatica/mediasoup)
- [Pion WebRTC GitHub](https://github.com/pion/webrtc)
- WebRTC/低延迟视频/实时语音 Agent 相关论文与资料，包括 Mamba、VineetVC、LTS-VoiceAgent、AsyncVoice Agent、WhisperKit 等方向

说明：WebRTC Ventures 的 YouTube 频道已检索，但当前工具无法稳定取得访谈正文或字幕，因此本报告没有把无法核验的访谈观点作为直接证据。

## 2. 非业内人士如何理解 RTC

RTC 是 Real-Time Communication，实时通信。它和普通视频播放、直播、短视频、会议录播有一个关键区别：它要求双方或多方“边说边传、边听边回”，延迟通常要低到人类对话可以自然进行。

一个简单类比：

- 点播视频像“寄包裹”：可以提前缓存，晚几秒也无所谓。
- 普通直播像“电视转播”：延迟十几秒通常可以接受。
- RTC 像“现场对话”：对方说完你要立刻反应，中间卡顿、回声、抢话失败都会破坏体验。
- Voice AI 则更进一步：用户不仅要和人对话，还要和 AI 对话。AI 必须听懂、思考、回答、被打断、继续上下文，而且最好像真人一样自然。

因此，RTC 产品真正卖的不是“音视频 SDK”四个字，而是实时体验的确定性。

## 3. RTC 为什么难

### 3.1 网络天然不稳定

互联网不是为实时对话设计的。包会丢、会乱序、会抖动，移动网络会从 Wi-Fi 切到 5G，跨国链路会绕路，企业网络可能有防火墙，家庭路由器后面还有 NAT。

WebRTC 标准体系中，ICE、STUN、TURN 负责 NAT 穿透和中继；RTP/RTCP 负责媒体传输和质量反馈；DTLS/SRTP 负责加密；SDP 负责描述媒体协商。W3C WebRTC 标准把这些能力包装进浏览器 API，但这些协议本身仍然复杂。

0voice 仓库中关于 ICE、STUN、RTP/RTCP、SDP、UDP/TCP 的资料反复说明了同一个事实：RTC 不是单一协议，而是一组协议和算法的组合。

### 3.2 延迟、清晰度和稳定性互相拉扯

码率越高，画质/音质越好，但弱网下更容易卡；码率越低，稳定性好一些，但体验下降。为了维持体验，RTC 系统必须持续判断网络拥塞情况，并动态调整码率、分辨率、帧率、编码参数、重传、前向纠错、抖动缓冲等策略。

0voice 仓库中 WebRTC 发送方码率预估、码率控制、H264 编码、音视频同步等文章说明：实时体验不是“把音频包发出去”这么简单，而是每几十毫秒都在做取舍。

### 3.3 多端设备碎片化

浏览器、iOS、Android、Windows、macOS、嵌入式设备、智能玩具、车机、耳机、电话网络都有差异。麦克风、扬声器、摄像头、蓝牙链路、系统权限、硬件编码器、回声路径都可能不同。

这也是为什么多端 SDK 工程本身就是护城河。一个 demo 能跑，不代表在大量低端 Android 机、弱网国家、蓝牙耳机场景和企业防火墙环境里也能跑。

### 3.4 音频体验尤其敏感

Voice AI 会让音频 RTC 更重要。人可以容忍视频画面短暂变糊，但很难容忍语音断续、回声、抢话失败或 AI 迟迟不回应。

Voice AI 的典型链路是：

用户说话 -> VAD 判断是否有人声 -> 降噪/回声消除 -> ASR 转文字 -> LLM 思考 -> TTS 合成语音 -> RTC/电话网络回传 -> 用户听到回答。

这里任何一环慢 200 毫秒，都会影响“像真人对话”的感觉。若用户打断 AI，系统还要立刻停止播放、保留上下文、重新理解新意图。

### 3.5 真正难的是生产环境运维

RTC 服务上线后，客户最关心的问题往往是：

- 为什么巴西某运营商突然卡？
- 为什么某型号 Android 手机有回声？
- 为什么某城市晚高峰丢包飙升？
- 为什么这次连麦用户进房慢？
- 为什么 AI 客服被打断后没有停住？
- 为什么成本突然上升？

这要求供应商有实时质量监控、链路诊断、区域/运营商/机型维度的数据、自动调度和事故响应体系。Agora 的 SD-RTN 白皮书和本地技术护城河报告都把这类能力视为核心资产。

## 4. RTC 的技术护城河在哪里

可以把 RTC 护城河分成四层。

### 4.1 弱护城河：标准协议和基础 SDK

WebRTC、RTP、RTCP、ICE、STUN、TURN、SRTP、SDP 等协议是行业标准。开源实现也很多。一个团队可以用浏览器 WebRTC、Pion、LiveKit、Jitsi、mediasoup 等方案较快搭建可用系统。

因此，单纯“支持 WebRTC”“提供 SDK”“能音视频通话”不是强护城河。

### 4.2 中等护城河：多端 SDK、集成效率、文档和支持

SDK 的价值在于降低客户接入成本。对应用开发者来说，不想理解所有协议细节，只想快速实现通话、连麦、转写、录制、回调、统计、权限、设备切换。

这类能力能带来商业价值，但如果开源生态和云厂商方案足够成熟，议价权会被压缩。

### 4.3 强护城河：全球实时网络和弱网 QoE

Agora 本地资料反复强调 SD-RTN，即 Software Defined Real-Time Network。它的本质不是普通 CDN，而是为实时互动优化的传输网络和调度系统。

强护城河来自：

- 更低的端到端延迟
- 更好的弱网抗丢包能力
- 更稳定的跨国链路
- 更快的故障绕路
- 更细的实时质量监控
- 更丰富的真实流量数据
- 更长期的区域、运营商、设备适配经验

这类能力很难靠短期 AI 工具补齐，因为它需要真实网络覆盖、长期流量、工程经验和客户问题积累。

### 4.4 更高层护城河：场景闭环

如果 RTC 厂商只卖通用传输能力，长期会面临商品化压力。如果它能围绕具体场景形成闭环，护城河会更强。

例如：

- 游戏语音：低延迟、空间音频、反作弊、全球分区。
- 在线教育：低延迟互动、白板、录制、内容安全。
- 金融客服：合规、录制、审计、身份验证。
- 智能硬件：低功耗、芯片适配、边缘部署。
- Voice AI 客服：电话/SIP/WebRTC 接入、ASR/LLM/TTS 编排、打断、质检、实时监控。

Agora 的机会在于把 RTC 网络能力和 Voice AI 场景闭环结合起来。

## 5. AI 会如何改变 RTC 行业

### 5.1 AI 会降低演示和应用开发门槛

OpenAI Realtime API 支持 WebRTC、WebSocket 和 SIP 等连接方式；LiveKit Agents 让开发者把 Python/Node 程序作为实时参与者接入房间；Twilio Media Streams 可以把电话音频通过 WebSocket 接入应用，并支持向通话中回传音频；Agora Conversational AI Engine 也宣称可以把任意 LLM、ASR、TTS 连接到实时语音 Agent。

这意味着创业公司今天做一个 Voice AI demo，比三五年前容易很多。过去要自己处理媒体链路、协议、ASR、TTS、LLM、电话接入，现在可以拼装平台能力。

### 5.2 AI 会优化音视频体验

AI 可以用于：

- 降噪
- 回声消除
- 语音增强
- 自动字幕
- 实时翻译
- 超分辨率
- 智能码率控制
- 说话人分离
- 语音活动检测
- 端侧 ASR/TTS
- 数字人或 talking-head 压缩

相关论文中，Mamba 一类工作尝试用强化学习协调 WebRTC 的码率、分辨率和帧率；VineetVC 一类工作尝试在低带宽场景下用 AI 重建说话人视频；WhisperKit 代表端侧实时 ASR 的方向。这些都说明 AI 会成为 RTC 体验优化工具。

### 5.3 AI 也会削弱部分 RTC 中间层

AI 模型平台如果直接提供实时语音入口，就可能绕过一部分独立 RTC 厂商。OpenAI Realtime 支持 WebRTC/WebSocket/SIP，说明模型平台正在把实时传输能力纳入自身开发者平台。

同时，LiveKit Agents 这类开源 Agent 框架会让创业者用开源实时媒体层加模型 API 搭出完整产品。Twilio 则在电话入口有天然优势，很多企业 Voice AI 场景首先是电话客服、外呼、IVR，而不是 App 内语音房。

因此，AI 对 RTC 厂商不是单向利好，而是双刃剑：它带来更多实时交互需求，也让更上游的模型平台和更下游的应用平台有机会吸收 RTC 能力。

## 6. AI 是否大幅降低 RTC/Voice AI 创业难度

答案要拆开看。

AI 大幅降低了以下难度：

- 做 demo 的难度
- 接入语音识别、语音合成和大模型的难度
- 做降噪、转写、摘要、质检、翻译的难度
- 用开源框架搭实时 Agent 的难度
- 垂直应用团队理解音视频底层协议的必要性

但 AI 没有大幅降低以下难度：

- 全球低延迟稳定传输
- 弱网体验优化
- 电话、SIP、WebRTC、App、网页、硬件之间的互通
- 生产环境下的打断体验
- 回声、噪声、蓝牙、低端机适配
- 企业客户的 SLA、合规、录制和审计
- 实时质量监控和事故定位
- 单位通话分钟成本
- 大规模并发和峰值扩容

所以更准确的说法是：AI 大幅降低了“应用层创业”的门槛，但没有大幅降低“基础设施级 RTC 供应商”的门槛。

这对行业格局的含义是：未来会出现更多 Voice AI 应用公司，但能否出现更多 Agora 级别的 RTC 基础设施公司，仍然要看网络、SDK、运维、成本和客户规模。

## 7. Voice AI 高增长下，Agora 能否成为绕不过去的供给瓶颈点

### 7.1 支持 Agora 成为重要供给方的理由

第一，Voice AI 的体验高度依赖实时音频。

如果用户和 AI 对话要像真人，延迟、打断、降噪、回声消除、弱网稳定性都很重要。这些正是传统 RTC 厂商长期解决的问题。Agora 的 Conversational AI Engine 明确围绕任意 LLM/ASR/TTS 接入、低延迟、打断、噪声/回声处理和全球网络优化展开。

第二，全球实时网络不是一夜之间能复制的。

Agora 的 SD-RTN 如果在跨国、弱网、移动端、IoT 和实时诊断上确实领先，就可能成为客户规模化时的首选。Voice AI 从 pilot 走向 production 后，客户会从“能不能跑”转向“能不能稳定、便宜、可观测地跑”。

第三，Agora 已经把公司叙事转向 Conversational AI。

本地 2025 至 2026 季度材料显示，Agora 推出了 Conversational AI Engine、Conversational AI Studio、Agent Studio，并披露在 AI 玩具、语言学习、呼叫中心等场景有客户进入生产或早期采用。2025 Q3/Q4 Agora 口径 NRR 分别达到 108%/109%，说明国际业务有复苏和扩张信号。

第四，开发者使用量仍在增长。

本地 npm/PyPI 数据显示，Agora 传统 RTC 包仍有增长。例如 `rtc-sdk-total` 最近 13 周下载量较前 13 周增长约 55.8%，`react-native-agora` 增长约 161.9%。这说明 Agora 并不是一个被开发者完全抛弃的生态。

### 7.2 反面观点：Agora 不会成为供给瓶颈的理由

第一，Voice AI 的主要瓶颈未必在 RTC。

很多 Voice AI 产品真正卡住的是模型响应、ASR 准确率、TTS 自然度、打断逻辑、业务系统集成、电话触达、客户数据和工作流，而不是单纯的音频包传输。LTS-VoiceAgent 和 AsyncVoice Agent 方向的研究也说明，实时语音 Agent 的核心矛盾常常是“听、想、说”的协同和延迟，而不只是网络传输。

第二，OpenAI 等模型平台可以直接提供实时连接。

OpenAI Realtime API 已支持 WebRTC、WebSocket 和 SIP。对许多开发者来说，如果模型平台同时提供语音模型、实时连接、工具调用和会话管理，他们未必需要额外选择独立 RTC 厂商。模型平台越上移，越可能把一部分 RTC 能力内嵌化。

第三，Twilio 在电话入口有强位置。

企业 Voice AI 的高频场景是客服、外呼、销售跟进、IVR 和呼叫中心。这些场景的入口常常是 PSTN/电话网络，而 Twilio Programmable Voice 和 Media Streams 天然贴近电话工作流。Twilio 文档明确支持从通话中获取原始音频、做实时转写、情绪分析、语音认证，以及和 AI chatbot 做双向实时语音互动。

如果 Voice AI 首先在电话客服爆发，Twilio 可能比 Agora 更接近需求入口。

第四，LiveKit 正在形成开源实时 Agent 生态。

LiveKit 官方文档把 Agents 定义为 voice、video、physical AI agents 的实时框架，允许 Python/Node 程序作为实时参与者接入房间，并与任意 AI provider 连接。LiveKit GitHub 项目是开源 WebRTC SFU，支持多端 SDK、UDP/TCP/TURN、多区域部署、Kubernetes、自托管和云托管。

本地 npm/PyPI 数据也显示，LiveKit 的 AI Agent 相关包下载量远高于 Agora 新 AI 包。例如 `@livekit/agents` 最近完整周约 22.2 万次下载，最近 13 周约 199.7 万次；LiveKit Python 相关包也在百万级周下载。相比之下，Agora agent 相关 npm 包目前仍是很小基数。这是 Agora 不成为默认瓶颈的强反证。

第五，开源 WebRTC/SFU 生态降低了供应商锁定。

Jitsi、mediasoup、Pion、LiveKit 等项目覆盖视频会议、SFU、WebRTC 协议栈和服务端实现。大客户或技术团队可以选择自建、混合部署或多供应商架构。开源不等于免费解决一切问题，但它降低了“只有某一家能做”的可能性。

第六，云厂商和垂直应用可能把 RTC 商品化。

对垂直 Voice AI 公司来说，真正差异化可能来自行业数据、销售渠道、业务流程、合规、效果闭环，而不是 RTC。它们可能把底层通信当作可替换组件，在 Agora、Twilio、LiveKit、OpenAI direct、云厂商 RTC 之间动态选择。

第七，成本压力会限制瓶颈议价权。

Agora 2026 Q1 材料显示，毛利率降至约 63.4%，公司解释与产品组合变化、带宽/服务器成本和 AI 产品成本有关。这提示 Voice AI 增长不必然转化为高毛利瓶颈利润。如果音频分钟、模型调用、服务器、带宽成本都在上升，供应商需要证明单位经济模型足够好。

### 7.3 判断框架

Agora 是否能成为 Voice AI 的绕不过去瓶颈，取决于五个条件：

1. 它是否掌握关键入口：Web/App/IoT/电话/SIP/硬件中至少一个高价值入口。
2. 它是否有明显 QoE 优势：弱网、跨国、低端设备、打断、降噪、回声消除明显优于替代方案。
3. 它是否能形成成本优势：同等体验下单位分钟成本更低，毛利率可维持。
4. 它是否能形成开发者生态：Agent SDK、模板、插件、示例、社区和第三方集成快速增长。
5. 它是否能进入客户生产系统：不是 pilot 多，而是生产流量、续约、NRR、并发和客户案例持续增长。

当前证据下，更稳妥的判断是：

- Agora 有机会成为 Voice AI RTC 层的重要供应商。
- Agora 还没有证明自己是不可绕过的瓶颈。
- 若 OpenAI/Twilio/LiveKit 等继续上移和扩张，Agora 更可能是“高质量实时音频基础设施选项之一”，而不是行业唯一瓶颈。

## 8. 对 Agora 护城河的分层打分

| 能力 | 护城河强度 | 说明 |
| --- | --- | --- |
| UDP/RTP/WebRTC 标准协议 | 弱 | 标准化、开源实现多，难以独占 |
| 普通音视频 SDK | 弱到中 | 有集成价值，但可替代方案多 |
| 多端 SDK 兼容 | 中 | 需要长期工程积累，尤其是移动端和嵌入式 |
| 弱网 QoE 算法 | 中到强 | 真实网络数据、算法和调参经验重要 |
| SD-RTN 全球实时网络 | 强 | 节点、调度、质量监控和运维积累较难复制 |
| 实时质量诊断系统 | 中到强 | 企业客户生产环境很看重 |
| Conversational AI Engine | 中，待验证 | 方向正确，但生态和规模仍需证明 |
| Agent Studio/低代码工具 | 中 | 降低接入门槛，但容易被模型平台和开源框架竞争 |
| 电话/PSTN 入口 | 偏弱 | Twilio 等通信平台更强 |
| 开源/开发者生态对抗 | 当前偏弱 | LiveKit/Twilio 下载量和开源声量是压力项 |

## 9. 投资或研究中应重点跟踪的指标

如果要判断 Agora 是否真的在 Voice AI 中形成瓶颈，应持续看以下指标：

1. Conversational AI 相关收入占比，而不仅是产品发布数量。
2. Voice AI 生产流量，包括通话分钟、并发频道、活跃客户数。
3. Agora 国际业务 NRR 是否持续高于 100%。
4. 毛利率在 AI 产品占比提升后是否企稳。
5. Agent SDK/npm/PyPI 下载量是否追上 LiveKit/Twilio。
6. 是否出现大客户把 Agora 作为核心实时语音层的公开案例。
7. 是否在电话/SIP、IoT、智能硬件、车载、AI 玩具等入口建立深合作。
8. 相比 OpenAI direct、Twilio、LiveKit、云厂商 RTC，是否有可量化 QoE 优势。
9. 是否有跨国弱网、低端设备、噪声环境下的真实 benchmark。
10. 客户是否把 Agora 从“可替换供应商”视为“生产稳定性关键供应商”。

## 10. 一句话总结

RTC 的护城河不在“能连上”，而在“复杂真实世界里始终好用”。AI 会让更多团队能做 Voice AI，也会让模型平台、通信平台和开源框架吸收部分 RTC 能力。Agora 的机会是真实存在的，但要成为绕不过去的瓶颈，还需要用生产流量、生态增长、QoE 优势和经济模型证明自己不仅是一个好供应商，而是客户难以替换的实时语音基础设施。

