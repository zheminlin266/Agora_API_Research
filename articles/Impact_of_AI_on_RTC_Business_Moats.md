# How Does AI Affect the Competitive Moat of RTC Businesses?

### Core Question

AI has significantly reduced the difficulty of supplying RTC services. This section objectively evaluates that claim and presents arguments both for and against it.

#### RTC Services Must Be Evaluated at Different Layers

| RTC Supply Layer | Degree to Which AI Reduces Difficulty | Assessment |
| --- | --- | --- |
| Integrating real-time audio and video into an app | High | Significantly reduced |
| Building a single-region or vertical RTC service based on an open-source SFU | Moderate | Barriers to entry have fallen |
| Building a global, highly available, high-quality RTC PaaS | Relatively low | Core barriers remain |

#### Significantly Improves Execution and Integration Efficiency

- SDK integration and cross-platform wrappers;
- Token management, user permissions, and room logic;
- Client adaptation for Web, iOS, Android, and React Native;
- Recording, streaming, Webhooks, and business backends;
- Terraform, Kubernetes, monitoring rules, and operations scripts;
- Documentation, sample code, and customer technical support.

Tasks in these areas that previously might have taken 1–2 weeks can now potentially be completed in 1–2 days.

#### AI-Driven Efficiency Gains Across Different Work Modules

If RTC services are divided into the media plane, control plane, and operations plane, their main responsibilities are:

- **Media plane**: audio and video capture, encoding, transmission, forwarding, and packet-loss resilience;
- **Control plane**: authentication, signaling, room management, scheduling, billing, and permissions;
- **Operations plane**: monitoring, alerting, log analysis, troubleshooting, and capacity planning.

AI delivers very significant efficiency gains in the control plane and operations plane, but its impact on the media plane still faces some constraints. That said, progress is extremely rapid, making the longer-term outlook difficult to predict.

#### Another Way to View the Decline in RTC Barriers

The decline in barriers to supplying RTC services is actually being driven by four forces working together:

| Factor | Main Barrier Reduced |
| --- | --- |
| WebRTC standardization | Interoperability across browsers, protocols, and clients |
| Open-source projects such as LiveKit and mediasoup | Media server and SDK development |
| Public cloud, containers, and infrastructure as code | Server procurement and deployment |
| Generative AI | Coding, integration, testing, documentation, and troubleshooting |

**Open-source RTC projects and cloud infrastructure solve the problem of “whether ready-made building blocks exist,” while AI solves the problem of “how to assemble those building blocks faster”**.

#### Bottlenecks That AI Struggles to Address

From today's perspective, AI still struggles to address the following bottlenecks, although a significant portion of them may eventually be handled by AI as the technology evolves.

- Propagation latency over fiber and wireless networks;
- Differences in interconnection quality among telecom operators;
- UDP blocking;
- Sudden packet loss and bandwidth contention;

These problems require physical network nodes, traffic scheduling, redundant links, and long-term operational data, rather than generated code alone.

Different use cases create different technical challenges. For example, when expanding across multiple regions and scenarios, providers must solve deeper problems such as:

- Multi-node deployments requiring Redis as shared data storage and a message bus;
- Multi-region deployments requiring region-aware signaling load balancing;
- Network performance data across different countries and telecom operators;
- Extensive compatibility records across devices and operating systems;
- Real-world failure cases;

Under weak-network and high-load conditions, the challenges shift to:

- Many bugs appearing only on specific devices or under particular weak-network conditions;
- A change improving one network scenario while degrading another;
- The need for prolonged stress testing and validation with real traffic;
- Feedback on the effectiveness of routing strategies;
- Long-term customer-side quality baselines.

### Summary

AI is having a profound impact on the RTC industry. First, the rapid expansion of data center infrastructure has changed the hardware landscape. Since RTC can now leverage infrastructure built for other major workloads, companies may no longer need to invest in dedicated infrastructure; instead, the existing capacity created by broader AI-driven demand may be sufficient to support RTC needs. Second, the availability of open-source RTC solutions has increased significantly, largely because AI has dramatically reduced the cost of software development. The effort required to assemble and integrate software components has also dropped substantially. In this new era, the capabilities of a senior RTC expert can be greatly amplified by AI.

However, some RTC scenarios still require deep technical expertise, such as cross-region communication, poor network environments, and high-concurrency deployments. These areas rely on years of accumulated experience in optimization, error correction, and proprietary datasets, creating barriers that AI alone cannot easily replace.

