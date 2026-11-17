"""Write the slides of "Behind the Page", the server and database history deck.

Run this script to regenerate deck/deck.json and deck/slides/*.html. The output uses the
same format as the Slides artifact, so the files can be published there unchanged.
"""

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "deck"
NAVY, CREAM, CARD = "#1B2A4A", "#F7F5F0", "#FFFDF9"
PART = {
    "HTML": ("#E8955C", "#A24A18"),
    "CSS": ("#8DB4E2", "#24588F"),
    "Scripts": ("#E9C46A", "#7A5D00"),
    "Server": ("#8CC9A6", "#2E6B4A"),
    "Database": ("#B9A6E0", "#5B3F9E"),
}
SERIF = "font-family:'Libre Baskerville', Georgia, serif"
MONO = "font-family:'JetBrains Mono', 'Courier New', monospace"
BASE = "font-family:'Public Sans', Arial, sans-serif;padding:128px"

slides, order, sections = {}, [], {}


def chip(name, size=24):
    pad = "6px 18px" if size <= 24 else "8px 24px"
    return (f'<p style="font-size:{size}px;font-weight:700;color:{NAVY};background:{PART[name][0]};'
            f'padding:{pad};border-radius:24px">{name}</p>')


def add(slide_id, html, section=None):
    if section:
        sections[section[0]] = {"description": section[1], "start": slide_id}
    order.append(slide_id)
    slides[slide_id] = html


def head(eyebrow, chips, title, dark, size=72):
    grey = "#C9D2E3" if dark else "#5A6478"
    return (f'<div style="display:flex;flex-direction:column;gap:16px">'
            f'<div style="display:flex;gap:16px;align-items:center">'
            f'<p style="font-size:24px;font-weight:700;color:{grey};letter-spacing:3px;text-transform:uppercase">{eyebrow}</p>'
            + "".join(chip(c) for c in chips) +
            f'</div><h2 style="{SERIF};font-size:{size}px;font-weight:700;line-height:1.1">{title}</h2></div>')


def section_open(slide_id, dark, layout="display:flex;flex-direction:column;justify-content:center;gap:48px"):
    bg, fg = (NAVY, "#F4F1EA") if dark else (CREAM, NAVY)
    return f'<section id="{slide_id}" data-transition="fade" style="background:{bg};color:{fg};{BASE};{layout}">'


def foot(text, dark):
    color = "#C9D2E3" if dark else "#3D4A63"
    return f'<p style="font-size:30px;line-height:1.45;color:{color}">{text}</p>' if text else ""


def divider(slide_id, number, years, title, sub, chips, notes, section):
    html = (section_open(slide_id, True, "display:flex;flex-direction:column;justify-content:center;gap:40px") +
            f'<p style="font-size:32px;font-weight:700;color:#C9D2E3;letter-spacing:4px;text-transform:uppercase">Chapter {number} · {years}</p>'
            f'<h2 style="{SERIF};font-size:96px;font-weight:700;line-height:1.1">{title}</h2>'
            f'<p style="font-size:40px;line-height:1.4;color:#C9D2E3">{sub}</p>'
            '<div style="display:flex;gap:16px">' + "".join(chip(c, 28) for c in chips) + '</div>'
            f'<aside>{notes}</aside></section>')
    add(slide_id, html, section)


def cards(slide_id, eyebrow, chips, title, items, footer, notes, dark=False, section=None):
    """items: (heading, body, part, example or None)."""
    cols = " ".join(["1fr"] * len(items))
    out = section_open(slide_id, dark) + head(eyebrow, chips, title, dark)
    out += f'<div style="display:grid;grid-template-columns:{cols};gap:40px">'
    for heading, body, part, example in items:
        light, deep = PART[part]
        if dark:
            out += (f'<div style="display:flex;flex-direction:column;gap:16px;border-top:8px solid {light};padding:32px 0 0 0">'
                    f'<h3 style="font-size:38px;font-weight:700;color:{light}">{heading}</h3>'
                    f'<p style="font-size:28px;line-height:1.45;color:#E6E9F0">{body}</p>')
            if example:
                out += f'<p style="font-size:24px;color:#C9D2E3">{example}</p>'
        else:
            out += (f'<div style="display:flex;flex-direction:column;gap:18px;background:{CARD};padding:44px;border:2px solid #D9D3C7;'
                    f'border-top:16px solid {light};border-radius:16px">'
                    f'<h3 style="font-size:38px;font-weight:700;color:{deep}">{heading}</h3>'
                    f'<p style="font-size:28px;line-height:1.45;color:#3D4A63">{body}</p>')
            if example:
                out += f'<p style="font-size:24px;color:#5A6478">{example}</p>'
        out += '</div>'
    out += '</div>' + foot(footer, dark) + f'<aside>{notes}</aside></section>'
    add(slide_id, out, section)


def code(slide_id, eyebrow, chips, title, text, code_label, code_text, footer, notes, dark=False):
    """Text on the left, a code panel on the right."""
    out = section_open(slide_id, dark, "display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center")
    grey = "#C9D2E3" if dark else "#3D4A63"
    out += f'<div style="display:flex;flex-direction:column;gap:32px">{head(eyebrow, chips, title, dark)}'
    out += "".join(f'<p style="font-size:30px;line-height:1.45;color:{grey}">{t}</p>' for t in text)
    out += '</div><div style="display:flex;flex-direction:column;gap:16px">'
    out += (f'<div style="background:#0F1A30;border-radius:16px;padding:32px;display:flex;flex-direction:column;gap:12px">'
            f'<p style="font-size:22px;font-weight:700;color:#C9D2E3">{code_label}</p>'
            f'<p style="{MONO};font-size:25px;line-height:1.6;color:#F4F1EA">{code_text}</p></div>')
    if footer:
        out += f'<p style="font-size:26px;line-height:1.45;color:{grey}">{footer}</p>'
    out += f'</div><aside>{notes}</aside></section>'
    add(slide_id, out)


def dated(slide_id, eyebrow, chips, title, left, items, notes, dark=False):
    """A short explanation on the left and a column of dated events on the right."""
    out = section_open(slide_id, dark) + head(eyebrow, chips, title, dark)
    grey = "#C9D2E3" if dark else "#3D4A63"
    out += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:start">'
    out += '<div style="display:flex;flex-direction:column;gap:24px">' + "".join(
        f'<p style="font-size:30px;line-height:1.45;color:{grey}">{t}</p>' for t in left) + '</div>'
    out += '<div style="display:flex;flex-direction:column;gap:24px">'
    for when, what, part in items:
        light, deep = PART[part]
        colour = light if dark else deep
        out += (f'<div style="display:flex;flex-direction:column;gap:6px;border-left:8px solid {light};padding:0 0 0 24px">'
                f'<p style="font-size:30px;font-weight:700;color:{colour}">{when}</p>'
                f'<p style="font-size:26px;line-height:1.4;color:{grey}">{what}</p></div>')
    out += f'</div></div><aside>{notes}</aside></section>'
    add(slide_id, out)


# ---------------------------------------------------------------- introduction
add("cover", section_open("cover", True, "display:flex;flex-direction:column;justify-content:center;gap:40px") +
    '<p style="font-size:32px;font-weight:700;color:#C9D2E3;letter-spacing:4px;text-transform:uppercase">A history of the web, from the other side</p>'
    f'<h1 style="{SERIF};font-size:120px;font-weight:700;line-height:1.05">Behind the Page</h1>'
    '<p style="font-size:44px;line-height:1.4;color:#C9D2E3;max-width:1400px">How servers learned to answer and databases learned to remember, from punched cards to vector search.</p>'
    '<div style="display:flex;gap:16px">' + chip("Server", 28) + chip("Database", 28) + '</div>'
    '<aside>Most histories of the web watch from the browser. This one walks round to the back of the page and watches the computers that answer. Every chapter adds one stop on the road a click travels: the request, the route, the SQL and the rows that come back.</aside></section>',
    ("s1", "The five colours and the plan for the talk"))

add("five-parts", section_open("five-parts", False) + head("The colour key", [], "One green box, opened up", False) +
    '<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr 1fr;gap:28px">' +
    "".join(
        f'<div style="display:flex;flex-direction:column;gap:16px;background:{CARD};padding:32px;border:2px solid #D9D3C7;border-top:16px solid {PART[p][0]};border-radius:16px">'
        f'<x-icon name="{icon}" style="color:{PART[p][1]};width:56px;height:56px"></x-icon>'
        f'<h3 style="font-size:36px;font-weight:700;color:{PART[p][1]}">{p}</h3>'
        f'<p style="font-size:24px;line-height:1.4;color:#3D4A63">{text}</p></div>'
        for p, icon, text in [
            ("HTML", "Book", "The structure of the page the server sends back."),
            ("CSS", "Star", "The look of that page. The server only delivers it."),
            ("Scripts", "Code", "Code in the browser that sends requests and shows replies."),
            ("Server", "Settings", "A program that listens for requests and decides what to send."),
            ("Database", "Database", "The place that remembers data after every request has ended."),
        ]) +
    '</div><p style="font-size:30px;line-height:1.45;color:#3D4A63">Seen from the browser, everything behind the page looks like one green box called the server. This talk opens the box: the program that answers stays green, and the database that remembers is purple.</p>'
    '<aside>Every slide carries a tag in these colours, with its name written on it, so nobody has to rely on colour alone. Most of this deck lives in green and purple, and the front-end colours appear only where the browser meets the server.</aside></section>')

PLAN = [
    ("1", "1966 to 1986", "Data learns to sit in tables", ["Database"]),
    ("2", "1990 to 1995", "The first servers hand out files", ["Server", "HTML"]),
    ("3", "1995 to 2004", "Pages built from a database", ["Server", "Database"]),
    ("4", "2003 to 2010", "Frameworks, caches and NoSQL", ["Server", "Database"]),
    ("5", "2006 to 2019", "Someone else’s computer", ["Server"]),
    ("6", "2020 to now", "Data for AI", ["Database", "Server"]),
    ("7", "Today", "Putting it together", ["Scripts", "Server", "Database"]),
]
add("timeline", section_open("timeline", True, "display:flex;flex-direction:column;gap:48px;padding:112px 128px") +
    '<div style="display:flex;flex-direction:column;gap:16px"><p style="font-size:24px;font-weight:700;color:#C9D2E3;letter-spacing:3px;text-transform:uppercase">The plan</p>'
    f'<h2 style="{SERIF};font-size:72px;font-weight:700;line-height:1.1">Seven chapters, from 1966 to now</h2></div>'
    '<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:40px">' +
    "".join(
        f'<div style="display:flex;flex-direction:column;gap:10px;border-top:6px solid #C9D2E3;padding:16px 0 0 0">'
        f'<div style="display:flex;gap:20px;align-items:baseline"><p style="{SERIF};font-size:48px;font-weight:700;color:#C9D2E3">{n}</p>'
        f'<p style="font-size:22px;font-weight:700;color:#C9D2E3">{years}</p></div>'
        f'<h3 style="font-size:30px;font-weight:700;line-height:1.2">{title}</h3>'
        '<div style="display:flex;flex-wrap:wrap;gap:10px">' + "".join(chip(c, 22) for c in chips) + '</div></div>'
        for n, years, title, chips in PLAN) +
    '</div><aside>The story starts before the web, because databases are older than web pages. Chapter 1 explains the tables and SQL that every later chapter relies on. Chapter 6 is about AI and has no settled ending, so it finishes with questions.</aside></section>')

# ---------------------------------------------------------------- chapter 1
divider("ch1", 1, "1966 to 1986", "Data learns to sit in tables",
        "Before the web, banks and airlines already needed computers that remembered things. The answer they settled on was the table.",
        ["Database"], "This chapter is older than the web by twenty years, and it explains the ideas that almost every web database still uses: tables, rows, keys and SQL.",
        ("s2", "Chapter 1, 1966 to 1986: data learns to sit in tables"))

cards("hierarchy", "1966 to 1970", ["Database"], "First, data lived in trees",
      [("A tree of records", "IBM’s IMS, built for the Apollo programme in the late 1960s, stored data as a tree. A customer record held its orders, and each order held its items.", "Database", None),
       ("Follow the path", "To find something, a program walked down the tree one level at a time. A new kind of question often meant writing a new program.", "Database", "Customer → Order 17 → Item 3")],
      "The data was fast to read along the paths the designers planned, and slow or impossible to read along any other path.",
      "IMS is still in use in some banks. The point for students: the shape of the storage decided which questions you could ask. The next slide shows the idea that broke that link.")

code("codd", "1970", ["Database"], "Codd: put everything in tables",
     ["In 1970 Edgar F. Codd, a mathematician at IBM, published “A Relational Model of Data for Large Shared Data Banks”.",
      "Every fact goes in a table of rows and columns. A key links one table to another. You say <b>what</b> you want, and the database works out <b>how</b> to find it."],
     "products and sales",
     "products<br>id &nbsp;name &nbsp;&nbsp;&nbsp;price<br>1 &nbsp;&nbsp;Crisps &nbsp;1.20<br>2 &nbsp;&nbsp;Water &nbsp;&nbsp;0.90<br><br>sales<br>id &nbsp;product_id &nbsp;sold_at<br>1 &nbsp;&nbsp;2 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;09:14",
     "The number 2 in sales points at Water in products. That pointer is a foreign key.",
     "Codd’s paper appeared in Communications of the ACM in June 1970. IBM was slow to build it because IMS made money, so other companies got there first. The two small tables on the slide are the pattern for a shop: one table of things for sale and one of sales.", dark=True)

dated("sql", "1974 to 1986", ["Database"], "SQL: one language for asking",
      ["Researchers at IBM wrote a language for Codd’s tables, first called SEQUEL and later SQL. A question in SQL reads almost like English.",
       '<span style="font-family:\'JetBrains Mono\', monospace;font-size:28px">SELECT name, price FROM products WHERE price &lt; 1;</span>'],
      [("1974", "SEQUEL is described at IBM, as part of a research system called System R.", "Database"),
       ("1979", "The company that became Oracle sells the first commercial SQL database.", "Database"),
       ("1986", "SQL becomes an official standard, so the same language works across products.", "Database")],
      "SQL is now over fifty years old, and anyone who builds a site with a database will write it. The standard is why SQL learned in SQLite mostly works in MySQL and PostgreSQL too, with small differences.")

# ---------------------------------------------------------------- chapter 2
divider("ch2", 2, "1990 to 1995", "The first servers hand out files",
        "A web server begins as a simple program: it waits for a request, finds a file and sends it back.",
        ["Server", "HTML"], "The browser asks for a page, and a program on another computer answers. This chapter is about that program.",
        ("s3", "Chapter 2, 1990 to 1995: the first servers hand out files"))

code("httpd", "1990", ["Server"], "A server is a program that listens",
     ["Tim Berners-Lee wrote the first web server at CERN in 1990. It listened on a network port, read each request, found the matching file on its disk and sent it back.",
      "If the file was missing, it answered with a status code. 404 still means “not found”."],
     "a request and its answer",
     "GET /hypertext/WWW/TheProject.html HTTP/1.0<br><br>HTTP/1.0 200 OK<br>Content-Type: text/html<br><br>&lt;h1&gt;World Wide Web&lt;/h1&gt;…",
     "Every request since works this way: a method, a path, then a status and a body.",
     "The CERN server was called CERN httpd; the d stands for daemon, a program that runs in the background. The browser’s developer tools show these messages for any site: open the Network tab and reload.", dark=True)

cards("cgi", "1993", ["Server", "HTML"], "CGI: the server runs a program",
      [("The idea", "The Common Gateway Interface, from NCSA in 1993, let a server run a program and send back whatever that program printed, instead of a stored file.", "Server", None),
       ("What it made possible", "A form could now send data to a script on the server, often written in Perl. The script could search, count or save, then print a fresh HTML page.", "HTML", "Example: the 1990s guestbook and hit counter")],
      "For the first time the page did not exist until somebody asked for it. That is a dynamic page.",
      "CGI started a new program for every request, which was slow when many people visited. Later server languages kept one program running to avoid that cost. The folder name cgi-bin survives on old servers today.")

dated("apache", "1995", ["Server"], "Apache, and the server log",
      ["In 1995 a group of webmasters collected their fixes, or patches, to the NCSA server and released them as Apache. It became the most used web server for many years.",
       "Like most servers, Apache writes one line to a log for every request. The log is how you find out who asked for what, and what went wrong."],
      [("A line of a log", '<span style="font-family:\'JetBrains Mono\', monospace;font-size:22px">203.0.113.7 - - [17/Nov/2026:09:14:02] "GET /index.html HTTP/1.1" 200 5120</span>', "Server"),
       ("Read it as", "Who asked, when, which method and path, the status code, and the size of the answer in bytes.", "Server")],
      "The name is often explained as “a patchy server”, which the Apache project itself has said is a story added afterwards. Reading logs is a real job skill, and the first place to look when something breaks.", dark=True)

# ---------------------------------------------------------------- chapter 3
divider("ch3", 3, "1995 to 2004", "Pages built from a database",
        "Cheap hosting and free software put a database behind ordinary websites. The server now remembers.",
        ["Server", "Database"], "Many sites still follow the pattern in this chapter: a server language, a SQL database and HTML built on each request.",
        ("s4", "Chapter 3, 1995 to 2004: pages built from a database"))

cards("lamp", "1995 to 1998", ["Server", "Database"], "LAMP: a free stack for everyone",
      [("Linux", "A free operating system for the server.", "Server", None),
       ("Apache", "The web server that receives each request.", "Server", None),
       ("MySQL", "A free SQL database, first released in 1995.", "Database", None),
       ("PHP", "A language mixed into HTML, also from 1995.", "Server", None)],
      "A German magazine named the four together LAMP in 1998. Shared hosting with LAMP cost a few euro a month, so blogs, forums and shops could all keep their data in a database.",
      "WordPress, which runs a large share of the web, is still a LAMP application. PostgreSQL, the other big free database, took its name in 1996. Perl and Python also filled the P in some versions.")

cards("sessions", "1994 onwards", ["Server", "Database"], "How the server remembers you",
      [("Cookies", "From 1994, a server could hand the browser a small cookie, and the browser sent it back with every later request.", "Server", "Set-Cookie: session=8f3a…"),
       ("Sessions", "The cookie holds only an id. The server keeps the real details, such as who you are and what is in your basket, in its own memory or database.", "Database", "8f3a… → user 42, basket [2, 7]")],
      "HTTP forgets each request as soon as it ends. Cookies and sessions are how a login or a shopping basket survives from one page to the next.",
      "This is the link to security later: if someone steals the session id, they become you. That is why session cookies should be marked HttpOnly and sent only over HTTPS.", dark=True)

code("injection", "1998", ["Server", "Database"], "SQL injection: when input becomes code",
     ["In 1998 a security researcher called rain.forest.puppy described how text typed into a form could change the SQL a server ran. The attack is called SQL injection.",
      "The cause is building a query by gluing strings together. The cure is a <b>parameterised query</b>: the SQL and the data travel separately."],
     "the mistake, and the fix",
     "# glued together: unsafe<br>sql = \"SELECT * FROM users WHERE name = '\" + name + \"'\"<br><br># typed into the form:<br>' OR '1'='1<br><br># parameterised: safe<br>db.execute(\"SELECT * FROM users WHERE name = ?\", [name])",
     "Over twenty-five years later, injection is still on OWASP’s list of the most common risks.",
     "Walk through the example slowly. The typed text closes the quote early, then adds a condition that is always true, so the query returns every user. With a parameter, the same text is only a strange name that matches nobody.")

dated("rest-json", "2000 to 2002", ["Server", "Scripts"], "Servers start answering with data",
      ["In 2000 Roy Fielding described REST in his PhD thesis: a way to design a server around resources, each with its own address, read and changed with the HTTP methods.",
       "Soon after, JSON gave servers a light way to send data instead of whole pages. A script in the browser then decides how to show it."],
      [("GET /api/products/2", "Read one product.", "Server"),
       ("POST /api/sales", "Record a new sale.", "Server"),
       ("{ \"id\": 2, \"name\": \"Water\", \"price\": 0.9 }", "The answer, as JSON.", "Scripts")],
      "Most web APIs today follow this design. On the browser side, a script sends the request and turns the JSON into part of the page.", dark=True)

# ---------------------------------------------------------------- chapter 4
divider("ch4", 4, "2003 to 2010", "Frameworks, caches and NoSQL",
        "Sites with millions of users push servers and databases to their limits, and new tools appear to cope.",
        ["Server", "Database"], "Three ideas in this chapter: frameworks that write the repetitive code, caches that remember answers, and databases that give up some of SQL's rules to grow bigger.",
        ("s5", "Chapter 4, 2003 to 2010: frameworks, caches and NoSQL"))

code("frameworks", "2004 and 2005", ["Server", "Database"], "Frameworks and the ORM",
     ["Ruby on Rails in 2004 and Django, in Python, in 2005 gave every new project the same folders, routes and database setup.",
      "An <b>ORM</b>, an object-relational mapper, lets the program treat rows as objects. The framework writes the SQL."],
     "the same question, twice",
     "# with an ORM (Django)<br>Product.objects.filter(price__lt=1)<br><br># the SQL it writes for you<br>SELECT * FROM products<br>WHERE price &lt; 1;",
     "An ORM saves typing and guards against injection. It also hides the SQL, so slow queries can go unnoticed.",
     "Migrations also came with these frameworks: small files that change the database’s tables step by step, so every copy of the project has the same structure. Laravel later brought the same ideas to PHP.", dark=True)

cards("cache", "2003", ["Server", "Database"], "Caching: remember the answer",
      [("The problem", "A popular page asked the database the same question thousands of times a minute.", "Database", None),
       ("The fix", "memcached, written in 2003 for the LiveJournal blog site, kept recent answers in memory. The server checks the cache first and asks the database only when the cache has nothing.", "Server", "cache hit: fast · cache miss: ask the database")],
      "A cache trades freshness for speed. The hard part is knowing when a remembered answer has gone out of date.",
      "There is an old joke that the two hardest problems in computing are naming things and cache invalidation. Browsers cache too, which is why a hard refresh sometimes fixes a page.")

dated("nosql", "2006 to 2009", ["Database"], "NoSQL: bigger, with fewer rules",
      ["Google and Amazon described databases that spread data over thousands of machines: Bigtable in 2006 and Dynamo in 2007. To grow that big, they gave up some of what SQL databases promise, such as joins between tables.",
       "In 2009 a meetup in San Francisco gave the movement a name: NoSQL, later read as “not only SQL”."],
      [("MongoDB, 2009", "Stores documents shaped like JSON, so one record can hold nested data.", "Database"),
       ("Redis, 2009", "Keeps keys and values in memory, very fast. Often used as a cache.", "Database"),
       ("Still SQL, today", "Most new projects still choose a SQL database, and many SQL databases now store JSON too.", "Database")],
      "Keep this balanced. NoSQL suits some jobs, such as huge volumes of simple records, and suits others badly, such as money, where every sale must add up. Ask which kind a small shop needs, and why.", dark=True)

cards("node-server", "2009", ["Server", "Scripts"], "JavaScript on the server",
      [("One thread, many visitors", "Node.js, from 2009, handles thousands of open connections in one program, by never waiting idle for the disk or the database.", "Server", None),
       ("One language at both ends", "The same JavaScript, or TypeScript, can now run in the browser and on the server.", "Scripts", "Example: a TypeScript server and TypeScript in the page")],
      "The point here is the server: Node changed how one program can wait for many things at once.",
      "Python, PHP and Ruby servers can do the same with the right tools. Node made this way of waiting the default.")

# ---------------------------------------------------------------- chapter 5
divider("ch5", 5, "2006 to 2019", "Someone else’s computer",
        "Servers move out of the back room and into rented data centres. You pay for what you use.",
        ["Server", "Database"], "The phrase “the cloud is just someone else’s computer” is a joke, and it is also accurate. This chapter explains what is rented and why.",
        ("s6", "Chapter 5, 2006 to 2019: someone else's computer"))

dated("cloud", "2006", ["Server", "Database"], "Renting servers by the hour",
      ["Before 2006 a company that wanted a server bought one, installed it and kept it running. A busy day meant buying more, and a quiet month left them idle.",
       "Amazon began renting storage and computers over the internet. A new server took minutes instead of weeks."],
      [("March 2006", "Amazon S3 stores files for anyone, priced per gigabyte.", "Database"),
       ("August 2006", "Amazon EC2 rents whole virtual servers, priced by the hour.", "Server"),
       ("Later", "Google, Microsoft and others offer the same. Managed databases arrive, where the provider runs the database for you.", "Database")],
      "This is when the server stopped being a box that a business owned. A site on GitHub Pages or a free hosted database is a descendant.")

cards("containers", "2013 and 2014", ["Server"], "Containers: it works on my machine, and on yours",
      [("Docker, 2013", "A container packs a program together with everything it needs to run. The same container runs the same way on a laptop and in a data centre.", "Server", "FROM python:3.12 · COPY . /app · CMD python server.py"),
       ("Kubernetes, 2014", "Google released a system for running many containers across many machines, restarting any that fail and adding more when traffic grows.", "Server", None)],
      "Containers ended a long-running excuse: “it works on my machine”.",
      "The three-line example is a simplified Dockerfile. Anyone who works with servers will meet Docker sooner or later.", dark=True)

cards("serverless", "2014 onwards", ["Server", "Database"], "Serverless: just the function",
      [("Functions on demand", "AWS Lambda, announced in November 2014, runs one function each time a request arrives. Nobody keeps a server running between requests.", "Server", None),
       ("Managed data", "Hosted databases and services such as Firebase let a small team store data without running a database server themselves.", "Database", None)],
      "There are still servers, of course. “Serverless” means that somebody else looks after them.",
      "Serverless is cheap for quiet sites and can be expensive for busy ones. It also brings back the CGI pattern from chapter 2 in a new form: start, answer one request, stop.")

cards("data-rules", "2017 and 2018", ["Database", "Server"], "Data comes with rules",
      [("Breaches", "In 2017 attackers took the personal data of about 147 million people from Equifax, through a server that had missed a security update.", "Server", None),
       ("GDPR, 2018", "The EU’s data protection law began to apply on 25 May 2018. A site must collect only the data it needs, protect it and delete it on request.", "Database", None)],
      "A database is now a responsibility as well as a tool. Every column you add is data you must protect.",
      "The Equifax breach exploited a flaw in Apache Struts, a Java framework, that had a fix available two months earlier. Updates matter. A question to ask: does a small online shop need each buyer’s date of birth?", dark=True)

# ---------------------------------------------------------------- chapter 6
divider("ch6", 6, "2020 to now", "Data for AI",
        "AI systems need data to learn from and data to look things up in. Databases learn to search by meaning.",
        ["Database", "Server"], "This chapter has no settled ending. Present the ideas and dates, then let the class discuss.",
        ("s7", "Chapter 6, 2020 to now: data for AI"))

code("embeddings", "2013 onwards", ["Database"], "Meaning as a list of numbers",
     ["An <b>embedding</b> turns a piece of text into a long list of numbers, called a vector. Texts with similar meanings get similar vectors.",
      "A database can then find the rows closest in meaning to a question, even when they share no words with it."],
     "a vector search, in SQL",
     "-- pgvector, an add-on for PostgreSQL<br>SELECT title FROM notes<br>ORDER BY embedding &lt;-&gt; :question<br>LIMIT 3;",
     "The &lt;-&gt; operator measures the distance between two vectors. Smaller means closer in meaning.",
     "Real embeddings have hundreds or thousands of numbers. A version with only two numbers can be drawn on a flat map, which is a good way to explain the idea. pgvector first appeared in 2021, and SQLite and MySQL now have similar features.", dark=True)

dated("rag", "2020 to 2023", ["Database", "Server"], "Look it up, then answer",
      ["A language model only knows what was in its training data. To answer questions about your own documents, it needs to look them up first.",
       "This pattern is called <b>retrieval-augmented generation</b>, or RAG: a server finds the closest rows in a vector database, then hands them to the model along with the question."],
      [("2020", "Researchers at Facebook AI name and describe retrieval-augmented generation.", "Database"),
       ("2021", "pgvector adds vector search to PostgreSQL.", "Database"),
       ("2023", "Vector databases become a product category of their own, as chat assistants spread.", "Server")],
      "RAG is a three-tier application in disguise: a front end asks, a server program decides, a database remembers. Only the kind of search is new.")

cards("bots", "2023 onwards", ["Server"], "The servers’ new visitors",
      [("Crawlers", "AI companies send crawlers to read the web for training data. Many sites saw their server logs fill with bots and their hosting bills rise.", "Server", "User-agent: GPTBot"),
       ("The defences", "robots.txt asks crawlers to stay away. Rate limits slow down any visitor that asks too fast. Some hosts now block AI crawlers by default.", "Server", None)],
      "The log file from chapter 2 is where a site owner first notices this.",
      "The angle here is cost: every request uses the server’s time and someone pays for it. A rate limit answers with status 429, Too Many Requests.", dark=True)

cards("discuss-ai", "Discuss", ["Database"], "Questions without settled answers",
      [("Whose data?", "If your writing helped train a model, should you have been asked? Should you be paid?", "Database", None),
       ("Forgetting", "GDPR gives you a right to have your data deleted. How would anyone delete it from a trained model?", "Database", None),
       ("Trust", "When an assistant answers from your own documents, how would you check that it read them correctly?", "Server", None)],
      "Reasonable people disagree on all three. Give each side a fair hearing.",
      "These questions are being argued in courts and parliaments now. Keep the discussion open and make sure students hear the strongest case on each side.")

# ---------------------------------------------------------------- chapter 7
divider("ch7", 7, "Today", "Putting it together",
        "One click, followed all the way to a database row and back, and the habits that keep it safe.",
        ["Scripts", "Server", "Database"], "The last chapter puts the history together, then turns it into habits for any site with a server and a database.",
        ("s8", "Chapter 7, today: putting it together"))

add("journey", section_open("journey", False) + head("Today", ["Scripts", "Server", "Database"], "The journey of one click", False) +
    '<div style="display:grid;grid-template-columns:1fr auto 1fr auto 1fr;gap:20px;align-items:stretch">' +
    "".join(
        (f'<div style="display:flex;flex-direction:column;gap:14px;background:{CARD};padding:36px;border:2px solid #D9D3C7;border-top:16px solid {PART[p][0]};border-radius:16px">'
         f'<x-icon name="{icon}" style="color:{PART[p][1]};width:52px;height:52px"></x-icon>'
         f'<h3 style="font-size:34px;font-weight:700;color:{PART[p][1]}">{h}</h3>'
         f'<p style="font-size:25px;line-height:1.4;color:#3D4A63">{t}</p>'
         f'<p style="{MONO};font-size:20px;color:#5A6478">{c}</p></div>')
        + (f'<p style="{SERIF};font-size:56px;font-weight:700;color:#5A6478;align-self:center">→</p>' if k < 2 else "")
        for k, (p, icon, h, t, c) in enumerate([
            ("Scripts", "Code", "Browser", "A click runs a script, which sends a request.", "POST /api/buy {id: 2}"),
            ("Server", "Settings", "Server program", "A route checks the request and decides what to do.", "if stock &gt; 0: sell"),
            ("Database", "Database", "Database", "A parameterised UPDATE changes one row.", "UPDATE products SET stock = stock - 1 WHERE id = ?"),
        ])) +
    '</div><p style="font-size:30px;line-height:1.45;color:#3D4A63">Then the same road in reverse: the row count comes back, the server answers with JSON and a status code, and the script updates the page. Every chapter of this history is one part of that road.</p>'
    '<aside>This slide is the whole talk in one picture. Ask the class to name the chapter each step came from: the request from chapter 2, the route from chapter 3, the SQL from chapter 1, the JSON from chapter 3, the framework habits from chapter 4.</aside></section>')

cards("keep-safe", "Today", ["Server", "Database"], "Five habits that keep a server safe",
      [("Parameters", "Never glue input into SQL. Send it as a parameter.", "Database", None),
       ("Hashes", "Store a slow hash of each password, never the password.", "Database", None),
       ("Check again", "Check every request on the server, even if the page checked it first.", "Server", None),
       ("HTTPS", "Encrypt every request, so no one can read or change it on the way.", "Server", None),
       ("Updates", "Install security updates promptly. Equifax waited two months.", "Server", None)],
      "None of these is new. Each one answers a mistake from earlier in this history.",
      "Each habit maps to a chapter: parameters to 1998, hashes and breaches to 2017, checking on the server to the CGI forms of 1993, HTTPS to the free certificates of 2015, updates to Equifax. The OWASP Top 10 is the list to show next.", dark=True)

cards("still-sql", "Today", ["Database"], "SQL is still here",
      [("SQLite", "A whole SQL database in one file, first released in 2000. It is in every phone and every web browser, and probably the most used database in the world.", "Database", None),
       ("PostgreSQL and MySQL", "The free databases of chapter 3 still run a large share of the web, now with JSON and vector features added.", "Database", None)],
      "Fifty years after Codd, the table and the SELECT statement are still the place to start.",
      "SQLite needs no database server at all, which makes it a good first database. It can even run inside a web page, compiled to WebAssembly.")

add("recap", section_open("recap", True, "display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center") +
    '<div style="display:flex;flex-direction:column;gap:32px"><p style="font-size:24px;font-weight:700;color:#C9D2E3;letter-spacing:3px;text-transform:uppercase">To take away</p>'
    f'<h2 style="{SERIF};font-size:72px;font-weight:700;line-height:1.1">Questions to talk over</h2>'
    '<p style="font-size:30px;line-height:1.45;color:#C9D2E3">Each question has more than one good answer. Pick one, and back it up with an example from the talk.</p></div>'
    '<ol style="font-size:30px;line-height:1.5;padding:0 0 0 40px;display:flex;flex-direction:column;gap:12px">'
    '<li>Pick a site you use. What do you think lives on its server, and what in its database?</li>'
    '<li>What could happen if a visitor typed SQL into a site’s search box?</li>'
    '<li>When would you choose a document database over SQL tables?</li>'
    '<li>What data does a site you use collect that it does not need?</li>'
    '<li>Find a status code in your browser’s network tab. What does it mean?</li></ol>'
    '<aside>The last question needs the browser developer tools: open the Network tab, reload a page and read the status column.</aside></section>')


def main():
    (OUT / "slides").mkdir(parents=True, exist_ok=True)
    for old in (OUT / "slides").glob("*.html"):
        old.unlink()
    for slide_id, html in slides.items():
        (OUT / "slides" / f"{slide_id}.html").write_text(html + "\n")
    deck = {
        "v": 5, "createdOnFiles": {"v": 1, "at": "2026-11-17T09:30:00Z"}, "lists": "css", "format": {"v": 1, "shared": ["project/deck.css"]},
        "title": "Behind the Page", "order": order, "sections": sections,
        "faces": {
            "libre-baskerville": {"family": "Libre Baskerville", "href": "https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&display=swap"},
            "public-sans": {"family": "Public Sans", "href": "https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;600;700&display=swap"},
            "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap"},
        },
    }
    (OUT / "deck.css").write_text("body { font-family: 'Public Sans', Arial, sans-serif; color: #1B2A4A; }\n")
    (OUT / "deck.json").write_text(json.dumps(deck, ensure_ascii=False))
    print(len(order), "slides")


if __name__ == "__main__":
    main()
