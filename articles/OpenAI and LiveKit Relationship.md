# OpenAI and LiveKit: From Co-Developing ChatGPT Voice to a Voice-Agent Infrastructure Ecosystem

July 28, 2026

## AI Voice and Real-Time Communications Are Not the Same Thing

AI voice has at least two layers:

- **The model layer:** The model must understand what someone says, follow the context, decide what to say, and generate a voice response. This involves STT (speech-to-text, which turns spoken audio into text), TTS (text-to-speech, which turns written text into spoken audio), and speech-to-speech (audio goes in and audio comes out directly).
- **The communications and runtime layer:** A user's microphone audio must travel over an unreliable Wi-Fi or mobile network and reach a server with very little delay. The generated audio must then come back smoothly. The system also has to handle packet loss, disconnections, echo, overlapping speakers, user interruptions, and routing each call to the right agent.

Early voice assistants usually followed a pipeline: **a person speaks → STT writes it down → a text model generates an answer → TTS reads the answer aloud → the user hears it.**

The approach is easy to understand, but information can be lost at every step. Tone of voice, laughter, pauses, and background sound may not survive several conversions between audio and text. LiveKit primarily solves the second layer, while OpenAI primarily solves the first; since 2024, their interfaces have tied the two layers together much more tightly.

## OpenAI's Development History in AI Voice

### 1. 2022: First, Make the System Understand Speech — Whisper Opens the Door

On September 21, 2022, OpenAI released Whisper. Whisper is an ASR model, or in plain English, a system that tries to write down what people say as accurately as possible. It was trained on roughly 680,000 hours of multilingual, multitask audio, with an emphasis on handling accents, noise, technical vocabulary, and different languages.[OpenAI: Introducing Whisper](https://openai.com/index/whisper/)

Whisper mattered for more than the model itself. It gave developers an open, reusable speech-recognition capability rather than forcing them to depend entirely on a closed voice service. It also became an important foundation for the early ChatGPT Voice experience, which first converted a user's speech into text. More broadly, it showed OpenAI's initial strategy: break voice into separate components that can be optimized independently, then gradually move toward genuinely real-time conversation.

At the same time, OpenAI had already begun developing Voice Engine in late 2022. Voice Engine is a TTS model that can generate a voice resembling the original speaker from text and roughly 15 seconds of audio.[OpenAI: How Voice Engine Works and the Safety Research Behind It](https://openai.com/index/expanding-on-how-voice-engine-works-and-our-safety-research/) OpenAI did not immediately release this capability at scale because voice cloning can be used for impersonation, fraud, and deception.

The distinction is important: **Whisper mainly handles listening, while Voice Engine mainly handles speaking.** Neither one, by itself, is a complete voice agent that can understand, decide, and respond.

### 2. September–November 2023: ChatGPT Voice Turns Speech into a Mass-Market Product

On September 25, 2023, OpenAI announced that ChatGPT was beginning to gain voice and image capabilities, initially rolling them out to Plus and Enterprise users. The early Voice Mode used a three-part pipeline: Whisper transcribed the user's speech, GPT-3.5 or GPT-4 generated the answer, and a TTS model converted the answer back into speech.[OpenAI: ChatGPT Can Now See, Hear, and Speak](https://openai.com/index/chatgpt-can-now-see-hear-and-speak/)

In plain English, the first generation of ChatGPT Voice worked by “transcribing first, thinking second, and reading aloud last.” It could already support back-and-forth conversations, but it was not yet a single model directly listening to audio and responding with audio.

In November 2023, OpenAI released a TTS API (an application programming interface, or a standardized way for software to call a capability) with six preset voices. OpenAI later explained that this TTS API was also powered by Voice Engine, but the release used preset voices created with professional voice actors rather than allowing ordinary users to upload arbitrary samples and clone a voice.[OpenAI: Expanding on How Voice Engine Works](https://openai.com/index/expanding-on-how-voice-engine-works-and-our-safety-research/)

On November 21, 2023, ChatGPT Voice became available to all users.[ChatGPT Release Notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes) This was the point when voice moved from a research demonstration into a high-frequency consumer product. It also forced OpenAI to confront real-world issues involving latency, interruptions, accents, background noise, emotional reliance, and voice safety.

### 3. March 2024: Voice Engine Is Previewed, but Not Released Broadly

On March 29, 2024, OpenAI publicly described a small-scale preview of Voice Engine. The model could use text and a 15-second voice sample to generate natural-sounding speech that resembled the original speaker. A small group of trusted partners tested it for reading assistance, education, and video translation.[OpenAI: Navigating the Challenges and Opportunities of Synthetic Voices](https://openai.com/index/navigating-the-challenges-and-opportunities-of-synthetic-voices/)

OpenAI also made clear that Voice Engine would not be broadly released at that point. Its proposed safeguards included obtaining the original speaker's consent, telling listeners when a voice was AI-generated, tracing the source of generated audio, and preventing the creation of voices that were too close to prominent public figures.

This revealed two separate paths in OpenAI's voice strategy. Preset voices were easier to control and more suitable for product deployment. Custom voices were more powerful but carried greater risks, so they remained mainly in small-scale research and partner testing.

### 4. May 2024: GPT-4o Moves Voice from an Add-On Module into the Model Itself

On May 13, 2024, OpenAI released GPT-4o. The “o” stands for omni, meaning that the model can accept combinations of text, audio, images, and video, and can produce combinations of text, audio, and images.[OpenAI: Hello GPT-4o](https://openai.com/index/hello-gpt-4o/)

The most important change from the old Voice Mode was that GPT-4o no longer depended entirely on a stitched-together “STT → text model → TTS” pipeline. OpenAI reported that older voice conversations had average latencies of roughly 2.8 to 5.4 seconds, while GPT-4o could respond to audio in as little as 232 milliseconds, with an average of about 320 milliseconds—close to the reaction time of a natural conversation.

The old pipeline was better at preserving what a person said than how they said it. GPT-4o could make more direct use of tone, pauses, laughter, and background sound, and could generate responses with rhythm, emotion, and nonverbal sounds. Its system card specifically evaluated risks involving unauthorized voice generation, speaker identification, copyrighted content, and sensitive-attribute inference.[GPT-4o System Card](https://openai.com/index/gpt-4o-system-card/)

GPT-4o was not fully opened up on launch day. OpenAI initially released the text and image capabilities while continuing to work on the infrastructure, product experience, and safety measures needed for audio. Advanced Voice Mode (the lower-latency voice experience with interruptions and more natural delivery) was rolled out later in stages.

### 5. July–September 2024: Advanced Voice Mode Moves from a Demo to Real Users

On July 30, 2024, OpenAI began rolling out Advanced Voice Mode to a small number of ChatGPT Plus users as an alpha test (a limited early test). The first rollout focused on voice; it did not mean that every video, screen-sharing, and other capability shown in the May demonstration was launching at the same time.[TechCrunch coverage of the first rollout](https://techcrunch.com/2024/07/30/openai-releases-chatgpts-super-realistic-voice-feature/)

By September 2024, Advanced Voice Mode had expanded to more paid users. The central challenge was no longer just generating a voice. The system also had to determine whether it could be interrupted while speaking, whether the user had finished, whether a pause or a noise should be treated as a new instruction, whether the conversation could resume from the correct context after an interruption, and whether the voice sounded natural without creating an excessive impersonation risk.

### 6. October 1, 2024: Realtime API Gives Developers Access to Real-Time Voice

On October 1, 2024, OpenAI released the public beta of the Realtime API. Developers could maintain a live connection that allowed GPT-4o to receive audio and produce audio in real time, without having to assemble Whisper, a text model, and TTS themselves. The Realtime API also supported function calling (letting the model ask an external program to perform an action, such as checking an order, changing an appointment, or querying a database) and user interruptions.[OpenAI: Introducing the Realtime API](https://openai.com/index/introducing-the-realtime-api/)

OpenAI also said that it had worked with LiveKit and Agora on audio components for echo cancellation, reconnection, and sound isolation, and with Twilio to connect the Realtime API to telephony. This shows that OpenAI did not initially try to own every client and communications problem itself. Instead, it used multiple infrastructure partners to connect its models to real applications.

### 7. October 3, 2024: The OpenAI–LiveKit Partnership Becomes Public

On October 3, 2024, LiveKit formally announced its partnership with OpenAI and described how to turn the end-to-end technology behind ChatGPT Advanced Voice into a developer-facing API.[LiveKit: OpenAI and LiveKit Partner to Turn Advanced Voice into an API](https://livekit.com/blog/openai-livekit-partnership-advanced-voice-realtime-api)

LiveKit disclosed the architecture:

1. The ChatGPT app uses a LiveKit client SDK to capture the user's speech.
2. The user's speech travels through LiveKit Cloud to OpenAI's voice agent.
3. The voice agent sends the audio to GPT-4o.
4. GPT-4o generates audio and sends it back to the voice agent.
5. The voice agent sends the audio back to the user's device through LiveKit Cloud.

The important point is that LiveKit does not replace OpenAI in running GPT-4o. Instead, LiveKit handles the “last mile” and the continuous runtime: connecting user devices, keeping audio usable over imperfect networks, and managing buffering, interruptions, reconnections, load balancing (distributing new sessions across suitable agent instances), and telephony.

### 8. December 2024: OpenAI Adds a Direct WebRTC Path That Does Not Require LiveKit

On December 17, 2024, OpenAI added direct WebRTC support to the Realtime API. WebRTC is a real-time audio and video standard widely used by browsers and mobile clients. Previously, developers often used a layer such as LiveKit to connect their server and client; now they could use OpenAI's own WebRTC integration directly.[OpenAI: o1 and New Tools for Developers](https://openai.com/index/o1-and-new-tools-for-developers/)

This was an important sign that the relationship could be moving away from single-provider dependence, but it did not mean the partnership was ending. Direct WebRTC reduced the number of layers for OpenAI and for simple applications. LiveKit still offered capabilities that direct connectivity alone did not provide, including telephony, agent orchestration, state management, observability, model switching, and large-scale operations. In practice, the two paths could coexist: a small application could connect directly to OpenAI, while a more complex product could use LiveKit as its communications and orchestration layer.

### 9. 2025: From One Real-Time Model to a Full Voice-Agent Product Line

On March 20, 2025, OpenAI released `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, and `gpt-4o-mini-tts`, among other next-generation audio models. The transcription models improved speech-to-text accuracy, while the TTS model gave developers more natural control over speaking style. OpenAI continued to recommend the Realtime API for developers seeking low-latency speech-to-speech experiences.[OpenAI: Introducing Next-Generation Audio Models](https://openai.com/index/introducing-our-next-generation-audio-models/)

On August 28, 2025, the Realtime API became generally available, or GA (formally ready for production use), and OpenAI introduced `gpt-realtime`. The release added image input, MCP (a common protocol for connecting models to external tools and data), and SIP (a session-establishment protocol commonly used in telephone systems) telephony support.[OpenAI: Introducing gpt-realtime](https://openai.com/index/introducing-gpt-realtime/)

This marked a shift in OpenAI's strategy: the goal was no longer merely to let ChatGPT talk. It was to let voice agents do useful work—answer calls, look up information, call tools, process orders, communicate across languages, and keep the conversation moving while actions were being performed.

### 10. 2026: Toward Continuous Conversation, Real-Time Translation, and More Capable Action

On May 7, 2026, OpenAI released GPT-Realtime-2, GPT-Realtime-Translate, and GPT-Realtime-Whisper for stronger real-time reasoning, live translation, and streaming transcription, respectively.[OpenAI: Advancing Voice Intelligence with New Models in the API](https://openai.com/index/advancing-voice-intelligence-with-new-models-in-the-api/)

On July 8, 2026, OpenAI introduced GPT-Live and began using it in a new ChatGPT Voice experience. GPT-Live uses a full-duplex architecture (the model can listen and speak at the same time rather than taking strictly alternating turns). It can keep listening while a user speaks, interrupt when appropriate, wait when needed, and call tools. If a request requires search or deeper reasoning, a more capable model can handle the work in the background while the front-end conversation continues.[OpenAI: Introducing GPT-Live](https://openai.com/index/introducing-gpt-live/)

OpenAI's evolution can be summarized as follows:

**Convert speech to text → connect listening, reasoning, and speaking → let one model process audio in and audio out → add interruptions, tool calls, telephony, and multiple languages → keep listening and speaking while delegating complex work to background models.**

## LiveKit's Development: From WebRTC Infrastructure to a Voice-Agent Platform

### 1. 2021: Starting with Open-Source Real-Time Audio and Video Infrastructure

LiveKit publicly launched on July 7, 2021. It was not initially an AI company. It was an open-source real-time audio and video infrastructure project that let developers add voice rooms, video conferencing, and livestreaming to their products without rebuilding the difficult WebRTC layer from scratch.[LiveKit: And…we're Live(Kit)!](https://livekit.com/blog/and-were-live-kit)

LiveKit's core components included an SFU (Selective Forwarding Unit, a server that receives and forwards media streams so every participant does not have to connect directly to everyone else) and client SDKs for major platforms. Its job was to make media transport between people and devices reliable—not to make a model understand language.

### 2. 2022: LiveKit Cloud Turns Open-Source Code into a Global Network

On October 24, 2022, LiveKit announced LiveKit Cloud. Cloud is the managed version of LiveKit: developers can use a globally distributed real-time media network without building, scaling, and monitoring a large WebRTC cluster themselves.[LiveKit: Announcing LiveKit Cloud](https://livekit.com/blog/announcing-livekit-cloud)

An important design choice was that the open-source and cloud versions used the same APIs and SDKs, allowing developers to move between self-hosting and managed hosting. This “open source first, managed cloud second” model made LiveKit a natural infrastructure layer for AI companies and developers.

### 3. 2023: Moving from Human-to-Human Communication to Human-to-AI Communication

In a later Series B retrospective, LiveKit said that it launched ChatGPT Voice Mode together with OpenAI in September 2023 and released LiveKit Agents around the same time. Its detailed public blog post introducing Agents, however, was published on January 18, 2024.[LiveKit: Series B Retrospective](https://livekit.com/blog/livekits-series-b) [LiveKit: An Open-Source Stack for Real-Time Multimodal AI](https://livekit.com/blog/open-source-realtime-multimodal-ai)

Taken together, these sources suggest that LiveKit was already involved in the engineering work behind a real OpenAI voice product around September 2023, and that it later extracted the lessons into the public Agents framework. LiveKit's AI transition therefore appears to have started with real product problems and only then turned those solutions into a general-purpose framework.

LiveKit Agents focused on four practical problems: receiving live audio and video; buffering, segmenting, and playing model-generated audio; deciding when a user has finished speaking through VAD (voice activity detection, which determines whether someone is currently speaking) and turn detection (deciding whether a speaking turn has ended); and managing agent connections, load, failed reconnections, and horizontal scaling.

### 4. January–June 2024: Agents and the OpenAI Co-Development Experience Become Public

On January 18, 2024, LiveKit formally introduced Agents. The open-source framework combined real-time media, backend SDKs, plugins, task scheduling, and load balancing, and supported OpenAI, Whisper, Deepgram, ElevenLabs, and other model or voice services.[LiveKit Agents announcement](https://livekit.com/blog/open-source-realtime-multimodal-ai)

On June 4, 2024, LiveKit announced a $22.5 million Series A and said that it had worked with OpenAI, Character.AI, and others over the previous 18 months to give their models the ability to see, hear, and speak. LiveKit also said that Agents incorporated the lessons from these voice-assistant projects.[LiveKit: Series A](https://livekit.com/blog/livekit-series-a)

This financing announcement is one of the most important public clues about the early relationship. It does not disclose a contract, purchase volume, or equity investment, but it does suggest that the work was more substantial than a one-off API adapter and influenced LiveKit's product direction.

### 5. October 2024: LiveKit Becomes the Developer-Facing Bridge for Advanced Voice

On October 3, 2024, LiveKit announced the partnership with OpenAI and released a Multimodal Agent API (an interface that brings text, audio, and image inputs and outputs into one agent workflow) built around the OpenAI Realtime API.

LiveKit explained why it was involved. OpenAI's voice model exchanged audio through WebSocket (a persistent connection between a server and client), but packet loss between a server and a browser or phone could create choppy audio. WebRTC was better suited to real-time media on client devices, yet using WebRTC directly brought signaling, codec, network-adaptation, and scaling complexity. LiveKit Cloud sat between these layers.[LiveKit: OpenAI and LiveKit Partner](https://livekit.com/blog/openai-livekit-partnership-advanced-voice-realtime-api)

The complementarity looked like this: **the user's microphone, browser, phone, or telephone connects over WebRTC or SIP → LiveKit Cloud and LiveKit Agents handle the real-time session → WebSocket connects the agent to the OpenAI Realtime API → OpenAI produces the voice response, tool call, or business action.**

OpenAI provided the model capability, while LiveKit provided the real-time connection and agent runtime. Developers could build something resembling Advanced Voice while still adding their own front end, business tools, and telephony system.

### 6. 2025: LiveKit Expands from an OpenAI Adapter into a Multi-Model Platform

On April 10, 2025, LiveKit announced its Series B, a $45 million financing round, and described its goal as building an all-in-one platform for voice AI agents. The announcement said LiveKit Cloud had served more than 100,000 developers and that Agents had expanded from an open-source framework into a product covering workflows, telephony, cloud deployment, and agent scaling.[LiveKit: Series B](https://livekit.com/blog/livekits-series-b)

This was an important change in the relationship. The OpenAI partnership remained, but LiveKit was no longer designing its platform around OpenAI alone. It began treating voice agents as an independent software category and supporting developer choice across different STT, LLM (large language model, the system that understands and generates language), and TTS providers.

### 7. 2026: A Full-Stack Platform for Building, Testing, Deploying, and Monitoring Agents

On January 22, 2026, LiveKit announced its Series C at a $1 billion valuation. It described voice AI as a new class of real-time, stateful application: a conversation can last minutes or hours, and the system must keep listening, thinking, responding, and preserving context throughout the session.[LiveKit: Series C](https://livekit.com/blog/livekit-series-c)

The announcement also said that LiveKit Agents was modeled partly on the work behind ChatGPT Voice Mode, had more than one million monthly downloads, supported hundreds of AI model integrations, and automatically handled turn detection and interruptions. LiveKit also introduced Agent Builder, which lets users create agents from templates and visual workflows.

As of July 2026, LiveKit's official OpenAI integration documentation still supports the OpenAI Realtime API, GPT-4o, GPT-5, OpenAI STT, and OpenAI TTS. The documentation describes LiveKit Agents as a bridge between a frontend connected over WebRTC and the OpenAI backend over WebSocket, and says it handles audio buffering, text-to-audio synchronization, interruptions, and telephony.[LiveKit: OpenAI Integration](https://docs.livekit.io/agents/integrations/openai/) [LiveKit: OpenAI Realtime Plugin](https://docs.livekit.io/agents/models/realtime/plugins/openai/)

## The Four Stages of the OpenAI–LiveKit Relationship

| Phase | Timing | What happened | Evidence of the change | Assessment |
|---|---|---|---|---|
| Hidden co-development | At least around September 2023, possibly earlier | ChatGPT Voice Mode launched; LiveKit later said the two companies built the product together | LiveKit's 2025 retrospective uses “together with OpenAI”; in October 2024, OpenAI and LiveKit publicly described the use of LiveKit SDKs and LiveKit Cloud in ChatGPT's voice architecture | A substantial engineering relationship existed, but there was no public announcement of an exclusive contract |
| Technical deepening | January–October 2024 | LiveKit released Agents; OpenAI released GPT-4o, Advanced Voice, and the Realtime API | LiveKit wrapped the OpenAI Realtime API in its Multimodal Agent API; both sides publicly described the ChatGPT Voice architecture | The relationship moved from internal product engineering into a developer platform, and LiveKit's role became explicit |
| Joint productization | October 2024–2025 | Developers could use LiveKit to build Advanced Voice-like applications while OpenAI expanded its Realtime API, audio models, and production capabilities | LiveKit maintained the OpenAI plugin; OpenAI's Realtime API added streaming audio, function calling, interruptions, and telephony | The two sides reinforced each other: OpenAI supplied the flagship model and use case, while LiveKit supplied communications, telephony, and agent operations |
| Open ecosystem and possible dilution | 2025–July 2026 | OpenAI added direct WebRTC, GA Realtime API, gpt-realtime, and GPT-Live; LiveKit added hundreds of model integrations and its own Inference and agent platform | OpenAI can connect clients without LiveKit; LiveKit openly supports other models and its own platform; the latest OpenAI Voice launch focuses on GPT-Live's internal architecture rather than naming LiveKit as a core product component | The relationship continues, but it has shifted from “co-building a flagship product” to “OpenAI as one important model partner for LiveKit” |

## Why the Relationship May Be Moving from Deep Cooperation to a Looser Ecosystem Tie

### 1. OpenAI Has an Incentive to Bring More of the Communications Layer In-House

At the beginning of the partnership, OpenAI needed to get GPT-4o audio to real users quickly. LiveKit already had mature WebRTC infrastructure, global network coverage, reconnection logic, and media handling, making it a natural partner.

As the Realtime API matured, OpenAI had three reasons to provide more direct access:

- **Lower the integration barrier:** Developers need only an OpenAI API instead of learning another platform's accounts, billing, and runtime.
- **Remove an intermediate layer:** Fewer forwarding layers can make latency optimization, incident debugging, and data boundaries easier.
- **Control the product cadence:** OpenAI can coordinate the model, protocol, client SDK, and voice product as one stack.

Direct WebRTC appeared in December 2024, the Realtime API became production-ready in August 2025, and OpenAI continued its own GPT-Realtime and GPT-Live product lines in 2026. These are signs that OpenAI does not need to depend forever on one real-time communications provider.

### 2. LiveKit Has an Incentive to Become Model-Neutral

LiveKit's long-term value is not any single model's voice; it is the real-time agent infrastructure around the model. An enterprise may use OpenAI today and another model tomorrow, or combine several models: one for live conversation, another for deeper reasoning, and a third for transcription or speech synthesis, with the final experience delivered over a phone, browser, mobile app, or robot.

LiveKit's public product direction reflects this. Agents has a plugin architecture, its documentation supports OpenAI, Azure OpenAI, and other providers, and its Series C announcement emphasizes hundreds of model integrations. OpenAI's success helps LiveKit, but OpenAI should not be the platform's only upstream provider.

### 3. The Level of Cooperation Has Changed

The early relationship looked like joint work on a specific product problem: How could ChatGPT Voice listen and speak with low latency?

The current relationship looks more like a standardized integration between the model layer and the infrastructure layer: OpenAI maintains the Realtime API, LiveKit maintains the plugin and agent framework, and developers decide whether LiveKit is useful for their application.

That is not necessarily a deterioration. It is a common shift as products mature: from custom co-development to standard interfaces, and from a single project to interchangeable ecosystem components.

## Evidence That the Partnership Continues—and Evidence That It May Be Less Exclusive

### Evidence that the partnership continues

1. LiveKit's current OpenAI integration documentation still lists the Realtime API, GPT-4o, GPT-5, OpenAI STT, and OpenAI TTS.
2. The LiveKit OpenAI Realtime plugin still provides Python and Node.js usage and authenticates with an OpenAI API key.
3. LiveKit's 2026 Series C announcement still says that Agents was shaped by the work behind ChatGPT Voice Mode.
4. The combination remains useful in practice: OpenAI provides the voice model, while LiveKit handles frontend media, state, telephony, and the agent lifecycle.

### Evidence that the relationship may be less exclusive

1. OpenAI added direct WebRTC to the Realtime API in December 2024, allowing developers to connect clients without LiveKit.
2. In August 2025, OpenAI made the Realtime API and `gpt-realtime` production-ready and began covering more tools, image input, SIP telephony, and model capabilities itself.
3. When OpenAI launched GPT-Live in 2026, its product story centered on the company's own full-duplex model, background-model delegation, and ChatGPT Voice experience, without continuing to present LiveKit as a central public component. This is only weak evidence: the absence of a public mention does not prove that LiveKit is no longer used under the hood.
4. LiveKit is also reducing its dependence on any one model by supporting hundreds of models, its own Inference product, Agent Builder, and partnerships across the broader ecosystem.

The most defensible conclusion is therefore: **the technical compatibility and commercial relationship still exist, but LiveKit's special position as the key bridge that turned OpenAI Advanced Voice into a developer platform has become less pronounced since 2025.**

## What Each Company Gains from the Relationship

### What OpenAI gains

- **Faster product delivery:** It did not need to build a global real-time media network from scratch.
- **Real-world voice engineering feedback:** Network jitter, packet loss, echo, interruptions, and long-lived connections expose problems that model benchmarks alone cannot reveal.
- **A developer-ecosystem entry point:** LiveKit's open-source Agents framework made it easier for developers to try the OpenAI Realtime API.
- **Coverage across phones and devices:** LiveKit's SIP, WebRTC, and cross-platform SDKs can bring the model to browsers, mobile apps, customer-support lines, and robots.

### What LiveKit gains

- **A flagship reference case:** ChatGPT Voice is the most recognizable example of a real-time AI product.
- **Technical credibility:** LiveKit can demonstrate that its infrastructure supports demanding AI voice workloads, not only video meetings or voice rooms.
- **Product direction:** OpenAI Voice Mode and similar projects exposed real requirements around agent dispatch, interruptions, state migration, and long-lived sessions.
- **Developer traffic from the model ecosystem:** OpenAI's Realtime API brings potential users, while LiveKit expands the platform's value through Agents, Cloud, and telephony.

## Implications for the Industry and for Investment Research

### 1. OpenAI and LiveKit Are Not Pure Competitors

OpenAI's primary arena is models and AI products. LiveKit's primary arena is real-time interaction infrastructure and agent runtimes. There is some overlap at the “voice-agent platform” layer, but the larger relationship remains complementary.

The clearest competitive pressure will likely appear in three areas: whether OpenAI's direct WebRTC, SIP, and Agents SDK cover LiveKit's basic functions; whether LiveKit can make it easy for developers to switch models and thereby reduce OpenAI's control over the application layer; and which company owns the enterprise customer, telephony entry point, session data, and agent runtime.

### 2. The Value of a Voice Agent Is Not Just the Quality of Its Answers

Production readiness also depends on time to first audio, recovery after an interruption, stability during long calls, integration with telephony and business systems, observability across every session, and privacy, security, recording-retention, and regional-compliance controls.

That is why OpenAI cannot deliver the entire product experience with a voice model alone, and why LiveKit can still have value even when OpenAI offers direct WebRTC.

### 3. “OpenAI Uses LiveKit” Does Not Mean “LiveKit Is Controlled by OpenAI”

The public materials reviewed for this article do not show that OpenAI acquired LiveKit, that LiveKit serves only OpenAI, or that the companies have an exclusive partnership. What the public record does support is that LiveKit says it helped build ChatGPT Voice Mode with OpenAI; LiveKit disclosed the use of LiveKit SDKs and LiveKit Cloud in the ChatGPT Voice architecture; LiveKit continued to maintain an OpenAI plugin while supporting other models; and OpenAI gradually added its own direct real-time access and voice-agent products.

The most reasonable characterization is: **LiveKit is an important infrastructure partner and ecosystem amplifier for OpenAI's voice capabilities, but it is not the only foundation of OpenAI's voice business.**

## Signals Worth Tracking Next

1. **Whether OpenAI's official architecture diagrams continue to name LiveKit:** If a new generation of ChatGPT Voice or Realtime products moves entirely to an OpenAI-owned real-time stack, underlying dependence is likely falling.
2. **The update cadence of LiveKit's OpenAI plugin:** Fast support for new OpenAI models and features would suggest an active relationship; long delays would suggest compatibility maintenance rather than close cooperation.
3. **Who owns billing and the customer relationship:** The choice between LiveKit Inference and a direct OpenAI connection affects which company sits closer to developers and enterprise buyers.
4. **Telephony and enterprise-agent capabilities:** OpenAI's expansion into SIP, contact centers, and deployment management will determine how far it moves into LiveKit's core territory.
5. **Whether multi-model switching becomes mainstream:** If enterprises prioritize model portability, LiveKit's neutral platform value should rise. If they prefer an all-in-one OpenAI product, the value of LiveKit as an intermediate layer will face more pressure.

## Final Assessment

OpenAI's AI voice story did not suddenly begin with GPT-4o. It developed layer by layer: Whisper helped the system understand speech in 2022; ChatGPT brought voice to users in 2023; GPT-4o and the Realtime API turned low-latency voice interaction into a model and platform capability in 2024; OpenAI pushed voice agents toward production in 2025; and in 2026 it continued toward continuous listening and speaking, real-time translation, tool use, and background delegation for deeper work.

LiveKit's story also did not begin with an OpenAI plugin. It started with open-source WebRTC infrastructure in 2021, added a global cloud network in 2022, accumulated experience in real AI voice projects in 2023–2024, extracted that experience into the Agents framework, and then expanded into a multi-model platform covering telephony, deployment, testing, and monitoring.

The two paths met around 2023, reached their closest public alignment around GPT-4o and the Realtime API in 2024, and became most explicit in the October 2024 partnership announcement. In 2025 and 2026, OpenAI gained more of its own real-time and agent capabilities, while LiveKit embraced more models and customers. The relationship therefore shifted from “co-building a flagship product” to an open partnership between a model provider and a real-time agent-infrastructure platform.

**The most accurate conclusion is not that OpenAI abandoned LiveKit. It is that OpenAI has gradually gained the ability to work around LiveKit, while LiveKit has gained the ability to operate without depending on OpenAI. The partnership continues, but its bargaining balance and technical necessity are less concentrated than they were in 2024.**
