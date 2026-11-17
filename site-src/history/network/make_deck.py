"""Write the slides of "Down the Wire", the history of networks and protocols.

Run this script to regenerate deck/deck.json and deck/slides/*.html in the Slides artifact format.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from deckkit import (CARD, MONO, NAVY, PART, SERIF, add, cards, chip, code, dated, divider,  # noqa: E402
                     head, section_open, write)

OUT = Path(__file__).resolve().parent / "deck"

# ---------------------------------------------------------------- introduction
add("cover", section_open("cover", True, "display:flex;flex-direction:column;justify-content:center;gap:40px") +
    '<p style="font-size:32px;font-weight:700;color:#C9D2E3;letter-spacing:4px;text-transform:uppercase">A history of the web, from underneath</p>'
    f'<h1 style="{SERIF};font-size:120px;font-weight:700;line-height:1.05">Down the Wire</h1>'
    '<p style="font-size:44px;line-height:1.4;color:#C9D2E3;max-width:1400px">How networks and protocols carried the web, and how each faster, wider pipe changed what a website could be.</p>'
    '<div style="display:flex;gap:16px">' + chip("Network", 28) + chip("Server", 28) + '</div>'
    '<aside>Every page, script and database query travels over a network. This talk follows the wires, radios and rules that carry them, from a two-letter message in 1969 to 5G. The thread through it is simple: each time the pipe got wider or faster, websites changed shape to fill it.</aside></section>',
    ("s1", "The colours and the plan for the talk"))

add("five-parts", section_open("five-parts", False) + head("The colour key", [], "The road under every request", False) +
    '<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr 1fr;gap:28px">' +
    "".join(
        f'<div style="display:flex;flex-direction:column;gap:16px;background:{CARD};padding:32px;border:2px solid #D9D3C7;border-top:16px solid {PART[p][0]};border-radius:16px">'
        f'<x-icon name="{icon}" style="color:{PART[p][1]};width:56px;height:56px"></x-icon>'
        f'<h3 style="font-size:36px;font-weight:700;color:{PART[p][1]}">{p}</h3>'
        f'<p style="font-size:24px;line-height:1.4;color:#3D4A63">{text}</p></div>'
        for p, icon, text in [
            ("HTML", "Book", "The page itself, which has to travel to the reader."),
            ("CSS", "Star", "The look of the page, sent alongside it."),
            ("Scripts", "Code", "Code in the browser that opens connections and sends requests."),
            ("Server", "Settings", "The computer at the other end that answers."),
            ("Network", "Globe", "The wires, radios and agreed rules that carry every byte between them."),
        ]) +
    '</div><p style="font-size:30px;line-height:1.45;color:#3D4A63">The rules are called <b>protocols</b>: agreements about how two machines talk. Teal marks the network and its protocols, which carry everything else.</p>'
    '<aside>Every slide carries a tag in these colours, with its name written on it, so nobody has to rely on colour alone. Most of this talk is teal. The other colours appear where a change in the network changed what pages, scripts or servers could do.</aside></section>')

PLAN = [
    ("1", "1969 to 1990", "Packets find their way", ["Network"]),
    ("2", "1991 to 1999", "The web over a phone line", ["Network", "HTML"]),
    ("3", "1998 to 2007", "Always on", ["Network", "Server"]),
    ("4", "2007 to 2014", "The web in your pocket", ["Network", "Scripts"]),
    ("5", "2015 to 2022", "Faster, and encrypted by default", ["Network"]),
    ("6", "2014 to now", "Heavier pages, uneven networks", ["Network", "HTML"]),
    ("7", "Today", "Putting it together", ["Network", "Server", "Scripts"]),
]
add("timeline", section_open("timeline", True, "display:flex;flex-direction:column;gap:48px;padding:112px 128px") +
    '<div style="display:flex;flex-direction:column;gap:16px"><p style="font-size:24px;font-weight:700;color:#C9D2E3;letter-spacing:3px;text-transform:uppercase">The plan</p>'
    f'<h2 style="{SERIF};font-size:72px;font-weight:700;line-height:1.1">Seven chapters, from 1969 to now</h2></div>'
    '<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:40px">' +
    "".join(
        f'<div style="display:flex;flex-direction:column;gap:10px;border-top:6px solid #C9D2E3;padding:16px 0 0 0">'
        f'<div style="display:flex;gap:20px;align-items:baseline"><p style="{SERIF};font-size:48px;font-weight:700;color:#C9D2E3">{n}</p>'
        f'<p style="font-size:22px;font-weight:700;color:#C9D2E3">{years}</p></div>'
        f'<h3 style="font-size:30px;font-weight:700;line-height:1.2">{title}</h3>'
        '<div style="display:flex;flex-wrap:wrap;gap:10px">' + "".join(chip(c, 22) for c in chips) + '</div></div>'
        for n, years, title, chips in PLAN) +
    '</div><aside>The network is older than the web by twenty years, so chapter 1 starts in 1969. Chapters overlap, because new networks arrived in some places years before others. Chapter 6 looks at how unevenly that happened.</aside></section>')

# ---------------------------------------------------------------- chapter 1
divider("ch1", 1, "1969 to 1990", "Packets find their way",
        "Before the web, researchers built a network that could carry any message, by any route, between any computers.",
        ["Network"], "This chapter lays the ground every later chapter stands on: packets, addresses and names. None of it was built for the web, which arrived twenty years later.",
        ("s2", "Chapter 1, 1969 to 1990: packets find their way"))

cards("packets", "29 October 1969", ["Network"], "The first message, and the idea of a packet",
      [("Packet switching", "A message is cut into small packets. Each packet carries the address it is going to, and can take any free route there. The receiver puts them back in order.", "Network", "HELLO → [H][E][L][L][O] → HELLO"),
       ("The first message", "On 29 October 1969 a student at UCLA tried to log in to a computer at Stanford Research Institute over ARPANET. The system crashed after two letters, so the first message was “LO”.", "Network", None)],
      "A telephone call holds one line open for the whole conversation. Packets share the lines, so a broken link only means a different route.",
      "Leonard Kleinrock's lab at UCLA sent the message. The network was funded by ARPA, part of the US Department of Defense, and linked four universities by the end of 1969. Packet switching is why the internet survives broken links: traffic flows round them.")

dated("tcpip", "1974 to 1983", ["Network"], "TCP/IP: one language for every network",
      ["By the 1970s there were many separate networks. Vint Cerf and Bob Kahn designed a way to join them: <b>IP</b> gives every computer an address and moves packets between networks, and <b>TCP</b> checks that every packet arrived, in order, and asks again for any that went missing.",
       '<span style="font-family:\'JetBrains Mono\', monospace;font-size:28px">IP address: 192.0.2.17</span>'],
      [("1974", "Cerf and Kahn publish their design for joining networks together.", "Network"),
       ("1 January 1983", "“Flag day”: ARPANET switches to TCP/IP. Computers that had not changed over were cut off.", "Network"),
       ("Today", "Every device on the internet still speaks IP, from a phone to a fridge.", "Network")],
      "A network of networks is what the word internet means. Flag day is a rare case of everyone switching at once, and it worked only because the network was still small, a few hundred computers.", dark=True)

code("dns", "1983", ["Network"], "DNS: names instead of numbers",
     ["People remember names, and computers route by numbers. In 1983 Paul Mockapetris designed the Domain Name System, which turns a name into an address.",
      "No single computer holds every name. Each level knows who to ask next."],
     "looking up www.example.ie",
     "1  root: ask the .ie servers<br>2  .ie: ask example.ie’s servers<br>3  example.ie: www is 192.0.2.17<br><br>then the browser connects to 192.0.2.17",
     "Your computer remembers answers for a while, so most lookups take a few milliseconds.",
     "DNS is the first step of almost every visit to a website, and when it breaks, sites seem to vanish even though their servers are fine. Each answer carries a time to live, which says how long it can be remembered.")

# ---------------------------------------------------------------- chapter 2
divider("ch2", 2, "1991 to 1999", "The web over a phone line",
        "Most people reached the web through a modem that turned data into sound on a telephone line. Every byte counted.",
        ["Network", "HTML"], "This chapter shows the network shaping the page. Designers built for slow, noisy connections, and the protocol itself grew up to make each connection go further.",
        ("s3", "Chapter 2, 1991 to 1999: the web over a phone line"))

dated("http1", "1991 to 1997", ["Network", "Server"], "HTTP: the web’s own protocol",
      ["HTTP is the protocol a browser and a web server use. It runs on top of TCP, so it can assume every byte arrives.",
       '<span style="font-family:\'JetBrains Mono\', monospace;font-size:26px">GET /index.html HTTP/1.1<br>Host: www.example.ie</span>'],
      [("1991 · HTTP/0.9", "One line: GET and a path. The answer was HTML and nothing else.", "Network"),
       ("1996 · HTTP/1.0", "Adds status codes such as 404, and headers that describe the content, so images could travel too.", "Network"),
       ("1997 · HTTP/1.1", "Keeps a connection open for several requests, and adds the Host header, so one server could hold many sites.", "Server")],
      "The Host header changed the business of the web. Before it, every site needed its own IP address. After it, one cheap server could host hundreds of small sites, which is what made shared hosting so cheap.", dark=True)

add("dialup", section_open("dialup", False) + head("1991 to 1999", ["Network", "HTML"], "How long did a page take?", False) +
    '<div style="display:grid;grid-template-columns:1.1fr 1fr;gap:64px;align-items:center">'
    '<table style="font-size:28px;color:#1B2A4A"><tr><th style="width:44%">Connection</th><th style="width:28%">Speed</th><th style="width:28%">A 100 KB page</th></tr>'
    '<tr><td>Modem, about 1994</td><td>14.4 kbit/s</td><td>about 56 s</td></tr>'
    '<tr><td>Modem, about 1996</td><td>28.8 kbit/s</td><td>about 28 s</td></tr>'
    '<tr><td>56k modem, 1998</td><td>56 kbit/s</td><td>about 14 s</td></tr>'
    '<tr><td>Early broadband, 2002</td><td>1 Mbit/s</td><td>under 1 s</td></tr></table>'
    '<div style="display:flex;flex-direction:column;gap:24px">'
    '<p style="font-size:28px;line-height:1.45;color:#3D4A63">Pages were built for that wait: small GIF images, few colours, text that appeared first, and images that loaded in coarse stripes, then sharpened.</p>'
    '<p style="font-size:28px;line-height:1.45;color:#3D4A63">The <b>alt</b> text on an image was often what a visitor read while the picture arrived, or instead of it.</p>'
    '<p style="font-size:24px;color:#5A6478">Times are the nominal speed and ignore overheads, so real pages took longer.</p></div></div>'
    '<aside>To work out a time: kilobytes times 8 gives kilobits, then divide by the speed. 100 times 8 is 800 kilobits, and 800 divided by 14.4 is about 56 seconds. The 56k standard, V.90, was agreed in 1998. A modem also tied up the phone line, so nobody could ring the house while someone was online.</aside></section>')

cards("ssl", "1995 to 1999", ["Network", "Server"], "A lock for the connection",
      [("SSL, 1995", "Netscape added SSL to its browser so that a connection could be encrypted. A card number could now cross the internet without anyone on the way reading it.", "Network", "https:// and a padlock"),
       ("TLS, 1999", "The standards body took SSL over and renamed it TLS. Every padlock in a browser today is TLS.", "Network", None)],
      "Encryption made online shopping possible. For years it was slow and expensive, so only the payment pages used it.",
      "Encryption costs a little time at the start of each connection, for the two computers to agree on keys. On 1990s hardware that cost was large, which is why sites encrypted only the pages that needed it. Chapter 5 shows how that changed.", dark=True)

# ---------------------------------------------------------------- chapter 3
divider("ch3", 3, "1998 to 2007", "Always on",
        "Broadband and Wi-Fi left the connection open all day. Sites could send more, more often, to more places.",
        ["Network", "Server"], "The shift from dialling in to always on changed habits as much as speed. People checked a site many times a day, and sites began to update themselves.",
        ("s4", "Chapter 3, 1998 to 2007: always on"))

cards("broadband", "About 1999 to 2005", ["Network", "Scripts"], "Broadband changes what a page can do",
      [("Always on", "DSL over phone lines and cable modems over TV cables gave connections that stayed open, at a megabit or more.", "Network", None),
       ("Scripts in the background", "With the connection always there, a page could ask the server for small updates every few seconds. That is the Ajax pattern of 2005.", "Scripts", "Gmail, 2004 · Google Maps, 2005"),
       ("Video", "YouTube launched in 2005. Streaming video to anyone needed both broadband homes and cheap bandwidth for the server.", "Network", None)],
      "Each of these was possible earlier in a lab. Broadband made it possible for ordinary visitors.",
      "Ask the class to imagine Google Maps on a 28.8 modem: every drag of the map fetches new image tiles. The design only works when fetching is cheap and quick.")

dated("wifi", "1997 to 2003", ["Network"], "Wi-Fi cuts the cable",
      ["Wi-Fi carries network packets over radio. The standard is called 802.11, and the name Wi-Fi came from the industry group that tested devices against it.",
       "A laptop could now be online anywhere in a building, and soon in cafés, stations and airports."],
      [("1997", "The first 802.11 standard, at 2 Mbit/s.", "Network"),
       ("1999", "802.11b reaches 11 Mbit/s, and the Wi-Fi Alliance forms to certify devices.", "Network"),
       ("2003", "Laptops start to include Wi-Fi as standard.", "Network")],
      "Radio is shared and noisy, so Wi-Fi spends much of its time on taking turns and resending lost packets. That is why it feels slower than its headline speed, and why a busy café network crawls.", dark=True)

cards("cdn", "1998 onwards", ["Network", "Server"], "Content delivery networks: copies near the reader",
      [("The problem", "Light in fibre needs at least 80 milliseconds to cross from Dublin to San Francisco and back. A page with many files makes that trip many times.", "Network", None),
       ("The fix", "A content delivery network keeps copies of a site’s images, styles and scripts on servers in many cities, and answers each visitor from the nearest one. Akamai, founded in 1998, was the first big one.", "Server", "Dublin visitor → Dublin copy, not California")],
      "Distance became a design problem. Bandwidth can grow, but nothing makes light faster.",
      "This is the first big change to the shape of a site: the origin server keeps the data and the pages, and copies of the heavy files live all over the world. Most large sites, and many small ones, now sit behind a CDN.", dark=False)

# ---------------------------------------------------------------- chapter 4
divider("ch4", 4, "2007 to 2014", "The web in your pocket",
        "Phones put the web on slow, patchy radio links, and the same pages had to work on all of them.",
        ["Network", "Scripts"], "Mobile networks brought the web to billions of people, often as their only connection. They also brought high latency and dropped signals, which changed how pages had to be built.",
        ("s5", "Chapter 4, 2007 to 2014: the web in your pocket"))

dated("mobile", "2001 to 2009", ["Network", "CSS"], "Mobile data grows up",
      ["The first iPhone, in 2007, showed full web pages on a phone, over a 2G network called EDGE at well under a megabit.",
       "Mobile networks add <b>latency</b>, the delay before anything arrives. A phone often waits hundreds of milliseconds for the first byte, however fast the download."],
      [("2001", "The first 3G network opens, in Japan.", "Network"),
       ("2008", "The iPhone 3G brings faster mobile data to a mass audience.", "Network"),
       ("14 December 2009", "The first commercial 4G LTE networks open in Stockholm and Oslo.", "Network")],
      "Two ideas to keep apart. Bandwidth is how much arrives each second, like the width of a pipe. Latency is how long the first drop takes to arrive, like the length of the pipe. Mobile improved bandwidth faster than latency.", dark=True)

code("websocket", "2011", ["Network", "Scripts"], "WebSocket: a line that stays open",
     ["Ajax asks, the server answers, and the line closes. For a chat or a live score, a page had to keep asking “anything new?” every few seconds.",
      "WebSocket, standardised in 2011, keeps one connection open in both directions, so the server can send news the moment it happens."],
     "in the browser",
     "const socket = new WebSocket(<br>  \"wss://chat.example.ie\");<br><br>socket.onmessage = (event) =&gt; {<br>  showMessage(event.data);<br>};",
     "Polling sends hundreds of empty questions. A socket sends only the answers.",
     "Live chat, shared documents and multiplayer games in the browser rely on this. On a phone it also saves battery, because the radio wakes up only when there is news.")

cards("mobile-design", "2010 onwards", ["Network", "HTML", "CSS"], "Designing for the slowest likely connection",
      [("Responsive images", "HTML gained ways to offer several sizes of an image, so a phone downloads a small one.", "HTML", "&lt;img srcset=\"small.jpg 480w, big.jpg 1600w\"&gt;"),
       ("Lazy loading", "Images further down the page wait until the reader scrolls near them.", "HTML", "&lt;img loading=\"lazy\"&gt;"),
       ("Mobile first", "Designers start from the phone layout and add to it for wide screens.", "CSS", None)],
      "The network had become part of the design brief.",
      "Each of these saves bytes on a slow or metered connection. Lazy loading became a plain HTML attribute from 2019, as browsers added it one by one; before that it needed a script.", dark=True)

# ---------------------------------------------------------------- chapter 5
divider("ch5", 5, "2015 to 2022", "Faster, and encrypted by default",
        "The protocols themselves were rebuilt: more requests at once, quicker handshakes, and a new transport for mobile.",
        ["Network"], "For twenty years HTTP barely changed. Between 2015 and 2022 it changed twice, and encryption went from optional to normal.",
        ("s6", "Chapter 5, 2015 to 2022: faster, and encrypted by default"))

cards("http2", "May 2015", ["Network", "HTML"], "HTTP/2: many requests on one connection",
      [("HTTP/1.1", "Browsers opened about six connections to a site and sent one request at a time on each. Pages with a hundred files waited in queues.", "Network", "1 · 2 · 3 · 4 · 5 · 6, then wait"),
       ("HTTP/2", "Many requests travel together on one connection, interleaved. Nothing waits for a slow file in front of it.", "Network", "all at once, on one line")],
      "Old speed tricks, such as joining every image into one big sprite sheet, stopped being necessary.",
      "HTTP/2 grew from SPDY, an experiment Google began in 2009. It is a good example of a technology moving from one company's test into a shared standard. The request and response look the same to a web developer; only the way they travel changed.")

dated("tls13", "2015 to 2018", ["Network", "Server"], "Encryption becomes the default",
      ["Free certificates from Let’s Encrypt, from December 2015, removed the cost of HTTPS. Browsers then began to warn about every plain HTTP page.",
       "TLS 1.3, in August 2018, cut the handshake from two round trips to one, so encryption barely slows the start of a visit."],
      [("2015", "Let’s Encrypt opens to the public with free certificates.", "Network"),
       ("2018", "TLS 1.3 is published. Chrome marks plain HTTP as “Not secure”.", "Network"),
       ("2025", "About 88 per cent of sites send visitors to HTTPS by default.", "Server")],
      "The 2025 figure comes from W3Techs. Encryption also hides which page on a site someone reads, from anyone on the same network. It does not hide which site they visit.", dark=True)

dated("http3", "2021 and 2022", ["Network"], "HTTP/3: a new road for mobile",
      ["TCP delivers bytes strictly in order, so one lost packet holds up everything behind it. On a patchy mobile signal that happens often.",
       "QUIC, standardised in May 2021, replaces TCP for the web. It runs over UDP, a simpler protocol, and handles each stream on its own, so one loss holds up only its own stream. <b>HTTP/3</b>, in June 2022, is HTTP over QUIC."],
      [("2013", "Google starts testing QUIC in Chrome.", "Network"),
       ("May 2021", "QUIC becomes a standard.", "Network"),
       ("June 2022", "HTTP/3 becomes a standard.", "Network")],
      "QUIC also survives a change of network. A phone that walks out of Wi-Fi onto 4G can keep the same connection, where TCP would have to start again.")

dated("five-g", "2019 onwards", ["Network"], "5G, fibre and Wi-Fi 6",
      ["The last mile got much faster in the late 2010s. Fibre to the home, 5G mobile and Wi-Fi 6 all arrived within a few years of each other.",
       "Headline speeds now reach a gigabit or more. The web did not need that speed for pages; video, games and large downloads used it."],
      [("April 2019", "The first 5G phone networks open, in South Korea and the United States.", "Network"),
       ("2019", "Wi-Fi 6 devices arrive.", "Network"),
       ("2020s", "Fibre replaces copper phone lines in many homes.", "Network")],
      "The pattern from chapter 3 repeats: a faster pipe arrives, and new uses fill it. Ask the class what they do on a phone now that would have been impossible in 2010.", dark=True)

# ---------------------------------------------------------------- chapter 6
divider("ch6", 6, "2014 to now", "Heavier pages, uneven networks",
        "Pages grew as fast as connections did, and a third of the world is still not online.",
        ["Network", "HTML"], "This chapter turns the story round. Faster networks did not make the web fast for everyone, because pages grew to fill them, and many people still have slow connections or none.",
        ("s7", "Chapter 6, 2014 to now: heavier pages, uneven networks"))

add("page-weight", section_open("page-weight", False) + head("2014 to 2024", ["HTML", "Network"], "Pages grew to fill the pipe", False) +
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:center">'
    '<div style="display:flex;flex-direction:column;gap:28px">'
    '<div style="display:flex;flex-direction:column;gap:8px"><p style="font-size:26px;font-weight:700;color:#5A6478">Median page on a phone, 2014</p>'
    '<div style="display:flex;align-items:center;gap:20px"><div style="width:110px;height:56px;background:#7CC6C1;border-radius:8px"></div><p style="font-size:36px;font-weight:700">505 KB</p></div></div>'
    '<div style="display:flex;flex-direction:column;gap:8px"><p style="font-size:26px;font-weight:700;color:#5A6478">Median page on a phone, 2024</p>'
    '<div style="display:flex;align-items:center;gap:20px"><div style="width:500px;height:56px;background:#1F6B66;border-radius:8px"></div><p style="font-size:36px;font-weight:700">2,311 KB</p></div></div>'
    '<p style="font-size:24px;color:#5A6478">Source: HTTP Archive, Web Almanac 2024</p></div>'
    '<div style="display:flex;flex-direction:column;gap:24px">'
    '<p style="font-size:28px;line-height:1.45;color:#3D4A63">The median page on a phone grew more than four times over in ten years. Most of the weight is images and scripts.</p>'
    '<p style="font-size:28px;line-height:1.45;color:#3D4A63">That 2024 page would take about <b>5½ minutes</b> on a 1998 modem, and about a second on good 4G.</p></div></div>'
    '<aside>The arithmetic: 2,311 kilobytes is about 18,500 kilobits, and at 56 kilobits a second that is about 330 seconds. On a 20 megabit 4G link it is just under a second. Desktop pages grew from 1,208 KB to 2,652 KB over the same years. The point is not that pages should be tiny; it is that every byte is paid for by someone on a slow or metered connection.</aside></section>')

cards("divide", "2024", ["Network"], "Who is still offline?",
      [("Online", "About 5.5 billion people used the internet in 2024, 68 per cent of the world’s population.", "Network", None),
       ("Offline", "About 2.6 billion people did not. Most live in low-income countries and rural areas.", "Network", None),
       ("Slow and metered", "Many people online pay for each gigabyte, or share one phone in a household.", "Network", None)],
      "Source: International Telecommunication Union, Facts and Figures 2024.",
      "The S-curve from the start of the talk has not reached the top, and it is flattening slowly. A site that loads in a second in Dublin may take a minute, and cost real money, somewhere else. Satellite services and cheaper phones are pushing the curve up, but the gap is still large.", dark=True)

cards("edge", "2017 onwards", ["Network", "Server"], "The server moves towards the reader",
      [("Edge functions", "CDNs began to run small programs, not only to store copies. A request can be answered in the nearest city without reaching the main server.", "Server", None),
       ("Caching rules", "Headers tell every browser and CDN how long a file may be kept, so most visits download only what changed.", "Network", "Cache-Control: max-age=31536000")],
      "The architecture keeps shifting to beat distance: data in one place, code and copies near every reader.",
      "This is chapter 3's content delivery network grown up. It also brings back an old question in a new form: if a page is built in two hundred cities, which copy is the true one, and how quickly do the others hear about a change?")

# ---------------------------------------------------------------- chapter 7
divider("ch7", 7, "Today", "Putting it together",
        "What happens between pressing Enter and seeing a page, and the habits that keep a site fast on every network.",
        ["Network", "Server", "Scripts"], "The last chapter follows one visit down the wire and back, naming the chapter each step came from.",
        ("s8", "Chapter 7, today: putting it together"))

add("journey", section_open("journey", False) + head("Today", ["Network", "Server", "HTML"], "What happens when you press Enter", False) +
    '<div style="display:grid;grid-template-columns:repeat(5, 1fr);gap:16px">' +
    "".join(
        f'<div style="display:flex;flex-direction:column;gap:12px;background:{CARD};padding:28px;border:2px solid #D9D3C7;border-top:16px solid {PART[p][0]};border-radius:16px">'
        f'<p style="{SERIF};font-size:44px;font-weight:700;color:{PART[p][1]}">{n}</p>'
        f'<h3 style="font-size:30px;font-weight:700;color:{PART[p][1]}">{h}</h3>'
        f'<p style="font-size:24px;line-height:1.4;color:#3D4A63">{t}</p></div>'
        for n, p, h, t in [
            ("1", "Network", "DNS", "The name becomes an IP address."),
            ("2", "Network", "Connect", "TCP or QUIC opens a connection to that address."),
            ("3", "Network", "Encrypt", "TLS agrees keys, so nobody can read the traffic."),
            ("4", "Server", "Request", "HTTP asks for the page, and the server answers."),
            ("5", "HTML", "Render", "The browser builds the page, then fetches its images, styles and scripts."),
        ]) +
    '</div><p style="font-size:30px;line-height:1.45;color:#3D4A63">On a good connection all five take well under a second. On a slow mobile link, steps 1 to 3 alone can take a second, before a single byte of the page arrives.</p>'
    '<aside>Name the chapter each step came from: DNS from chapter 1, TCP from chapter 1 and QUIC from chapter 5, TLS from chapters 2 and 5, HTTP from chapter 2, and the many extra files from chapter 6. Every browser can show this sequence: open the developer tools, choose the Network tab and reload, then hover over the timing bar of the first request.</aside></section>')

cards("fast-habits", "Today", ["Network", "HTML", "Server"], "Five habits for every network",
      [("Weigh the page", "Check the total size in the developer tools. Images are usually the heaviest part.", "HTML", None),
       ("Right-size images", "Serve small images to small screens, in modern formats.", "HTML", None),
       ("Load lazily", "Let images and scripts below the fold wait.", "HTML", None),
       ("Cache", "Tell browsers and CDNs how long files can be kept.", "Server", None),
       ("Test slow", "Throttle the connection in the developer tools and watch the page load.", "Network", None)],
      "Each habit answers a constraint from this history: the modem, the phone, the distance, and the page that grew.",
      "Every browser's developer tools can pretend to be a slow 3G phone. Trying a site that way for a minute teaches more than any rule.", dark=True)

add("recap", section_open("recap", True, "display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center") +
    '<div style="display:flex;flex-direction:column;gap:32px"><p style="font-size:24px;font-weight:700;color:#C9D2E3;letter-spacing:3px;text-transform:uppercase">To take away</p>'
    f'<h2 style="{SERIF};font-size:72px;font-weight:700;line-height:1.1">Questions to talk over</h2>'
    '<p style="font-size:30px;line-height:1.45;color:#C9D2E3">Each question has more than one good answer. Pick one, and back it up with an example from the talk.</p></div>'
    '<ol style="font-size:30px;line-height:1.5;padding:0 0 0 40px;display:flex;flex-direction:column;gap:12px">'
    '<li>Which change in this history most changed what a website could do?</li>'
    '<li>What is the difference between bandwidth and latency? Which matters more for a phone?</li>'
    '<li>Why did pages get heavier as networks got faster?</li>'
    '<li>Who pays for a heavy page, and how?</li>'
    '<li>Load a site with the network throttled. What appears first, and what makes you wait?</li></ol>'
    '<aside>The last question needs the developer tools: open the Network tab, choose a slow throttling preset, and reload. Pairs can compare two sites they use often.</aside></section>')


def main():
    write(OUT, "Down the Wire")
    import adoption  # the opening section on adoption curves
    adoption.update_deck("network")
    import timeline  # every date in the story, before the recap
    timeline.update_deck("network")


if __name__ == "__main__":
    main()
