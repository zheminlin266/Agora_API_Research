# RTC行业供给

### 核心问题

1. 几类RTC供应商在不同工作负载中的优势？
2. 2020年以来RTC市场有哪些供应商进入？发展情况如何？

#### 几类RTC供应商在不同工作负载中的优势？

取决于工作负载的主要瓶颈在哪里：

- 瓶颈是实时媒体质量：独立 RTC PaaS 更强。
- 瓶颈是与云上数据、AI、安全体系集成：综合云厂商更强。
- 瓶颈是电话号码、运营商网络和客户旅程编排：CPaaS 更强。
- 瓶颈是海量观众的单位分发成本：CDN 更强。
- 瓶颈是可移植性、私有部署和媒体/AI 管线定制：开源托管更强。
- 瓶颈是极致控制、特殊架构或超大稳定流量下的长期成本：客户自研更强。

| 类型 | 最具优势的工作负载 | 结构性优势 | 相对弱项 |
| --- | --- | --- | --- |
| 独立 RTC PaaS | 全球多人通话、语聊房、游戏语音、在线课堂、社交娱乐、K歌、连麦直播、应用内人机实时对话 | 将弱网对抗、拥塞控制、路由、编解码、跨设备兼容和 QoE 诊断作为核心产品；跨云中立；场景 SDK 深 | PSTN、号码合规和全渠道工作流通常不如 CPaaS；海量纯观看成本不如 CDN；容易受到云厂商打包定价影响 |
| 综合云厂商 | RTC 与云数据库、对象存储、AI、内容审核、企业身份和已有云采购紧密结合的工作负载 | 统一 IAM、账单、数据驻留、AI/存储/安全集成；可用云折扣和既有销售关系打包 | RTC 往往只是产品组合的一部分；对复杂弱网、娱乐音效、异构终端和跨云中立性的投入可能不及专业厂商 |
| CPaaS | 呼叫中心、通知、IVR、营销触达、预约、客服、电话机器人、短信/WhatsApp/邮件与语音联动 | 电话号码、SIP/PSTN、运营商互联、号码及消息合规、路由、身份、客户数据和全渠道工作流 | 大型多人视频、互动直播、复杂媒体处理和海量观众分发通常不是核心优势 |
| CDN | 体育赛事、发布会、电商直播、财经资讯等一到少数主播、数万至数百万观众的直播 | 边缘节点覆盖、扇出能力、转码和自适应码率、DVR/录制、单位观看成本 | 多人双向互动、频繁上下麦、复杂房间状态和上行弱网优化较弱 |
| 开源托管 | 开发者主导的会议、语音 AI、多模态 Agent、需要源代码可见、私有/混合部署或模型自由选择的场景 | 开源可移植、可修改媒体及 Agent 管线，同时把全球部署、扩缩容、可观测性交给托管商 | 真正自托管后，跨区域调度、TURN、Redis、升级、容量规划和7×24运维仍然复杂 |
| 客户自研 | RTC 是核心产品差异化能力、流量巨大且稳定、专用硬件/协议/编解码、封闭网络、极强数据主权要求 | 最大控制权；可针对单一业务拓扑优化；在足够大的稳定规模下可能摊薄供应商毛利 | 全球网络、弱网算法、终端兼容、故障诊断和持续演进的固定成本极高；机会成本最大 |

#### 2020年以来RTC市场有哪些供应商进入？发展情况如何？

表格列出2020年以来进入RTC行业的服务商，主要集中于2020-2022年之间。

| 供应商 | 进入时间及方式 | 当前发展情况 | 综合评价 |
| --- | --- | --- | --- |
| Zoom Video SDK | Zoom于2020年首次推出Video SDK，将其会议系统中的实时音视频能力开放给第三方应用。([zoom.com](https://www.zoom.com/en/blog/bring-industry-leading-video-to-your-application-with-zoom-video-sdk/?utm_source=chatgpt.com)) | 截至2026年仍持续维护Native、Web和UI Toolkit等版本，当前产品覆盖音视频、屏幕共享、聊天、数据流、API和Webhook（服务端事件回调）。([zoom.com](https://www.zoom.com/en/video-sdk/?utm_source=chatgpt.com)) | **战略性进入并持续运营。** 借助Zoom既有媒体技术和企业客户渠道，产品存续度较高；但Zoom未单独披露Video SDK收入，无法判断其独立规模和盈利能力。 |
| Microsoft Azure Communication Services | 2020年9月开始预览，2021年4月正式商用，提供语音、视频、聊天、短信、电话网接入及Microsoft Teams互操作。([Source](https://news.microsoft.com/ignite-march-2021-book-of-news/?utm_source=chatgpt.com)) | 此后继续深化与Teams会议、通话和企业身份体系的整合。([Microsoft for Developers](https://devblogs.microsoft.com/microsoft365dev/build-a-meetings-app-with-azure-communication-services-and-microsoft-teams-part-1/?utm_source=chatgpt.com)) | **成功成为Azure的标准通信组件，但不属于独立RTC业务。** 其优势是云、Teams、身份、安全和企业采购整合；微软未披露RTC独立收入。 |
| 华为云SparkRTC | 2020年开始公测，2021年4月首次商业发布。([华为云](https://www.huaweicloud.com/guide/category-a96d413fb46e8e89dc6140a7a0bdcfd7eef081f8a44f632fb63c1e13c001f415?utm_source=chatgpt.com)) | 截至2026年产品及文档仍在更新。华为云称其服务过70多场部长级峰会和500多场大型高规格会议，并公布了水滴、美术宝等案例；这些属于厂商口径，未获独立验证。([华为云](https://www.huaweicloud.com/product/cloudrtc.html?utm_source=chatgpt.com)) | **在政企会议、教育和华为云生态中持续运营。** 产品存续和项目案例较明确，但外部商业收入及其相对于华为内部业务的规模无法判断。 |
| 100ms | 公司成立于2020年，约在2021年开始规模推广实时视频和互动直播SDK。 | 2022年3月完成**2,000万美元A轮融资**；当时公司称自2021年8月以来已有超过2,200家企业使用，且此前一个季度业务增长20倍。这些均为公司对外口径。([TechCrunch](https://techcrunch.com/2022/03/10/100ms-secures-20m-to-power-next-generation-of-live-video-apps/)) | **早期产品增长较快，但后续战略明显变化。** RTC产品仍然存在，不过公司目前也重点发展医疗运营AI Agent（智能体），说明纯通用RTC不再是唯一业务重心。近期RTC收入和盈利数据未公开。([100ms.live](https://www.100ms.live/customers/townscript?utm_source=chatgpt.com)) |
| Dyte | 2020年成立，提供可嵌入应用的音视频SDK和会议组件。([LinkedIn](https://www.linkedin.com/company/dyteio?utm_source=chatgpt.com)) | 2025年Dyte团队加入Cloudflare，其技术和产品逐步整合进Cloudflare RealtimeKit。Cloudflare并未公开交易金额或Dyte经营数据。([The Cloudflare Blog](https://blog.cloudflare.com/introducing-cloudflare-realtime-and-realtimekit/?utm_source=chatgpt.com)) | **独立供应商身份已经结束，但产品技术并未消失。** 这更接近被更大边缘网络平台吸收，而不是彻底关闭。 |
| LiveKit | 2021年7月首次发布开源版本，2022年10月推出LiveKit Cloud托管服务。([LiveKit](https://livekit.com/blog/the-end-of-participant-minute?utm_source=chatgpt.com)) | 2026年1月完成**1亿美元C轮融资**，估值达到**10亿美元**；其客户和应用范围已从传统音视频房间扩展到语音AI、智能体和电话接入。([LiveKit](https://livekit.com/blog/livekit-series-c?utm_source=chatgpt.com)) | **本轮最成功的独立新进入者。** 开源带来开发者采用，托管云实现商业化，生成式AI又扩大了需求。不过融资和估值不能代替收入、毛利和盈利证明，LiveKit未公开经审计财务数据。 |
| 火山引擎RTC | 字节跳动旗下火山引擎于2022年1月正式对外发布RTC和低延迟直播产品。([火山引擎开发者社区](https://developer.volcengine.com/articles/7043802734918631438?utm_source=chatgpt.com)) | 产品仍持续更新，并扩展到AI实时对话、直播互动和多端SDK。火山引擎强调相关技术经过抖音等大规模产品验证，但属于供应商自述，外部客户收入未披露。([VolcEngine](https://www.volcengine.com/product/rtc?utm_source=chatgpt.com)) | **技术和产品活跃度较高。** 最大优势是字节跳动内部流量、算法和工程经验；但难以区分内部使用、生态协同和真正第三方商业收入。 |
| Dolby／Millicast | Dolby于2022年2月收购Millicast，进入超低延迟、大规模WebRTC直播市场。收购时产品主打低于500毫秒延迟和超过6万观众规模。([杜比新闻](https://news.dolby.com/en-WW/209521-dolby-acquires-millicast-the-real-time-ultra-low-delay-video-streaming-platform)) | 产品后来更名为Dolby OptiView Real-time Streaming，继续面向体育、博彩、拍卖和大型现场活动运营。([Dolby OptiView](https://optiview.dolby.com/docs/millicast/?utm_source=chatgpt.com)) | **通过并购完成了相对成功的进入。** 产品持续存在并获得更清晰的垂直定位，但它更偏一对多超低延迟流媒体，不是Agora式全场景多人RTC PaaS。 |
| 快手StreamLake | 快手于2022年8月推出StreamLake视频云品牌，正式面向外部企业提供音视频云、RTC和视频AI能力。([新华网](https://www.news.cn/tech/20220811/2a22c6efd98845c1bbb31aeb25f5c016/c.html?utm_source=chatgpt.com)) | 当前RTC仍在StreamLake产品矩阵中，平台同时扩展视频云和AI相关服务。([StreamLake](https://www.streamlake.com/?utm_source=chatgpt.com)) | **仍在运营，但商业透明度低。** 更像快手将内部视频技术对外输出的综合视频云业务，未披露RTC客户数、收入和毛利。 |
| Cloudflare Calls／Realtime | Cloudflare于2022年9月发布Cloudflare Calls，首先提供基于全球边缘网络的SFU和TURN（Traversal Using Relays around NAT，NAT穿透中继）服务。([The Cloudflare Blog](https://blog.cloudflare.com/announcing-cloudflare-calls/?utm_source=chatgpt.com)) | 2024年进入公开测试；2025年进一步升级为Cloudflare Realtime和RealtimeKit，增加客户端SDK、录制、协调和转写，并吸收Dyte团队。2026年仍在持续更新。([The Cloudflare Blog](https://blog.cloudflare.com/cloudflare-calls-anycast-webrtc/?utm_source=chatgpt.com)) | **发展方向明确，仍处于战略扩张阶段。** Cloudflare正从底层网络和SFU向完整RTC开发平台上移，但没有独立收入数据，商业化效果尚不能定量评价。 |
| Mux Real-Time Video | Mux于2022年5月推出Real-Time Video，并于2022年11月正式商用。([Mux](https://www.mux.com/blog/tmi-2022-customer-conference?utm_source=chatgpt.com)) | 2024年1月，Mux停止Real-Time Video、Mux Studio和Web Broadcast SDK；其点播和传统直播产品继续运营。([Mux](https://www.mux.com/docs/changelog/real-time-video-and-studio-shutdown)) | **明确失败或至少主动放弃的进入案例。** 从2022年11月正式商用到2024年1月宣布停止，约13个月。Mux未公开具体停止原因，因此不能确认是技术、需求、毛利还是内部资源配置问题。 |
| AWS IVS Real-Time Streaming | AWS于2023年8月推出Amazon IVS Real-Time Streaming，首发时支持低于300毫秒延迟、最多1万名观众。([Amazon Web Services, Inc.](https://aws.amazon.com/about-aws/whats-new/2023/08/amazon-interactive-video-service-real-time-streaming/)) | 当前能力已扩展到超过2.5万名观众、最多12名主播，并在2025—2026年继续增加功能及冗余接入。([AWS 文档](https://docs.aws.amazon.com/ivs/latest/RealTimeUserGuide/what-is.html?utm_source=chatgpt.com)) | **作为AWS互动直播组件发展较稳健。** 它适合“少量主播＋大量观众”，与传统多人会议RTC并不完全重叠；AWS未披露其独立收入。 |

**按时间的分阶段梳理**

- 第一阶段（2020-2021）：Zoom Video SDK、Azure Communication Services、华为云SparkRTC、100ms、Dyte和LiveKit。疫情导致通信需求激增，比如电话会议、在线教育场景。
- 第二阶段（2022-2023）：火山引擎、StreamLake、Cloudflare、Dolby/Millicast、Mux和AWS IVS。场景扩展到直播电商、互动观看。
- 第三阶段（2024以来）：没有新进入者，但几乎所有原有RTC服务商都在向AI语音扩展。其中Livekit转型的最好。

#### 2020年以来哪些RTC的服务商退出了这个领域？

| 原供应商/产品 | 退出性质 | 时间 | 退出后的状态 | 主要原因判断 |
| --- | --- | --- | --- | --- |
| Mux Real-Time Video | RTC产品彻底关闭 | 2024年1月 | Real-Time Video、Studio和Web Broadcast SDK全部停止；Mux保留点播和传统直播 | 公司未披露原因；高度可能是RTC业务规模或预期回报不足，选择重新聚焦核心视频业务 |
| Twilio Live | 退出互动实时直播产品 | 2023年11月 | API、文档和状态页均撤下；Twilio仍保留Video API | 公司未披露具体原因；大概率属于盈利压力下的产品线收缩和重叠产品整合 |
| Vidyo.io | 退出独立RTC PaaS | 2022年7月 | 代码库更新频率极低，推测公司几乎停滞。 | 没有足够业务支撑企业经营 |
| Dyte | 独立供应商身份结束 | 2025年 | 团队加入Cloudflare，产品能力并入RealtimeKit；底层RTC能力继续运营 | 通过并购/团队整合获得Cloudflare全球网络和渠道，不属于技术关闭 |
| CafeX部分WebRTC业务 | 业务转让及战略转型 | 2020年以后 | Live Assist for Dynamics 365转让给CBA；产品继续由CBA销售和支持，CafeX转向AI和企业数据系统 | 通用/垂直WebRTC业务不再由CafeX直接运营，资源转向更高层的AI和数据产品 |
| 100ms | 没有退出RTC业务，但声明转移向医疗AI | 2024年 | 没有公开信息 | 原来的商业模式同质化严重，竞争激烈，向更高价值量的细分和场景扩展 |