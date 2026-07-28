# OpenAI 与 LiveKit：从 ChatGPT 语音模式共研，到语音代理基础设施生态
## AI 语音和实时通信不是一回事

所谓 AI 语音，至少包含两层：

- **模型层**：模型要听懂人说的话、理解上下文、决定回答内容，并生成声音。这里会涉及 STT（Speech-to-Text，自动语音识别：把声音转成文字）、TTS（Text-to-Speech，文本转语音：把文字读成声音）和 speech-to-speech（语音到语音：声音直接进、声音直接出）。
- **通信和运行层**：用户的麦克风声音要经过不稳定的 Wi-Fi 或移动网络低延迟地到达服务器；服务器生成的声音也要顺畅回来。系统还要处理丢包、断线、回声、多人同时说话、用户打断模型，以及把电话分配给正确的代理。

早期的语音助手通常是一条流水线：

**典型语音助手链路：** 人说话 → STT 把声音写成文字 → 文本模型生成文字答案 → TTS 把答案读成声音 → 用户听到

这条路容易理解，但每一站都可能丢掉信息。人的语气、笑声、停顿和背景声音，经过“声音—文字—声音”几次转换后不一定还保留。LiveKit 解决的主要是第二层，OpenAI 主要解决第一层；2024 年之后，两家的接口把这两层更紧密地接到了一起。

## OpenAI 在 AI 语音领域的发展历史

### 1. 2022 年：先解决“听懂”，Whisper 打开入口

2022 年 9 月 21 日，OpenAI 发布 Whisper。Whisper 是 ASR 模型，简单说就是“把人说的话尽量准确地写下来”。它使用约 68 万小时的多语言、多任务语音数据训练，目标是适应口音、噪音、专业词和不同语言。[OpenAI：Introducing Whisper](https://openai.com/index/whisper/)

Whisper 的意义不只是一个模型：它让开发者可以把语音识别作为开放、可复用的基础能力；也为后来 ChatGPT Voice 的“先把用户说的话转成文字”提供了重要基础。它还显示了 OpenAI 当时的路线：先把语音拆成可分别优化的模块，再逐步向真正的实时语音对话推进。

与此同时，OpenAI 在 2022 年末已经开始开发 Voice Engine。Voice Engine 是一种 TTS 模型，能够根据文字和约 15 秒的声音样本生成接近原说话人的声音。[OpenAI：Voice Engine 的技术与安全研究](https://openai.com/index/expanding-on-how-voice-engine-works-and-our-safety-research/) 这项能力后来没有直接大规模开放，因为声音克隆容易被用于冒充、诈骗和误导。

这里要区分两件事：**Whisper 主要负责“听”，Voice Engine 主要负责“说”**。它们还不是一个能够自己理解、决定和回应的完整语音代理。

### 2. 2023 年 9 月至 11 月：ChatGPT Voice Mode 让语音成为大众产品

2023 年 9 月 25 日，OpenAI 宣布 ChatGPT 开始逐步加入语音和图像能力，先向 Plus 和 Enterprise 用户推送。官方说明里，早期 Voice Mode 使用三段式流水线：Whisper 把语音转成文字，中间的 GPT-3.5 或 GPT-4 负责回答，最后由 TTS 模型把文字变回声音。[OpenAI：ChatGPT can now see, hear, and speak](https://openai.com/index/chatgpt-can-now-see-hear-and-speak/)

用大白话说，这一代 ChatGPT Voice 是“先听写、再思考、再朗读”。它已经能进行来回对话，但还不是严格意义上的“一个模型直接听声音、直接用声音回应”。

2023 年 11 月，OpenAI 发布 TTS API（应用程序接口：软件之间约定如何调用能力），提供六种预设声音。官方后来解释，这个 TTS API 同样由 Voice Engine 提供底层能力，但只开放由专业配音演员参与制作的预设声音，没有让普通用户上传任意声音来克隆。[OpenAI：Expanding on how Voice Engine works](https://openai.com/index/expanding-on-how-voice-engine-works-and-our-safety-research/)

2023 年 11 月 21 日，ChatGPT Voice 向所有用户开放。[ChatGPT Release Notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes) 这一步把语音从研究展示变成高频消费产品，也让 OpenAI 开始面对延迟、打断、口音、噪声、情绪依赖和声音安全等真实问题。

### 3. 2024 年 3 月：Voice Engine 公开预览，但选择不全面开放

2024 年 3 月 29 日，OpenAI 公开介绍 Voice Engine 的小规模预览。它用文字和 15 秒语音样本生成自然、接近原说话人的声音，已被少量可信合作方用于阅读辅助、教育和视频翻译。[OpenAI：Navigating the challenges and opportunities of synthetic voices](https://openai.com/index/navigating-the-challenges-and-opportunities-of-synthetic-voices/)

OpenAI 同时明确表示暂时不全面发布 Voice Engine，并提出征得原说话人同意、披露声音由 AI 生成、对音频做来源追踪、避免生成过于接近知名人物的声音等安全措施。这显示出两条路线：预设声音路线更适合产品化；自定义声音路线效果更强，但风险更高，主要停留在小规模研究和合作测试。

### 4. 2024 年 5 月：GPT-4o 把语音从外挂模块推进到模型本身

2024 年 5 月 13 日，OpenAI 发布 GPT-4o。“o”是 omni 的缩写，意思是“全模态”：模型可以接收文字、音频、图像和视频的组合，也可以输出文字、音频和图像的组合。[OpenAI：Hello GPT-4o](https://openai.com/index/hello-gpt-4o/)

GPT-4o 相比旧 Voice Mode 最关键的变化，是不再完全依赖“STT → 文本模型 → TTS”三段式拼接。OpenAI 称，旧版语音平均延迟约为 2.8 秒到 5.4 秒，而 GPT-4o 对音频的响应最低可以到约 232 毫秒，平均约 320 毫秒，接近自然交谈中的反应速度。

旧流水线更容易看到“说了什么”，不容易直接保留“怎么说的”。GPT-4o 可以更直接地利用语气、停顿、笑声和背景声音，也可以生成带节奏、情绪和非语言声音的回答。其系统卡专门评估了未经授权的声音生成、说话人识别、版权内容和敏感属性推断等风险。[GPT-4o System Card](https://openai.com/index/gpt-4o-system-card/)

GPT-4o 并非发布当天就全面开放。OpenAI 先开放文字和图像能力，音频能力还要继续做基础设施、体验和安全测试；Advanced Voice Mode（高级语音模式：更低延迟、支持打断和更自然语气的实时语音模式）随后才逐步进入测试。

### 5. 2024 年 7 月至 9 月：Advanced Voice Mode 从展示走向真实用户

2024 年 7 月 30 日，OpenAI 开始向一小部分 ChatGPT Plus 用户推送 Advanced Voice Mode 的 alpha 测试（小规模测试版）。这次推送先聚焦语音，不等于 5 月演示里的所有视频、屏幕共享和其他能力都同时上线。[TechCrunch 对首次推送的报道](https://techcrunch.com/2024/07/30/openai-releases-chatgpts-super-realistic-voice-feature/)

到 2024 年 9 月，Advanced Voice Mode 扩大到更多付费用户。这个阶段的重点不只是生成声音，还包括：用户说到一半时能否打断模型、模型能否判断用户说完、停顿和噪声会不会被误判为新指令、上下文被打断后能否正确恢复，以及声音是否自然而不制造过强的冒充效果。

### 6. 2024 年 10 月 1 日：Realtime API 把实时语音交给开发者

2024 年 10 月 1 日，OpenAI 发布 Realtime API 公测版。开发者可以通过持续连接，让 GPT-4o 接收音频并实时输出音频，不再需要自己把 Whisper、文本模型和 TTS 拼起来。Realtime API 还支持函数调用（模型请求外部程序执行动作，例如查询订单、改预约或调用数据库），并能处理用户打断。[OpenAI：Introducing the Realtime API](https://openai.com/index/introducing-the-realtime-api/)

OpenAI 同时写明，发布前已经和 LiveKit、Agora 一起制作音频组件，处理回声消除、断线重连和声音隔离；还和 Twilio 一起把 Realtime API 接入电话。这说明 OpenAI 从一开始就没有把所有客户端和通信问题都自己包办，而是通过多家基础设施伙伴把模型接到真实应用里。

### 7. 2024 年 10 月 3 日：OpenAI 与 LiveKit 的合作公开化

2024 年 10 月 3 日，LiveKit 正式宣布与 OpenAI 合作，把 ChatGPT Advanced Voice 背后的端到端技术做成开发者可用的 API。[LiveKit：OpenAI and LiveKit partner to turn Advanced Voice into an API](https://livekit.com/blog/openai-livekit-partnership-advanced-voice-realtime-api)

LiveKit 披露的架构是：

1. ChatGPT 应用用 LiveKit 客户端 SDK 采集用户语音。
2. 用户语音通过 LiveKit Cloud 传到 OpenAI 的语音代理。
3. 语音代理把音频送给 GPT-4o。
4. GPT-4o 生成音频数据，再返回给语音代理。
5. 语音代理通过 LiveKit Cloud 把声音送回用户设备。

关键不是 LiveKit 代替 OpenAI 运行 GPT-4o，而是 LiveKit 负责“最后一公里”和“持续运行”：接入用户设备，在弱网中尽量保持流畅，处理缓冲、打断、重连、负载均衡（把新会话分到合适的代理实例）和电话接入。

### 8. 2024 年 12 月：OpenAI 提供不经 LiveKit 的直接 WebRTC 路径

2024 年 12 月 17 日，OpenAI 为 Realtime API 增加直接 WebRTC 支持。WebRTC 是浏览器和移动端常用的实时音视频通信标准；过去开发者需要借助 LiveKit 等中间层把服务器和客户端接起来，现在可以直接使用 OpenAI 的 WebRTC 接入方式。[OpenAI：o1 and new tools for developers](https://openai.com/index/o1-and-new-tools-for-developers/)

这是关系可能开始“去单点依赖”的重要迹象，但不等于合作退潮：对 OpenAI，直接 WebRTC 减少中间环节；对 LiveKit，直接连接只解决“能否把音频送到模型”，并不完整解决电话、代理编排、状态、监控、跨模型切换和大规模运营；对开发者，两条路可以并存，小型应用直连 OpenAI，复杂应用使用 LiveKit。

### 9. 2025 年：从一个实时模型，扩展成语音代理产品线

2025 年 3 月 20 日，OpenAI 发布 `gpt-4o-transcribe`、`gpt-4o-mini-transcribe` 和 `gpt-4o-mini-tts` 等新一代音频模型。前两者提高语音转文字准确率，后者允许开发者更自然地控制说话风格；OpenAI 同时建议，追求低延迟语音到语音体验的开发者继续使用 Realtime API。[OpenAI：Introducing next-generation audio models](https://openai.com/index/introducing-our-next-generation-audio-models/)

2025 年 8 月 28 日，Realtime API 正式 GA（General Availability，正式可用于生产），并推出 `gpt-realtime`。它增加了图像输入、MCP（让模型通过统一协议连接外部工具和数据）和 SIP（电话系统常用的会话建立协议）电话接入。[OpenAI：Introducing gpt-realtime](https://openai.com/index/introducing-gpt-realtime/)

这代表 OpenAI 的语音战略从“让 ChatGPT 会聊天”转为“让语音代理能完成工作”：接电话、查资料、调用工具、处理订单、跨语言沟通，并在动作执行时保持对话。

### 10. 2026 年：向连续对话、实时翻译和更强行动能力推进

2026 年 5 月 7 日，OpenAI 发布 GPT-Realtime-2、GPT-Realtime-Translate 和 GPT-Realtime-Whisper，分别面向更强的实时推理、实时翻译和实时转写。[OpenAI：Advancing voice intelligence with new models in the API](https://openai.com/index/advancing-voice-intelligence-with-new-models-in-the-api/)

2026 年 7 月 8 日，OpenAI 发布 GPT-Live，并将其用于新的 ChatGPT Voice。GPT-Live 采用 full-duplex（全双工：模型可以一边听、一边说，而不是严格轮流说话）的设计，能够在用户说话时继续听，在需要时插话、等待或调用工具；如果问题需要搜索和深度推理，它可以让后台的更强模型处理，同时保持前台对话不断。[OpenAI：Introducing GPT-Live](https://openai.com/index/introducing-gpt-live/)

OpenAI 的演进路线可以概括为：

**OpenAI 的演进路线：** 先把语音转成文字 → 把听、想、说串起来 → 一个模型直接处理语音输入和语音输出 → 实时打断、工具调用、电话和多语言 → 持续听说，并把复杂任务交给后台模型完成

## LiveKit 的发展历程：从 WebRTC 基础设施到语音代理平台

### 1. 2021 年：从开源实时音视频基础设施起步

LiveKit 于 2021 年 7 月 7 日公开发布。它最初不是 AI 公司，而是开源的实时音视频基础设施项目，让开发者可以在自己的产品里加入语音房间、视频会议和直播，而不必从头处理复杂的 WebRTC 细节。[LiveKit：And…we’re Live(Kit)!](https://livekit.com/blog/and-were-live-kit)

LiveKit 的核心组件包括 SFU（Selective Forwarding Unit，选择性转发单元：服务器接收并转发音视频流，不要求每个用户都直接连接所有人）和各平台客户端 SDK。它解决的是“多人或设备之间如何稳定传输媒体”，而不是“模型如何理解语言”。

### 2. 2022 年：LiveKit Cloud，把开源代码变成全球网络

2022 年 10 月 24 日，LiveKit 发布 LiveKit Cloud。Cloud 是托管版的 LiveKit：开发者不用自己搭建、扩容和监控大规模 WebRTC 集群，就可以使用全球分布的实时音视频网络。[LiveKit：Announcing LiveKit Cloud](https://livekit.com/blog/announcing-livekit-cloud)

LiveKit Cloud 的重要设计是开源版和云版使用相同的 API 与 SDK，开发者可以在自建和云托管之间切换。这种“先开源、再托管”的路线，使 LiveKit 更容易成为其他 AI 公司和开发者的底层传输层。

### 3. 2023 年：从人与人实时通信，转向人与 AI 实时通信

LiveKit 后来的 Series B 回顾称，LiveKit 在 2023 年 9 月与 OpenAI 一起推出 ChatGPT Voice Mode，同时发布了 LiveKit Agents；不过，LiveKit 面向公众详细介绍 Agents 的正式博客是在 2024 年 1 月 18 日。[LiveKit：Series B 回顾](https://livekit.com/blog/livekits-series-b) [LiveKit：An open source stack for real-time multimodal AI](https://livekit.com/blog/open-source-realtime-multimodal-ai)

这两条信息合起来说明：2023 年 9 月前后，LiveKit 已经开始参与 OpenAI Voice Mode 这类真实产品的工程工作；2024 年 1 月，LiveKit 把从这些项目中学到的能力公开做成 Agents 框架。因此，LiveKit 的 AI 转型并非先做一个通用框架再找模型合作，而是先在真实语音产品里遇到问题，再把解决方案抽出来。

LiveKit Agents 主要处理四类麻烦：接收实时音频和视频；缓冲、切分并播放模型音频；判断用户什么时候说完，也就是 VAD（Voice Activity Detection，语音活动检测：判断当前有没有人在说话）和 turn detection（轮次检测：判断这一轮发言是否结束）；管理代理连接、负载、失败重连和水平扩容。

### 4. 2024 年 1 月至 6 月：Agents 框架和共研经验公开化

2024 年 1 月 18 日，LiveKit 正式介绍 Agents。它把实时媒体、后端 SDK、插件、任务调度和负载均衡放进一个开源框架，并支持 OpenAI、Whisper、Deepgram、ElevenLabs 等多个模型或语音服务。[LiveKit Agents 官方发布](https://livekit.com/blog/open-source-realtime-multimodal-ai)

2024 年 6 月 4 日，LiveKit 宣布获得 2250 万美元 Series A，并表示在过去 18 个月里已经与 OpenAI、Character.AI 等团队合作，让它们的模型具备“看、听、说”的能力；LiveKit 同时称，Agents 吸收了这些语音助手项目的经验。[LiveKit：Series A](https://livekit.com/blog/livekit-series-a)

这篇融资文章是双方关系早期最重要的公开线索之一。它没有给出合同、采购额或股权投资信息，但至少说明合作不是一次临时的 API 适配，而是足以影响 LiveKit 产品路线的工程合作。

### 5. 2024 年 10 月：LiveKit 成为 Advanced Voice 的开发者化桥梁

2024 年 10 月 3 日，LiveKit 宣布与 OpenAI 的明确合作，并发布支持 OpenAI Realtime API 的 Multimodal Agent API（多模态代理接口：把文本、音频、图像等输入输出统一放进代理流程）。

LiveKit 解释，OpenAI 的语音模型通过 WebSocket（服务器与客户端之间保持长连接的通信方式）接收和输出音频，但面向浏览器和手机时，网络丢包会导致声音卡顿；WebRTC 更适合客户端实时媒体传输，而直接使用 WebRTC 又涉及复杂的信令、编解码、网络适应和扩容问题。LiveKit Cloud 正好位于这两层之间。[LiveKit：OpenAI and LiveKit partner](https://livekit.com/blog/openai-livekit-partnership-advanced-voice-realtime-api)

双方的互补关系可以画成：

**双方的技术分工：** 用户的麦克风、浏览器、手机、电话 →（WebRTC / SIP）→ LiveKit Cloud + LiveKit Agents →（WebSocket）→ OpenAI Realtime API / GPT-4o → 语音回答、工具调用、业务动作

OpenAI 提供模型能力，LiveKit 提供实时连接和代理运行环境。开发者可以较快做出“像 Advanced Voice 一样”的产品，同时加入自己的前端、业务工具和电话系统。

### 6. 2025 年：LiveKit 从 OpenAI 适配层扩展成多模型平台

2025 年 4 月 10 日，LiveKit 发布 Series B，宣布融资 4500 万美元，并把目标描述为构建“为语音 AI 代理提供的一体化平台”。文章回顾称，LiveKit Cloud 已经服务超过 10 万名开发者，Agents 也从开源框架发展为覆盖工作流、电话、云端部署和代理扩容的产品。[LiveKit：Series B](https://livekit.com/blog/livekits-series-b)

这时 LiveKit 与 OpenAI 的关系出现变化：合作仍然存在，但 LiveKit 不再只围绕 OpenAI 设计。它开始把语音代理视为独立的软件类别，并支持开发者在不同 STT、LLM（Large Language Model，大语言模型：负责理解和生成语言）和 TTS 之间切换。

### 7. 2026 年：覆盖开发、测试、部署和监控

2026 年 1 月 22 日，LiveKit 宣布 Series C，估值达到 10 亿美元。LiveKit 将语音 AI 描述为一种新的实时、有状态应用：一段对话可能持续几分钟甚至几小时，系统要持续听、思考、回应，还要维护整段上下文。[LiveKit：Series C](https://livekit.com/blog/livekit-series-c)

该文章还提到，LiveKit Agents 借鉴了 ChatGPT Voice Mode 的工作经验，每月下载量超过 100 万次，提供数百种 AI 模型集成，并自动处理轮次检测和打断；LiveKit 还推出 Agent Builder，让用户可以用模板和图形化方式创建代理。

截至 2026 年 7 月，LiveKit 官方 OpenAI 集成文档仍支持 OpenAI Realtime API、GPT-4o、GPT-5、OpenAI STT 和 OpenAI TTS。文档明确，LiveKit Agents 可以作为前端 WebRTC 与 OpenAI 后端 WebSocket 之间的桥梁，并自动处理音频缓冲、文字与音频同步、打断和电话接入。[LiveKit：OpenAI integration](https://docs.livekit.io/agents/integrations/openai/) [LiveKit：OpenAI Realtime plugin](https://docs.livekit.io/agents/models/realtime/plugins/openai/)

## OpenAI & LiveKit 合作关系的四个阶段

| 阶段        | 具体时间                 | 发生了什么                                                                                                  | 关系变化的线索                                                                                                     | 判断                                                                |
| --------- | -------------------- | ------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| 隐性共研      | 至少 2023 年 9 月前后，可能更早 | ChatGPT Voice Mode 上线；LiveKit 后来称双方共同完成该产品                                                             | LiveKit 2025 年回顾使用“together with OpenAI”；OpenAI 2024 年 10 月披露 ChatGPT 应用使用 LiveKit SDK 和 LiveKit Cloud      | 已有深度工程合作，但当时没有公开宣布合同或独家关系                                         |
| 技术深入      | 2024 年 1 月至 10 月     | LiveKit 发布 Agents；OpenAI 发布 GPT-4o、Advanced Voice 和 Realtime API                                       | LiveKit 将 OpenAI Realtime API 封装进 Multimodal Agent API；双方公开描述 ChatGPT Voice 的真实架构                           | 合作从产品内部工程走向开发者平台，LiveKit 角色变得清晰                                   |
| 共同产品化     | 2024 年 10 月至 2025 年  | 开发者可以用 LiveKit 构建类似 Advanced Voice 的应用；OpenAI 推进 Realtime API、音频模型和生产能力                                | LiveKit 提供 OpenAI 插件；OpenAI Realtime API 采用实时音频、函数调用、打断和电话能力                                                | 双方互相导流：OpenAI 给 LiveKit 带来旗舰模型和案例，LiveKit 给 OpenAI 补足通信、电话和代理运行能力 |
| 开放生态与可能淡化 | 2025 年至 2026 年 7 月   | OpenAI 提供直接 WebRTC、正式版 Realtime API、gpt-realtime 和 GPT-Live；LiveKit 支持数百个模型并发展自己的 Inference 和 Agent 平台 | OpenAI 可以绕过 LiveKit 直接连接客户端；LiveKit 公开支持其他模型和自有平台；最新 OpenAI Voice 发布重点是 GPT-Live 内部架构，没有再把 LiveKit 作为核心产品叙事 | 关系仍在，但从“共同打造一个标杆产品”转为“OpenAI 是 LiveKit 的重要模型伙伴之一”                 |

## 为什么会从深度合作转向可能淡化

### 1. OpenAI 有动力把通信层逐渐收回自己手里

合作初期，OpenAI 最需要的是快速把 GPT-4o 的声音送到真实用户设备。LiveKit 已经有成熟的 WebRTC、全球节点、重连和媒体处理能力，因此是自然的合作对象。

但 Realtime API 成熟后，OpenAI 有三个理由提供自己的直接接入：

- **降低接入门槛**：开发者只需要 OpenAI API，不必再理解另一套平台的账号、计费和运行方式。
- **减少中间层**：更少的转发环节，通常更容易优化延迟、故障排查和数据边界。
- **掌握产品节奏**：OpenAI 可以直接控制模型、协议、客户端 SDK 和语音产品组合。

2024 年 12 月已经出现直接 WebRTC 接入，2025 年 8 月 Realtime API 正式可用于生产，2026 年 OpenAI 又继续沿着 GPT-Realtime 和 GPT-Live 自己的产品线推进。这些都是“OpenAI 不必永远依赖某一个实时通信供应商”的迹象。

### 2. LiveKit 有动力从单一模型伙伴变成模型中立的平台

LiveKit 的长期价值不是某个单一模型的声音，而是整套实时代理基础设施。企业可能今天用 OpenAI，明天改用其他模型，或者同时用多个模型：一个负责实时对话，一个负责长推理，一个负责转写或声音合成，最后通过电话、浏览器、移动端和机器人交付。

LiveKit 的公开产品路线已经朝这个方向走：Agents 有插件系统，官方文档支持 OpenAI、Azure OpenAI 以及其他提供商；Series C 文章强调数百种模型集成。对 LiveKit 来说，OpenAI 越强越好，但不应该成为平台唯一上游。

### 3. 双方合作层级发生变化

早期合作更像“共同解决一个具体产品的难题”：ChatGPT Voice 要如何低延迟地听和说？

现在合作更像“模型层和基础设施层的标准化适配”：OpenAI 维护 Realtime API，LiveKit 维护插件和代理框架，开发者可以根据应用需要选择是否加上 LiveKit。

这不是关系变差，而是产品成熟后的常见变化：从定制共研转为标准接口，从单一项目转为可替换的生态组件。

## 哪些证据支持“仍在合作”，哪些证据支持“可能淡化”

### 支持“仍在合作”的证据

1. LiveKit 当前 OpenAI 集成文档仍列出 Realtime API、GPT-4o、GPT-5、OpenAI STT 和 OpenAI TTS。
2. LiveKit OpenAI Realtime 插件仍提供 Python 和 Node.js 用法，并使用 OpenAI API Key。
3. LiveKit 2026 年 Series C 文章仍称 Agents 的设计受到 ChatGPT Voice Mode 工作经验影响。
4. OpenAI Realtime API 与 LiveKit 的组合仍有现实价值：OpenAI 负责语音模型，LiveKit 负责前端媒体、状态、电话和代理生命周期。

### 支持“可能淡化”的证据

1. OpenAI 在 2024 年 12 月为 Realtime API 增加直接 WebRTC，开发者可以不经过 LiveKit 连接客户端。
2. OpenAI 在 2025 年 8 月把 Realtime API 和 `gpt-realtime` 做成生产级产品，开始自己覆盖更多工具、图像、SIP 电话和模型能力。
3. OpenAI 在 2026 年发布 GPT-Live 时，产品核心叙事是自己的 full-duplex 模型、后台模型委派和 ChatGPT Voice 体验，并没有继续把 LiveKit 作为公开叙事中心。这里的“没有提到”只能作为弱证据，不能证明底层一定不再使用 LiveKit。
4. LiveKit 也在主动降低对单一模型的依赖：支持数百种模型、自己的 Inference、Agent Builder，以及与其他模型公司的合作。

最稳妥的结论是：**双方的技术兼容和商业合作仍然存在，但 2024 年那种“LiveKit 是 OpenAI Advanced Voice 对外开发者化的关键桥梁”的特殊性，到了 2025—2026 年已经下降。**


## 最终判断

OpenAI 的 AI 语音发展不是突然从 GPT-4o 开始，而是一条逐层推进的路线：2022 年先把声音听懂，2023 年把语音放进 ChatGPT，2024 年用 GPT-4o 和 Realtime API 把低延迟语音交互做成模型与平台能力，2025 年把它推向生产级语音代理，2026 年继续向持续听说、实时翻译、工具调用和后台推理委派推进。

LiveKit 的路线也不是从“做一个 OpenAI 插件”开始，而是从 2021 年的开源 WebRTC 基础设施出发，2022 年做全球云网络，2023—2024 年在真实 AI 语音项目中积累经验，随后把这些经验抽象成 Agents 框架，再扩展为多模型、电话、部署、测试和监控的一体化平台。

两条路线在 2023 年前后相遇，2024 年 GPT-4o 和 Realtime API 发布时达到最深，2024 年 10 月的公开合作是关系最清晰的标志。进入 2025—2026 年后，OpenAI 能自己提供更多实时通信和代理能力，LiveKit 也在拥抱更多模型和客户，因此双方从“共同打造标杆产品”转向“模型供应商 + 实时代理基础设施平台”的开放合作。

**最准确的结论不是“OpenAI 抛弃了 LiveKit”，而是：OpenAI 逐步拥有了绕过 LiveKit 的能力，LiveKit 也逐步拥有了不依赖 OpenAI 的能力；双方仍然合作，但合作的议价关系和技术必要性已经不像 2024 年那样集中。**
