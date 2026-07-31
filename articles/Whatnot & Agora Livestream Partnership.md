On February 8, 2026, MrBeast hosted a major giveaway on Whatnot, a livestream shopping platform. Peak concurrent viewership reached 583,000, and more than 555,000 people entered the same giveaway round. The platform also attracted hundreds of thousands of new users within 24 hours. Ultimately, the event concluded without any major technical incidents.

The significance of this livestream went beyond setting a viewership record. It also demonstrated the technical capabilities of Whatnot and Agora in ultra-large-scale, real-time livestreaming. The original technical blog post is available at [Scaling Whatnot: Behind the Largest Live Shopping Stream in US History](https://medium.com/whatnot-engineering/scaling-whatnot-behind-the-largest-live-shopping-stream-in-us-history-040a458f538c).

### Whatnot's Technical Requirements and Solutions

#### Which Scenarios Created the Greatest Technical Demands?

Conventional online video primarily solves the problem of letting users watch content. Livestream commerce, however, must support video, comments, product displays, giveaways, follows, account registration, and purchases—all at the same time.

The real challenge in this event was not having 583,000 people passively watch. It was the possibility that, after MrBeast issued an instruction during the livestream, hundreds of thousands of users could click the same button within a single second. For example, when the host said, “Enter the giveaway now” or “Go follow me,” a huge volume of requests could suddenly hit the giveaway system, user profiles, and databases. This phenomenon is known as the “thundering herd effect,” in which large numbers of users access the same service at nearly the same time.

The platform therefore had to handle extremely high concurrency—the number of users accessing a system simultaneously—while also keeping video latency low, giveaway results accurate, and transactions uninterrupted, without affecting other livestreams on the platform.

#### Why Was the Technical Challenge So Difficult?

The first challenge was the tension between scale and low latency.

Whatnot originally used WebRTC, a networking technology designed for real-time audio and video transmission, to deliver livestreams with latency of only a few hundred milliseconds. But when hundreds of thousands of users are online in a single livestream, this architecture can cause connection counts, traffic, and computing pressure to rise sharply.

The second challenge was the potential for cascading effects across systems.

As the application layer scales out, every application server needs connections to systems such as Redis, OpenSearch, and Kafka. Increasing the number of servers also increases the number of connections, potentially exceeding the capacity of underlying systems and triggering a “cascading failure,” in which a problem in one system causes failures in multiple other systems.

The third challenge was unpredictable traffic.

Livestreams do not follow a fixed workflow. A single sentence from the host can instantly trigger simultaneous actions from hundreds of thousands of users. Traditional, gradually ramped load tests have difficulty simulating this kind of sudden burst.

#### How Did Whatnot Address These Challenges?

First, Whatnot developed a CAS admission-control system, a service that controls when new users are allowed to enter the platform. When traffic exceeds a safe threshold, the system limits new users from entering but does not affect people who are already watching or completing transactions, helping prevent a platform-wide outage.

Second, Whatnot introduced a proxy layer and connection pools between its application servers and data systems, allowing multiple services to reuse a fixed number of connections. Envoy was used to proxy Redis and OpenSearch, while Kafka was given a dedicated connection proxy. This prevented application-server scaling from causing connection counts to grow without limit.

Third, Whatnot built a “Doomsday Feed,” a backup information feed for peak periods. When the primary recommendation system came under excessive pressure, the platform automatically switched to a backup page with a simpler, cache-friendly structure, ensuring that users could still enter the livestream. During the event, approximately 95% of feed requests followed this path.

In addition, Whatnot split complex queries across independent database clusters so that heavy queries for orders and products would not affect core viewing and transaction flows. It also used as much as ten weeks of load testing in the production environment to identify and gradually eliminate system bottlenecks.

### What Role Did Agora Play in the Livestream?

For this livestream, Whatnot was primarily responsible for the application layer, including login, giveaways, products, transactions, and recommendations. Agora was responsible for the stable delivery of real-time video.

The two companies began preparing together approximately ten weeks in advance. Agora and Whatnot conducted large-scale testing, validating the video delivery path for up to 1.3 million concurrent users. They also tested scenarios including rapid user entry, sustained heavy load, and regional failover.

During the actual livestream, Agora supported 582,225 concurrent viewers in a single RTC channel, a real-time audio and video room. It kept time to first frame—the time from when a user enters the livestream to when the first frame appears—under one second, while maintaining stable overall video latency and image quality.

Under fluctuating network conditions, Agora maintained the viewing experience through adaptive bitrate, which automatically adjusts video quality based on network conditions; congestion control, which adjusts the sending rate in response to network congestion; and packet-loss resilience, which helps keep video playing continuously when some data is lost.

The two companies also formed a joint operations team of approximately 30 people to monitor the systems continuously for 72 hours and ensure that the livestream ran reliably.

### Agora's Competitive Advantages

The description of this livestream highlights several of Agora's core advantages.

**Supporting Ultra-Large-Scale, Single-Channel Livestreams**

During this event, Agora supported roughly 580,000 concurrent users in a single RTC channel while maintaining stable, low-latency video. This indicates that its systems can operate reliably in a scenario where users are highly concentrated in one livestream—not merely support a large aggregate user count across many rooms.

**Maintaining a Stable Experience on Complex Networks**

Throughout the livestream, Agora used adaptive bitrate, congestion control, and packet-loss resilience to preserve video continuity, stable image quality, and controllable latency despite network fluctuations. This demonstrates its ability to deliver real-time media under unstable network conditions.

**Providing Joint Engineering Support for Large-Scale Events**

For this livestream, Agora and Whatnot conducted joint testing ten weeks in advance and validated the delivery path at a scale of approximately 1.3 million users. Agora also provided 72 hours of continuous monitoring during the livestream and helped form a joint support team of approximately 30 people. This shows that Agora provides more than technical capabilities: it also offers end-to-end engineering collaboration and operational support.
