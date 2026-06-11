import pandas as pd
import plotly.graph_objects as go

df = pd.read_csv('npm_downloads_weekly.csv')
# df contains 'Date' as first column

descriptions = {
    "agora-rtc-sdk-ng": {
        "function": "Agora RTC SDK NG (Next Generation) is the Web SDK for Agora's real-time communication platform, providing audio, video, and screen sharing capabilities.",
        "use_case": "Developers use this to build web applications that require real-time voice and video calling, live interactive audio/video streaming, and web-based conferencing.",
        "fundamental": "This is the primary web SDK for Agora. High download volumes indicate strong developer adoption and ongoing maintenance of web applications using Agora. Tracking this shows the overall health and growth of Agora's web developer ecosystem."
    },
    "agora-rtc-sdk": {
        "function": "Agora RTC SDK (Legacy) is the older version of Agora's Web SDK.",
        "use_case": "Used in older web projects for real-time audio and video communication. Mostly maintained for legacy support.",
        "fundamental": "A declining trend is expected and healthy if accompanied by a corresponding or greater rise in 'agora-rtc-sdk-ng'. Steady downloads might indicate enterprise customers who are slow to migrate from legacy systems."
    },
    "rtc-sdk-total": {
        "function": "The combined total of Agora RTC SDK NG and the legacy Agora RTC SDK.",
        "use_case": "Represents the total web-based RTC usage and demand for Agora's services.",
        "fundamental": "This is a key metric for overall web market penetration. Continuous growth implies that Agora is acquiring new developers and maintaining existing ones across all web platforms, which is a bullish signal for their web communication business."
    },
    "agora-rtm-sdk": {
        "function": "Agora RTM (Real-time Messaging) SDK enables developers to add real-time messaging, signaling, and presence status to their apps.",
        "use_case": "Used for building chat applications, whiteboards, signaling for video calls, and real-time control features in interactive broadcasts.",
        "fundamental": "Downloads here indicate the attachment rate of secondary features. Strong RTM usage often pairs with RTC, showing developers are building complex, interactive applications (like live streaming with chat) rather than just basic video calls."
    },
    "agora-rtc-react": {
        "function": "A React wrapper for the Agora Web SDK NG, providing React hooks and components.",
        "use_case": "Used by React developers to quickly integrate Agora video/audio features into React-based web applications without writing boilerplate code.",
        "fundamental": "React is a dominant web framework. High growth here shows Agora is successfully catering to modern web development workflows, reducing friction for new adoptions in the large React developer community."
    },
    "react-native-agora": {
        "function": "The React Native SDK for Agora, allowing developers to build cross-platform mobile apps (iOS and Android) with real-time communication.",
        "use_case": "Used when developers want to build a mobile app with video/audio calling capabilities using React Native instead of native code (Swift/Kotlin).",
        "fundamental": "Indicates mobile footprint. Strong downloads show Agora's popularity in the cross-platform mobile development space, a cost-effective choice for many startups and mid-sized companies."
    },
    "agora-agent-server-sdk": {
        "function": "SDK for integrating Agora's conversational AI and server-side agents.",
        "use_case": "Used by backend developers to deploy AI agents that can join Agora channels, process audio/video streams, and interact with users in real-time.",
        "fundamental": "This reflects Agora's expansion into AI. Growing downloads represent developer interest in building next-gen AI-powered interactive applications, a potential new growth engine for the company."
    },
    "agora-agent-client-toolkit": {
        "function": "Client-side toolkit to interact with Agora's AI agents.",
        "use_case": "Used to manage the state, connection, and UI elements related to AI agents within the client application.",
        "fundamental": "Complements the server SDK. Adoption here shows end-to-end implementation of AI features in client-facing applications."
    },
    "agora-agent-uikit": {
        "function": "UI components specifically designed for Conversational AI applications on top of Agora.",
        "use_case": "Allows developers to quickly drop in pre-built UI elements (like voice visualizers or AI chat interfaces) for their AI agents.",
        "fundamental": "Measures the ease-of-use and developer experience for their AI products. High usage means developers are utilizing Agora's higher-level abstractions to speed up time-to-market."
    },
    "agora-conversational-ai-denoiser": {
        "function": "An AI-powered noise reduction extension for Agora's SDKs.",
        "use_case": "Used to eliminate background noise in harsh environments, improving audio clarity in calls or live streams.",
        "fundamental": "Shows demand for premium, high-quality audio features. High attachment rate indicates customers value audio quality and are willing to integrate advanced features, potentially reflecting higher-tier usage or enterprise adoption."
    }
}

html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Agora NPM Downloads Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f9f9f9; }
        .chart-container { background-color: white; padding: 20px; margin-bottom: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .description { margin-top: 20px; padding: 15px; background-color: #f1f8ff; border-left: 4px solid #0056b3; }
        h2 { color: #333; }
        p { line-height: 1.6; color: #555; }
        strong { color: #222; }
    </style>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <h1>Agora NPM Packages Download Dashboard</h1>
"""

for col in df.columns[1:]:  # Skip 'Date'
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df[col], mode='lines', name=col))

    fig.update_layout(
        title=f"Weekly Downloads: {col}",
        xaxis_title="Date",
        yaxis_title="Downloads",
        template="plotly_white",
        height=400
    )

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    desc = descriptions.get(col, {"function": "N/A", "use_case": "N/A", "fundamental": "N/A"})

    html_content += f"""
    <div class="chart-container">
        {plot_div}
        <div class="description">
            <p><strong>功能 (Function):</strong> {desc['function']}</p>
            <p><strong>需求场景 (Use Case):</strong> {desc['use_case']}</p>
            <p><strong>基本面含义 (Fundamental Implications):</strong> {desc['fundamental']}</p>
        </div>
    </div>
    """

html_content += """
</body>
</html>
"""

with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("HTML dashboard generated successfully.")
