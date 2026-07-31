# How AI Voice Changes Infrastructure Requirements

### RTC Topologies Across Different Use Cases

A typical AI voice topology looks like this:

![AI voice RTC topology](/articles/ai-voice-infrastructure/ai-voice-topology.png)

At its core, this architecture consists of a large number of one-to-one, continuously bidirectional, low-bitrate sessions.

The model server effectively acts as another participant in the conversation. The communications layer must not only connect the user, but also maintain link quality between the user's region and the region where the model is deployed.

By contrast, a typical live-commerce topology looks like this:

![Live-commerce livestream topology](/articles/ai-voice-infrastructure/live-commerce-topology.png)

In most cases, only the host and a small number of co-hosts use RTC. The vast majority of viewers receive video through low-latency streaming or a CDN.

This is the classic **small number of uplinks, large-scale downstream distribution** model.

Social live streaming takes more forms:

![Social livestream topology](/articles/ai-voice-infrastructure/social-livestream-topology.png)

Or a multi-person voice room:

![Multi-person voice-room topology](/articles/ai-voice-infrastructure/voice-room-topology.png)

It combines multi-party, real-time interaction with potentially large numbers of passive viewers, so it often uses both RTC and CDN infrastructure.

#### Differences in Infrastructure Requirements

| Dimension | AI Voice | Live Commerce | Social Live Streaming |
| --- | --- | --- | --- |
| Primary topology | One-to-one, bidirectional human-AI interaction | One-to-many, host to audience | A mix of many-to-many and one-to-many |
| Primary media | A single audio stream | High-definition video and audio | Audio, video, and multi-party co-hosting |
| Bandwidth demand | Low | Extremely high | Medium to high |
| Latency sensitivity | Extremely high | Moderate to high | High |
| Sensitivity to latency variation | Extremely high | Relatively low | High |
| Importance of the uplink | Extremely high | Extremely high for hosts; lower for viewers | High for active speakers |
| Importance of the downlink | One stable stream is sufficient | Paramount | Depends on room size |
| Main scaling bottlenecks | Long-lived connections, packet-processing rate, session state | Egress bandwidth, transcoding, CDN capacity | SFU capacity, audio mixing, dynamic subscriptions |
| Buffering strategy | As shallow as possible | Can be deeper | Shallow for interactive users; deeper for viewers is acceptable |
| Role switching | Rare | Viewers occasionally become co-hosts | Very frequent |
| Communications control events | Interruptions, stop playback, reconnects | Start streaming, switch streams, co-hosting | Go on mic, leave mic, mute, move between rooms, merge streams |
| Core cost drivers | RTC connections, servers, cross-region links | Bandwidth, transcoding, CDN traffic | RTC servers, bandwidth, and mixing |
| Importance of a CDN | Generally unnecessary | Very important | Important for large rooms; less so for small rooms |

### What Makes AI Voice Different

**The goal is not the lowest average latency, but the lowest tail latency.**

In live commerce, it is usually not immediately disruptive if a small share of viewers occasionally waits a few hundred extra milliseconds.

AI voice is different. Even if most turns in a conversation are fast, a few unexpectedly long pauses can make users feel that the AI has frozen or does not know how to respond.

For this reason, the AI voice communications layer places greater emphasis on:

**P95 and P99 network latency**, as well as:

- Latency jitter
- Time to first audio packet
- Reconnection time after a disconnect
- Intermittent degradation on cross-region links
- End-to-end round-trip time from the device to the model server

Traditional live-streaming systems can absorb network variation with relatively deep playback buffers. AI voice cannot use buffers that deep, because buffering itself directly increases conversational wait time.

**AI voice is low-bandwidth, high-packet-rate, and high-connection-count.**

A single audio stream uses far less bandwidth than high-definition video, but audio is broken into a continuous sequence of many small packets.

When large numbers of AI customer-service sessions or voice agents run concurrently, the infrastructure challenge is not simply bandwidth. It includes:

- Large numbers of long-lived connections
- Large volumes of small packets
- A high packet-processing rate per second
- Independent connection state for every session
- NAT traversal and connection keepalives
- Frequent control messages at scale

Live commerce is more of a throughput problem. AI voice is more about connection density and packet-processing efficiency.

**Uplink quality matters far more than it does in a viewing-only live-streaming scenario.**

Typical live-streaming viewers primarily receive video. Their uplink usually carries only data messages such as likes and comments, so a mediocre uplink generally does not affect video playback.

In AI voice, the user's uplink audio is the input to the entire system. The following uplink problems directly degrade communications quality:

- Packet loss
- Choppy audio
- Out-of-order packet delivery
- Network jitter
- Inconsistent sample rates or codecs
- An abrupt handoff from Wi-Fi to a mobile network

**It must support true full-duplex communication.**

Full duplex means that the user and the AI can send and receive audio at the same time.

Live commerce is typically host-led: the host speaks and the audience listens. Even when co-hosting is enabled, participation is often limited to a small number of people.

In AI voice, a user may begin speaking while the AI is still playing audio. The communications layer must therefore handle:

- Simultaneous AI audio playback and user audio capture
- Echo cancellation
- Rapid reporting that the user has started speaking
- Immediate suspension of downstream audio
- Clearing the playback buffer on the device
- Flushing audio packets that have not yet been sent from the media server
- Telling upstream services to stop sending additional audio

**Playback buffers must be quickly cancelable.**

Live video generally prioritizes uninterrupted playback. When the network jitters, systems tend to increase buffering to prevent visible stalling.

AI voice has the opposite requirement: buffers cannot be too deep, and they must be cancelable.

For example, suppose the AI has generated five seconds of speech and the user interrupts after hearing two seconds. The communications layer needs to:

1. Stop receiving additional audio.
2. Delete the server-side buffer.
3. Clear the device playback queue.
4. Ensure that the remaining three seconds are not played later.

AI voice buffering therefore has to meet two conflicting goals at once:

- Keep audio continuous during brief network jitter.
- Stop immediately when the user interjects, without continuing to play audio from inertia.

**Media format conversion is more frequent.**

Live commerce typically has an end-to-end pipeline built around standard video codecs: the host encodes the uplink, the cloud transcodes it, the CDN distributes it, and viewers' players decode it. In AI voice, different stages may use different formats:

- WebRTC clients use Opus.
- Telephone networks use narrowband voice codecs.
- Some voice models use PCM audio.
- Different models require different sample rates.
- Clients may use mono or stereo audio.
- The model's output format may differ from the playback format on the device.

Communications gateways often need to perform:

- Decoding and re-encoding
- Sample-rate conversion
- Channel conversion
- Audio framing
- Protocol conversion
- Timestamp realignment

**Compatibility with telephone networks is more important.**

Many AI voice use cases involve customer service, outbound calling, appointment scheduling, and sales. They therefore often need to connect to SIP and PSTN networks. This introduces requirements that live commerce and most social live-streaming services do not have:

- SIP signaling
- RTP media streams
- Narrowband telephone audio
- DTMF keypresses
- Call hold and transfer
- Escalation from AI to a human agent
- Failover when a carrier route fails
- Caller ID and line-status management
- Interoperability with telecom networks in different countries

### Summary

| Business | Most Important Communications-Infrastructure Question |
| --- | --- |
| AI voice | Can it keep a large number of independent, bidirectional sessions low-latency, low-jitter, and interruptible? |
| Live commerce | Can it distribute high-quality video reliably and cost-effectively to a large audience? |
| Social live streaming | Can it manage complex, real-time media relationships among many users, roles, and dynamically changing interactions? |
