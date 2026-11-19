"""Long-form on-page SEO content for every tool page: intro copy, deep-dive
sections, FAQs (also rendered as FAQPage JSON-LD), and curated related-tool
internal links. Kept separate from registry.py (which only holds nav/menu
metadata) so this can grow large without cluttering the routing code.

Keyed by (category_slug, tool_slug) to match registry.py's TOOL_CATEGORIES.

House style for this copy: plain language, no em dashes, no filler openers,
and every tool explains where to get the data it asks the visitor to paste in.
"""


def _rel(endpoint, name, blurb):
    return {"endpoint": endpoint, "name": name, "blurb": blurb}


SEO_CONTENT = {

    ('outreach', 'email-finder'): {
        "intro_html": """
<p>Finding the right person to email is usually the slowest part of any outreach campaign. Most sites
do not publish an obvious address. The real contact sits behind a "Contact", "About" or "Write for Us"
link, and the address itself is often written as plain text, hidden behind a form, or lightly disguised
as something like <code>name at domain dot com</code> to put off spam bots.</p>
<p>This tool visits each domain you give it, follows the links that look like contact or contributor
pages, and pulls out the email addresses it finds. You get a list you can start writing to instead of
half an hour of clicking through navigation menus.</p>
<p>It is built for outreach and guest posting, not bulk harvesting. Rather than guessing address
patterns across a whole domain the way many paid tools do, it only reads pages the site owner has
already signposted as the place to get in touch. The addresses you get back are ones somebody checks.</p>
""",
        "sections": [
            {
                "heading": 'How it finds addresses',
                "html": """
<p>For each domain, the tool loads the homepage and looks at every link for outreach words such as
"contact", "write for us", "guest post", "contributor guidelines" and "about". If nothing matches, it
falls back to the XML sitemap and searches that for the same words, because plenty of sites bury their
contact page well below the main navigation.</p>
<p>Every page it finds is then scanned two ways: for normal <code>name@domain.com</code> addresses, and
for disguised versions like <code>name at domain dot com</code> that some sites use to avoid scrapers.</p>
""",
            },
            {
                "heading": 'Where to get your list of domains',
                "html": """
<ul>
<li><strong>From a search.</strong> Search for the kind of site you want, such as "write for us" plus
your topic, and copy the domains from the results.</li>
<li><strong>From your competitors' backlinks.</strong> If you have access to a backlink tool, export the
list of sites linking to a competitor. Those sites already publish content in your area.</li>
<li><strong>From a broken link hunt.</strong> Use the Broken-Link Outreach Finder on this site first. It
gives you resource pages with dead links, which is a stronger reason to make contact.</li>
<li><strong>From a spreadsheet you already keep.</strong> Copy the domain column and paste it straight
in. One domain per line is all the tool needs, with or without the https prefix.</li>
</ul>
<p>Start with twenty or thirty domains rather than several hundred. You will learn quickly whether your
list is well matched, and a smaller batch finishes faster.</p>
""",
            },
            {
                "heading": 'Getting replies',
                "html": """
<ul>
<li><strong>Personalise past the first line.</strong> Mentioning something specific from the page you
are writing about works far better than a template with the site name dropped in.</li>
<li><strong>Match the channel you found.</strong> If the only address came from a "write for us" page,
pitch a contribution. Sending a sales email to that address gets you deleted.</li>
<li><strong>Send fewer, better emails.</strong> A short list of well matched sites beats a mass send,
and it keeps your sending domain out of spam filters.</li>
<li><strong>Follow the law.</strong> Contacting a published business address is normal practice, but you
still have to honour unsubscribe requests and comply with CAN-SPAM, GDPR or your local equivalent.</li>
</ul>
""",
            },
        ],
        "faqs": [
            {"q": 'Does this guess email addresses?',
             "a": 'No. It only reports addresses actually published on the pages it visits. It never guesses patterns like first.last@domain.com, which is what produces the high bounce rates people associate with cheap email finders.'},
            {"q": 'Why did it find nothing for some domains?',
             "a": 'Usually because the site only offers a contact form, which has no address to extract. It can also happen if the contact page is not linked from the homepage and the site has no sitemap, or if the address is displayed as an image.'},
            {"q": 'How many domains can I check at once?',
             "a": 'Paste as many as you like. Larger batches take longer because each domain needs several page loads, so start small if you want a quick answer.'},
            {"q": 'Is scraping contact pages legal?',
             "a": 'Reading a published business contact page is normal practice. What matters is what you do next: honour unsubscribe requests, do not send bulk unsolicited mail, and follow the marketing law that applies where your recipients live.'},
        ],
        "related": [
            _rel('audit.broken_links', 'Broken Link Checker', 'Find dead links on resource pages as outreach opportunities.'),
            _rel('classic_seo.domain_age', 'Domain Age Checker', "Vet a prospect's domain before you pitch it."),
            _rel('linkgraph.site_audit', 'Site Crawler & Semantic Audit', 'Crawl a whole site to find more contact and contributor pages at once.'),
            _rel('converters.csv_json', 'CSV ⇄ JSON Converter', 'Reshape your exported prospect list for a CRM or script.'),
            _rel('utilities.line_tools', 'Duplicate Remover and Sorter', 'Deduplicate your domain list before scanning.'),
        ],
    },

    ('outreach', 'broken-link-finder'): {
        "intro_html": """
<p>Broken link building works because you are doing someone a favour before you ask for anything. You
find a page with a dead outbound link, tell the owner, and suggest your own page as the replacement.
The pitch writes itself, and it is far easier to answer than a cold request for a link.</p>
<p>The slow part is finding the dead links. This tool takes a list of pages, follows every outbound link
on each one, and reports the ones that fail, along with the anchor text that pointed at them.</p>
""",
        "sections": [
            {
                "heading": 'What counts as broken',
                "html": """
<p>The tool reports links returning 404 and 410, which mean the page is gone, along with 5xx server
errors and links whose domain no longer resolves at all. A dead domain is the strongest opportunity of
the lot, because nothing is coming back and the owner almost certainly has not noticed.</p>
<p>Redirects are not treated as broken. A link that redirects still works for a visitor, even if it is
untidy.</p>
""",
            },
            {
                "heading": 'Where to get pages worth checking',
                "html": """
<ul>
<li><strong>Search for resource pages in your field.</strong> Try your topic plus words like "resources",
"useful links" or "further reading". These pages collect outbound links and go stale quickly.</li>
<li><strong>Look at old roundups.</strong> A list post from several years ago will usually have several
dead links in it by now.</li>
<li><strong>Check pages that already link to competitors.</strong> If you have a backlink tool, export
the pages linking to a competitor and run those. A page willing to link out once will do it again.</li>
<li><strong>Use university and association pages.</strong> They keep long link lists and rarely audit
them.</li>
</ul>
<p>Paste one URL per line. These should be the pages containing the links, not the sites you want a
link from.</p>
""",
            },
            {
                "heading": 'Writing the pitch',
                "html": """
<p>Name the specific dead link and the anchor text it used. That single detail proves you actually
looked at the page instead of sending a template, and it is the difference between a reply and silence.</p>
<p>Suggest your page as a replacement once, plainly, and leave it there. Pushing harder rarely helps and
often ends the conversation.</p>
<p>Expect a modest reply rate even when you do everything right. Broken link building is a numbers game
played politely.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Why are some links reported broken when they load fine for me?',
             "a": 'Some sites block automated requests, so they return an error to the tool and a normal page to your browser. Always open a link yourself before mentioning it in an email.'},
            {"q": 'Does it check links between pages of the same site?',
             "a": 'It focuses on outbound links, since those are the ones that create an outreach opportunity. To find broken internal links, use the Broken Link Checker instead.'},
            {"q": 'How many pages should I check at once?',
             "a": 'Every page needs its outbound links tested one by one, so a large batch takes a while. Twenty to fifty pages is a comfortable run.'},
        ],
        "related": [
            _rel('outreach.email_finder', 'Email & Contact Finder', "Find the right contact once you've spotted a broken-link opportunity."),
            _rel('outreach.pitch_personalizer', 'Guest Post Pitch Personalizer', 'Turn your broken-link findings into personalized outreach at scale.'),
            _rel('audit.broken_links', 'Broken Link Checker', 'The single-page version of this check, for auditing your own site.'),
            _rel('outreach.social_profile_finder', 'Social Profile Finder', 'Round out your outreach contact record beyond email.'),
        ],
    },

    ('outreach', 'social-profile-finder'): {
        "intro_html": """
<p>Email is not always the best way to reach someone. Plenty of site owners ignore their inbox but
answer on LinkedIn or X within the hour. This tool checks a list of domains and reports the social
profiles each one links to, so you can pick the channel where a person is actually active.</p>
""",
        "sections": [
            {
                "heading": 'What it looks for',
                "html": """
<p>It loads each homepage and reads the links, headers and footers for profile URLs on the major
platforms, including X, LinkedIn, Facebook, Instagram, YouTube, TikTok, Pinterest and GitHub. Most sites
put these in the footer or in a social icon row, which is exactly where it looks first.</p>
<p>It reports what the site itself publishes. It does not search the platforms, so a company with an
account it never links to will not show up.</p>
""",
            },
            {
                "heading": 'Where to get your domain list',
                "html": """
<ul>
<li>Copy the domain column out of any outreach spreadsheet you already keep.</li>
<li>Take the domains from a search for sites in your field.</li>
<li>Export the referring domains from a backlink tool if you have one.</li>
<li>Reuse the list you ran through the Email and Contact Finder, so you have both an address and a
social profile for each target.</li>
</ul>
<p>One domain per line. The https prefix is optional.</p>
""",
            },
            {
                "heading": 'Using it well',
                "html": """
<p>A company account and a personal account are not the same opportunity. A brand profile is usually
run by whoever handles marketing, while a founder's personal account reaches the person who can say yes.
When a site links both, the personal one is normally the better bet.</p>
<p>Engage before you pitch. A reply to something they posted lands very differently from a cold message
to someone who has never seen your name.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Why did it miss a profile I know exists?',
             "a": 'It only reports profiles the site links to. If an account is not linked anywhere on the homepage, there is nothing on the page to find.'},
            {"q": 'Does it check whether the accounts are active?',
             "a": 'No. It reports the links only. Open the profile to see whether anyone has posted recently, because plenty of linked accounts have been dormant for years.'},
        ],
        "related": [
            _rel('outreach.email_finder', 'Email & Contact Finder', 'The primary contact-discovery tool this one complements.'),
            _rel('outreach.pitch_personalizer', 'Guest Post Pitch Personalizer', 'Personalize your outreach once you have a full contact record.'),
            _rel('classic_seo.domain_age', 'Domain Age Checker', 'Quick sanity check on a domain before you invest outreach time.'),
            _rel('outreach.broken_link_finder', 'Broken-Link Outreach Finder', 'Another source of ready-made outreach opportunities.'),
        ],
    },

    ('outreach', 'pitch-personalizer'): {
        "intro_html": """
<p>Sending the same message to fifty sites gets a poor response, but writing fifty from scratch is not
realistic either. This tool sits in between. Write your pitch once with placeholders, paste in your list
of targets, and get one ready message per site.</p>
<p>It is a starting point, not a finished email. The value is that it removes the mechanical part so you
can spend your time on the sentence that actually earns a reply.</p>
""",
        "sections": [
            {
                "heading": 'How to write the template',
                "html": """
<p>Put a placeholder wherever the target's name should appear, and the tool fills it in for each site
in your list. Keep the surrounding sentence natural, so the result reads like something a person wrote
rather than a mail merge.</p>
<p>Leave one sentence deliberately blank and fill it in yourself before sending. A single specific line
about their actual page is what separates a reply from a delete, and no tool can write it for you.</p>
""",
            },
            {
                "heading": 'Where to get your target list',
                "html": """
<ul>
<li>From the Email and Contact Finder on this site, which gives you domains and addresses together.</li>
<li>From the Broken-Link Outreach Finder, where you also get a concrete reason to write.</li>
<li>From your own prospect spreadsheet. Copy the domain column and paste it in.</li>
</ul>
<p>Check the names before you send. An automatically derived name is right most of the time, but the
few it gets wrong are the ones that make you look careless.</p>
""",
            },
            {
                "heading": 'What actually earns replies',
                "html": """
<ul>
<li><strong>Keep it short.</strong> Three or four sentences. Long pitches get skimmed and abandoned.</li>
<li><strong>Say what is in it for them.</strong> Not what you want.</li>
<li><strong>Ask one clear question.</strong> A message with three requests usually gets none answered.</li>
<li><strong>Follow up once.</strong> One polite follow up after a week is reasonable. More than that is
not.</li>
</ul>
""",
            },
        ],
        "faqs": [
            {"q": 'How many pitches can I generate at once?',
             "a": 'Paste as many targets as you need in one batch. Nothing is sent from here, so the output is just text for you to review and use.'},
            {"q": 'Does this send the emails?',
             "a": 'No. It only writes them. You copy the results into whatever you send from, which also gives you a chance to read each one before it goes.'},
            {"q": 'Will personalised templates alone get me links?',
             "a": 'They help, but the offer matters more. A well written pitch for something nobody wants still fails. Personalisation makes a good offer land, it does not rescue a weak one.'},
        ],
        "related": [
            _rel('outreach.email_finder', 'Email & Contact Finder', 'Find the actual contact address to send your personalized pitch to.'),
            _rel('outreach.broken_link_finder', 'Broken-Link Outreach Finder', 'A ready-made reason to reach out in the first place.'),
            _rel('outreach.social_profile_finder', 'Social Profile Finder', "An alternate channel when email isn't the best fit."),
            _rel('classic_seo.domain_age', 'Domain Age Checker', 'Vet a prospect before you spend outreach effort on them.'),
        ],
    },

    ('classic-seo', 'serp-preview'): {
        "intro_html": """
<p>Google shows a limited amount of your title and description, and it measures the limit in pixels
rather than characters. A title full of wide letters gets cut sooner than one made of narrow ones, which
is why character counts alone can mislead you.</p>
<p>Type your title, description and URL here and see roughly how the result will look, with a warning
when either is long enough to be truncated.</p>
""",
        "sections": [
            {
                "heading": 'How long is too long',
                "html": """
<p>As a working guide, titles get cut somewhere around 55 to 60 characters and descriptions around 155
to 160. Treat those as soft limits. The real constraint is width, and it changes between desktop and
mobile.</p>
<p>The practical fix is to front load. Put the important words first so the sentence still makes sense
when the end disappears. A title that reads well truncated is better than one that only works in full.</p>
""",
            },
            {
                "heading": 'Where to get your current title and description',
                "html": """
<ul>
<li><strong>From the live page.</strong> Open it, right click, choose View Page Source, and look for the
<code>&lt;title&gt;</code> tag and the meta description near the top.</li>
<li><strong>From your CMS.</strong> In WordPress with Yoast or Rank Math, they are in the SEO box below
the editor. Most other systems have an equivalent panel.</li>
<li><strong>From Search Console.</strong> Open Performance, filter to the page you care about, and look
at which queries it already ranks for. Write the title around the query that actually brings traffic.</li>
<li><strong>In bulk.</strong> If you have a crawler, export title and description for every page and work
through the ones that are too long or duplicated.</li>
</ul>
""",
            },
            {
                "heading": 'Writing ones that get clicked',
                "html": """
<ul>
<li><strong>Put the main phrase near the front,</strong> where it survives truncation and matches what
the searcher typed.</li>
<li><strong>Make every page different.</strong> Duplicate titles across a site are a common and easily
fixed problem.</li>
<li><strong>Write the description as an advert, not a summary.</strong> It does not affect ranking
directly, but it affects whether anyone clicks.</li>
<li><strong>Skip the keyword stuffing.</strong> Repeating a phrase three times looks like spam to a
reader deciding between ten results.</li>
</ul>
<p>Google often rewrites descriptions, and sometimes titles, to match the query. Yours is a strong
suggestion rather than a guarantee, so it is still worth writing well.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Why does Google show something different from what I wrote?',
             "a": 'Google rewrites snippets when it thinks another part of the page answers the query better. It happens most often on pages whose description is vague or stuffed with keywords, so a clear specific description reduces it.'},
            {"q": 'Does the meta description affect rankings?',
             "a": 'Not directly. It affects your click-through rate, and a result nobody clicks tends not to hold its position, so it matters indirectly.'},
            {"q": 'Should every page have a unique description?',
             "a": 'Every page that matters, yes. If you cannot write one for a page, Google will pick text from the page itself, which is usually better than a duplicate copied across the whole site.'},
        ],
        "related": [
            _rel('classic_seo.keyword_density', 'Keyword Density & Readability Analyzer', 'Check the content backing up that title and description.'),
            _rel('audit.schema_validator', 'Structured Data (JSON-LD) Validator', 'Structured data can unlock rich snippets beyond the basic preview.'),
            _rel('geo.geo_readiness', 'GEO Readiness Scorer', 'See how the same page is likely to fare in AI answer engines.'),
            _rel('classic_seo.canonical_hreflang', 'Canonical & Hreflang Checker', "Make sure the URL you're optimizing is the one Google will actually index."),
            _rel('utilities.word_counter', 'Word and Character Counter', 'Check title and description lengths as you write them.'),
        ],
    },

    ('classic-seo', 'keyword-density'): {
        "intro_html": """
<p>Keyword density had its moment twenty years ago, when repeating a phrase enough times genuinely moved
rankings. That has not been true for a long time. What the number is still good for is spotting the
opposite problems: a page that never states its own topic plainly, or one that repeats a phrase so often
it reads badly.</p>
<p>Paste your text to see which words and phrases you actually use, along with readability scores for
the writing itself.</p>
""",
        "sections": [
            {
                "heading": 'What the numbers mean',
                "html": """
<p>Density is simply how often a word appears as a share of the total. There is no target to hit. If a
phrase sits above roughly three percent you are probably repeating yourself in a way readers will
notice, and if your main topic never appears at all the page may be vaguer than you think.</p>
<p>The two and three word phrases are more useful than single words, because they are closer to how
people actually search. Nobody types one word and expects a good answer.</p>
""",
            },
            {
                "heading": 'Where to get the text to check',
                "html": """
<ul>
<li><strong>From your draft.</strong> Copy it out of your editor before publishing, which is when
changes are cheapest.</li>
<li><strong>From a live page.</strong> Select the article body with your mouse and copy it. Leave out
the navigation, sidebar and footer, or you will be measuring your menu.</li>
<li><strong>From a page that outranks you.</strong> Copy a competitor's article and run it through to
see which phrases they cover that you do not. This is the most useful way to use the tool.</li>
</ul>
<p>Paste the article text only. Including boilerplate that repeats on every page will skew every number
on the report.</p>
""",
            },
            {
                "heading": 'Readability',
                "html": """
<p>The readability scores estimate the education level needed to follow your writing. Most general
audiences are served well by something around a ninth grade level, which is lower than most people write
by default.</p>
<p>If the score is high, the usual causes are long sentences and long words. Splitting one long sentence
into two fixes more than any thesaurus will. Technical writing for a technical audience can sit higher
without any problem, so use judgement rather than chasing a number.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'What keyword density should I aim for?',
             "a": 'None. There is no target that helps rankings. Write for a reader, then check the report to make sure you have not accidentally repeated a phrase or forgotten to mention your topic.'},
            {"q": 'Can high density get a page penalised?',
             "a": 'Deliberate stuffing can. In practice the bigger cost is that the page reads badly, so people leave. Both problems have the same fix.'},
            {"q": "Why do words like 'the' top the list?",
             "a": 'They are the most common words in English, so that is expected. Look at the two and three word phrases instead, which tell you something about the topic.'},
        ],
        "related": [
            _rel('classic_seo.serp_preview', 'SERP Snippet Preview', 'Check the title and description that represent this same content in search.'),
            _rel('geo.geo_readiness', 'GEO Readiness Scorer', 'See how well this content is structured for AI answer engines.'),
            _rel('audit.schema_validator', 'Structured Data (JSON-LD) Validator', 'Pair strong content with structured data for richer visibility.'),
            _rel('linkgraph.site_audit', 'Site Crawler & Semantic Audit', 'Score content quality and find thin pages across an entire site.'),
            _rel('utilities.word_counter', 'Word and Character Counter', 'Word counts, reading time and frequency in one pass.'),
        ],
    },

    ('classic-seo', 'redirect-checker'): {
        "intro_html": """
<p>A redirect that works in a browser can still be wrong. Browsers follow chains silently, so a link
that quietly passes through four hops before landing looks perfect to a visitor while wasting crawl
budget and losing a little link value at every step.</p>
<p>Paste a list of URLs to see the full chain for each one: every hop, the status code at each step, and
where it finally lands.</p>
""",
        "sections": [
            {
                "heading": 'The status codes that matter',
                "html": """
<ul>
<li><strong>200</strong> means the page loaded normally with no redirect.</li>
<li><strong>301</strong> is a permanent move. Use this when a page has moved for good, because search
engines transfer ranking signals to the new address and update their index.</li>
<li><strong>302</strong> and <strong>307</strong> are temporary. The original keeps its ranking signals.
Using a 302 for a permanent move is one of the most common redirect mistakes there is.</li>
<li><strong>404</strong> and <strong>410</strong> mean the page is gone. A redirect chain ending in a
404 is worse than no redirect, because you have spent hops to arrive nowhere.</li>
</ul>
""",
            },
            {
                "heading": 'Where to get your URL list',
                "html": """
<ul>
<li><strong>From Search Console.</strong> Open Pages under Indexing to see URLs flagged with redirect
problems, and export the list.</li>
<li><strong>From your old sitemap.</strong> After a site migration, run the previous sitemap through
here. Every old URL should land on a sensible new one in a single hop.</li>
<li><strong>From your backlinks.</strong> Export the pages other sites link to. Those are the URLs where
a broken redirect costs you the most, because the link value has nowhere to go.</li>
<li><strong>From your redirect rules.</strong> Copy the source URLs out of your .htaccess file or your
redirect plugin and confirm each one does what you intended.</li>
</ul>
<p>One URL per line, including the https prefix.</p>
""",
            },
            {
                "heading": 'Fixing what you find',
                "html": """
<p>Collapse chains. If A goes to B goes to C, change the rule so A points straight at C. Then update the
links pointing at A wherever you control them, so the redirect becomes a safety net rather than something
every visitor relies on.</p>
<p>Watch for loops, where a URL eventually redirects back to itself. A browser gives up and shows an
error, so the page is completely unreachable.</p>
<p>Check that http goes to https and that you have settled on one of www or non-www. Getting this wrong
is how a site ends up serving four versions of every page.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'How many redirects in a chain is too many?',
             "a": 'Aim for one. Two is tolerable. Beyond that you are losing crawl efficiency for no benefit, and some crawlers stop following after a handful of hops.'},
            {"q": 'Do redirects lose link value?',
             "a": 'A well implemented 301 passes nearly all of it. The loss comes from long chains and from using temporary redirects where a permanent one belongs.'},
            {"q": 'Should I redirect a deleted page to the homepage?',
             "a": 'Only if nothing better exists. Redirecting to a genuinely related page is far more useful to the visitor. Mass redirects to the homepage are often treated as soft 404s anyway, so you gain little.'},
        ],
        "related": [
            _rel('audit.broken_links', 'Broken Link Checker', 'Find outright broken links, not just redirect chains.'),
            _rel('classic_seo.canonical_hreflang', 'Canonical & Hreflang Checker', 'Redirects and canonicals both address duplicate-URL issues. Make sure they agree.'),
            _rel('audit.robots_sitemap', 'Robots.txt & Sitemap Validator', 'Check whether redirected URLs are still listed in your sitemap by mistake.'),
            _rel('audit.mixed_content', 'Mixed Content Checker', 'Another common side effect of a messy HTTP-to-HTTPS migration.'),
            _rel('utilities.line_tools', 'Duplicate Remover and Sorter', 'Clean a URL list before checking it.'),
        ],
    },

    ('classic-seo', 'canonical-hreflang'): {
        "intro_html": """
<p>Canonical and hreflang tags both tell search engines which version of a page to treat as the real one.
They are easy to get subtly wrong, and the mistakes are invisible on the page itself, so they tend to sit
there for months.</p>
<p>Enter a URL to see the canonical tag it declares, the hreflang tags it lists, and whether they are
consistent.</p>
""",
        "sections": [
            {
                "heading": 'What a canonical tag does',
                "html": """
<p>A canonical tag says "this is the address I want indexed". It matters when the same content is
reachable at several URLs, which happens constantly: with and without www, with tracking parameters
attached, with a trailing slash, or through print and sort variants.</p>
<p>Every page should have one, and on most pages it should point at itself. A page whose canonical points
somewhere else is asking not to be indexed, which is fine when you mean it and a serious problem when you
do not.</p>
""",
            },
            {
                "heading": 'The mistakes worth checking for',
                "html": """
<ul>
<li><strong>Pointing every page at the homepage.</strong> This asks search engines to drop your entire
site from the index except one page. It usually comes from a misconfigured plugin or template.</li>
<li><strong>Canonical pointing at a redirect.</strong> The signal gets muddled. Point it at the final
address.</li>
<li><strong>Mixing http and https, or www and non-www.</strong> The canonical must match the version you
actually serve, exactly.</li>
<li><strong>hreflang without a return tag.</strong> If the English page lists the French one, the French
page has to list the English one back. One-directional hreflang is ignored.</li>
<li><strong>Missing x-default.</strong> Worth adding so search engines know what to show someone whose
language you do not cover.</li>
</ul>
""",
            },
            {
                "heading": 'Where to get the URLs to check',
                "html": """
<ul>
<li><strong>From Search Console.</strong> Under Indexing, look at Pages for anything reported as
"Alternate page with proper canonical tag" or "Duplicate without user-selected canonical". Those reports
are where canonical problems show up first.</li>
<li><strong>From your sitemap.</strong> Every URL in it should be canonical to itself. Spot check a
handful from each template type: a homepage, a category, a product, a blog post.</li>
<li><strong>From your language versions.</strong> If you run a multilingual site, check one page in each
language and confirm they all point at each other.</li>
</ul>
""",
            },
        ],
        "faqs": [
            {"q": 'Can a canonical point to a different domain?',
             "a": "Yes. Cross-domain canonicals are valid and commonly used for syndicated content, where you want the original publisher's version indexed rather than the copy."},
            {"q": 'Is a canonical tag an instruction or a hint?',
             "a": 'A hint. Search engines usually follow it, but they can ignore it if other signals disagree, such as the sitemap and internal links all pointing elsewhere.'},
            {"q": 'Do I need hreflang for a site in one language?',
             "a": 'No. It only applies when you have the same content in several languages or for several regions.'},
        ],
        "related": [
            _rel('classic_seo.redirect_checker', 'Bulk Redirect & Status Checker', "Confirm your canonical target doesn't itself redirect somewhere else."),
            _rel('audit.robots_sitemap', 'Robots.txt & Sitemap Validator', "Make sure blocked or non-canonical URLs aren't listed in your sitemap."),
            _rel('audit.schema_validator', 'Structured Data (JSON-LD) Validator', 'Structured data and canonicals should agree on which URL is authoritative.'),
            _rel('classic_seo.serp_preview', 'SERP Snippet Preview', 'Preview how the canonical, indexed version will actually appear in search.'),
            _rel('utilities.utm_builder', 'UTM Link Builder', 'Build campaign URLs that consolidate to the right canonical.'),
        ],
    },

    ('classic-seo', 'header-checker'): {
        "intro_html": """
<p>HTTP headers travel with every page and are invisible unless you go looking. They control caching,
security protections, compression and more. Enter a URL to see exactly what your server sends back.</p>
""",
        "sections": [
            {
                "heading": 'The security headers worth having',
                "html": """
<ul>
<li><strong>Strict-Transport-Security</strong> tells browsers to only ever use https for your site, which
closes the gap where a first plain-http request could be intercepted.</li>
<li><strong>Content-Security-Policy</strong> limits where scripts and styles may load from. It is the
strongest defence against cross-site scripting and also the fiddliest to configure, so start in
report-only mode.</li>
<li><strong>X-Content-Type-Options: nosniff</strong> stops browsers guessing a file's type, which is a
one-line change with no real downside.</li>
<li><strong>Referrer-Policy</strong> controls how much of your URL is passed on when someone clicks a
link away from your site.</li>
<li><strong>X-Frame-Options</strong> or the equivalent CSP rule stops other sites embedding your pages in
a frame to trick users into clicking things.</li>
</ul>
""",
            },
            {
                "heading": 'The headers that affect speed',
                "html": """
<p><strong>Cache-Control</strong> decides how long browsers keep a copy of a file. Getting this right on
images, CSS and JavaScript is one of the cheapest speed improvements available, because returning
visitors stop re-downloading things that have not changed.</p>
<p><strong>Content-Encoding</strong> should show gzip or brotli on text responses. If it is missing, you
are sending HTML, CSS and JavaScript uncompressed, which typically means several times more data than
necessary.</p>
""",
            },
            {
                "heading": 'Where to get URLs worth checking',
                "html": """
<ul>
<li><strong>Start with your homepage,</strong> then check one page of each type, because headers often
differ between your CMS pages and your static files.</li>
<li><strong>Check a CSS or image file directly.</strong> Caching headers matter most there, and they are
frequently set differently from HTML.</li>
<li><strong>Check both http and https versions</strong> to confirm the redirect and the HSTS header are
in place.</li>
<li><strong>After any hosting or CDN change,</strong> re-run the check. Headers are one of the first
things to quietly change when infrastructure moves.</li>
</ul>
""",
            },
        ],
        "faqs": [
            {"q": 'Where do I change these headers?',
             "a": 'It depends on your stack. On Apache it is usually .htaccess, on Nginx the server config, and on a CDN like Cloudflare there is a rules panel. Many WordPress security plugins can also set them for you.'},
            {"q": 'Will adding security headers break my site?',
             "a": 'Content-Security-Policy can, if it blocks a script you actually need. Deploy it in report-only mode first and watch what it flags. The others are low risk.'},
            {"q": 'Do security headers help SEO?',
             "a": 'Not directly. They protect your visitors, and the caching and compression headers do affect page speed, which is a ranking factor.'},
        ],
        "related": [
            _rel('audit.mixed_content', 'Mixed Content Checker', 'Another common HTTPS-era issue worth auditing alongside your headers.'),
            _rel('classic_seo.domain_age', 'Domain Age Checker', 'Cross-check registration details as part of a broader trust audit.'),
            _rel('audit.ai_crawler_access', 'AI Crawler Access Checker', 'Headers control browsers; robots.txt controls crawlers. Check both.'),
            _rel('audit.robots_sitemap', 'Robots.txt & Sitemap Validator', 'Round out your technical audit with crawlability checks.'),
            _rel('utilities.hash_generator', 'Hash Generator', 'Verify a downloaded file against its published checksum.'),
        ],
    },

    ('classic-seo', 'domain-age'): {
        "intro_html": """
<p>How long a domain has been registered is a useful piece of background when you are weighing up a link
prospect, checking a competitor, or thinking about buying a domain. Enter one to see its registration
date, expiry, registrar and current status.</p>
<p>One thing to be clear about: domain age is not a ranking factor. Google has said so plainly. An old
domain is often a sign of an established site, but the age itself does nothing.</p>
""",
        "sections": [
            {
                "heading": 'What the dates tell you',
                "html": """
<p>The creation date is when the domain was first registered by anyone, not when the current owner took
it over. A domain created in 2004 may have changed hands several times, and its history may include uses
you would not want to inherit.</p>
<p>The expiry date is worth a look for a different reason. An owner who renews for several years at a
time is usually running a real long-term site, while a domain renewed a year at a time and close to
expiry may be about to lapse.</p>
""",
            },
            {
                "heading": 'Where to get more of the picture',
                "html": """
<ul>
<li><strong>Check the archive.</strong> Look the domain up in the Wayback Machine to see what it hosted
in the past. This is the single most useful check before buying a domain, because it reveals whether it
was once a spam site.</li>
<li><strong>Check whether it is indexed.</strong> Search for the domain to see whether search engines are
currently showing its pages at all.</li>
<li><strong>Check the current site.</strong> Open it. A registration from 2001 means very little if the
site has been a parked page for a decade.</li>
<li><strong>For link prospecting,</strong> combine this with the Email and Contact Finder so you have the
background and the contact in one pass.</li>
</ul>
""",
            },
        ],
        "faqs": [
            {"q": 'Does an older domain rank better?',
             "a": 'No. Google has stated domain age is not a ranking factor. Older domains often rank well because they have had longer to earn links and publish content, which is a different thing.'},
            {"q": 'Why is some ownership information hidden?',
             "a": "Privacy protection replaces owner details with the registrar's, and it is the default at many registrars. Data protection rules also restrict what can be published for domains registered in some regions."},
            {"q": 'Does buying an old domain give me a head start?',
             "a": 'Sometimes, and it can also give you an inherited problem. Always check what the domain was used for before, because a history of spam is difficult to undo.'},
        ],
        "related": [
            _rel('outreach.email_finder', 'Email & Contact Finder', 'Once a prospect checks out, find the right contact to pitch.'),
            _rel('classic_seo.header_checker', 'HTTP & Security Header Checker', 'Round out a domain trust check with its security posture.'),
            _rel('audit.ai_crawler_access', 'AI Crawler Access Checker', "See who's allowed to crawl a domain you're researching."),
            _rel('linkgraph.site_audit', 'Site Crawler & Semantic Audit', "Go deeper. Crawl the domain's actual content and internal links."),
        ],
    },

    ('audit', 'robots-sitemap'): {
        "intro_html": """
<p>Your sitemap tells search engines which pages you want found. Your robots.txt tells them which pages
they may not fetch. When those two disagree, you are sending a contradiction: come and index this page,
but you are not allowed to look at it.</p>
<p>Enter a site to check both files against each other and see any URLs caught in that conflict.</p>
""",
        "sections": [
            {
                "heading": 'Why the conflict matters',
                "html": """
<p>A page that is blocked in robots.txt but listed in your sitemap usually ends up indexed with no
description, showing a note that no information is available. That is worse than either including it
properly or leaving it out entirely.</p>
<p>The other common problem is the reverse. Blocking a page in robots.txt does not remove it from the
index, because the crawler cannot fetch the page to see your noindex tag. If you want a page gone, allow
crawling and add a noindex tag, or remove it and return a 404.</p>
""",
            },
            {
                "heading": 'Where to find your files',
                "html": """
<ul>
<li><strong>robots.txt</strong> always lives at the root of your domain, at /robots.txt. There is no
other valid location, and a file in a subfolder is ignored.</li>
<li><strong>Your sitemap</strong> is usually at /sitemap.xml or /sitemap_index.xml. If you are not sure,
robots.txt normally names it on a Sitemap line.</li>
<li><strong>In Search Console,</strong> open Sitemaps in the left menu to see which sitemaps Google has
actually read and when it last fetched them.</li>
<li><strong>To test a single URL,</strong> use the URL Inspection tool in Search Console. It tells you
whether that exact page is blocked and why.</li>
</ul>
""",
            },
            {
                "heading": 'What belongs in a sitemap',
                "html": """
<p>Only pages you want indexed. That means no redirects, no pages returning errors, no pages carrying a
noindex tag, and no pages canonicalised to somewhere else. A sitemap full of URLs that should not be
there teaches search engines to trust it less.</p>
<p>Keep it current. A sitemap listing pages you deleted months ago is a signal that nothing is
maintaining it.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Does blocking a page in robots.txt remove it from Google?',
             "a": 'No, and this catches people out constantly. Blocking stops crawling, not indexing. A blocked page can still appear in results based on links pointing at it. To remove a page, allow crawling and serve a noindex tag, or delete the page.'},
            {"q": 'Do I need a sitemap at all?',
             "a": 'Small, well linked sites usually get crawled fine without one. It matters most for large sites, new sites with few links, and pages that are hard to reach through normal navigation.'},
            {"q": 'How often should I update it?',
             "a": 'Most content systems regenerate it automatically whenever you publish. If yours does not, update it whenever you add or remove pages.'},
        ],
        "related": [
            _rel('audit.ai_crawler_access', 'AI Crawler Access Checker', "Robots.txt controls AI crawlers too. Check which ones you're allowing."),
            _rel('geo.llms_txt_generator', 'llms.txt Generator', 'Give AI assistants a curated summary alongside your sitemap.'),
            _rel('classic_seo.redirect_checker', 'Bulk Redirect & Status Checker', "Make sure sitemap URLs aren't secretly redirecting elsewhere."),
            _rel('linkgraph.site_audit', 'Site Crawler & Semantic Audit', 'Crawl the whole site to find orphaned or unlinked pages too.'),
        ],
    },

    ('audit', 'schema-validator'): {
        "intro_html": """
<p>Structured data is a block of JSON in your page that describes what the page is about in a format
machines can read. It is what makes star ratings, prices, FAQs and recipe times appear in search results.</p>
<p>Enter a URL to pull out every JSON-LD block on the page and check whether the required fields for
each type are present.</p>
""",
        "sections": [
            {
                "heading": 'What gets checked',
                "html": """
<p>The tool finds each JSON-LD block, reads the type it declares, and compares the fields present
against the ones that type requires. A missing required field is the most common reason a page never
gets the rich result it was marked up for.</p>
<p>It checks the shape of your markup. It does not check whether the values are true, and that
distinction matters: markup claiming a five star rating on a page with no reviews is valid JSON and a
policy violation at the same time.</p>
""",
            },
            {
                "heading": 'Where to get the markup to check',
                "html": """
<ul>
<li><strong>From the live page.</strong> Enter the URL and the tool extracts the blocks itself.</li>
<li><strong>From View Page Source,</strong> if you want to read it yourself. Search for
<code>application/ld+json</code> to find each block.</li>
<li><strong>From Search Console.</strong> Under Enhancements you will see a report for each structured
data type it has detected, listing errors and warnings across your whole site. That is the fastest way to
find which pages have problems.</li>
<li><strong>From your plugin settings.</strong> In WordPress, Yoast and Rank Math both output schema
automatically, so check their settings before adding your own and creating duplicates.</li>
</ul>
""",
            },
            {
                "heading": 'Getting rich results',
                "html": """
<p>Valid markup makes a page eligible for a rich result. It does not guarantee one. Google decides per
query whether to show the enhanced format, and eligibility is the entry requirement rather than the
outcome.</p>
<p>Mark up what is actually on the page. Adding FAQ markup for questions a visitor cannot see is the
fastest way to lose the feature entirely, and repeated violations can affect the whole site.</p>
<p>Use one block per entity. Several competing blocks describing the same thing in different ways give
search engines a reason to ignore all of them.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Does structured data improve rankings?',
             "a": 'Not directly. It affects how your result is displayed, and a result with stars or prices attracts more clicks than a plain one, so the benefit is real but indirect.'},
            {"q": 'JSON-LD, Microdata or RDFa?',
             "a": 'JSON-LD. Google recommends it, and it sits in one block in the head rather than being woven through your HTML, which makes it far easier to maintain.'},
            {"q": 'Why is my valid markup not showing a rich result?',
             "a": 'Eligibility is not a guarantee. It can also take weeks after the page is recrawled, and Google withholds the feature on pages it judges low quality regardless of the markup.'},
        ],
        "related": [
            _rel('geo.geo_readiness', 'GEO Readiness Scorer', 'Structured data is one of three pillars this score is built on.'),
            _rel('classic_seo.keyword_density', 'Keyword Density & Readability Analyzer', 'Pair strong structured data with genuinely well-written content.'),
            _rel('classic_seo.serp_preview', 'SERP Snippet Preview', 'See the baseline snippet schema can enhance with rich results.'),
            _rel('geo.llms_txt_generator', 'llms.txt Generator', 'Give AI assistants an even more direct summary of your site.'),
            _rel('utilities.json_formatter', 'JSON Formatter and Validator', 'Fix the JSON syntax before checking the schema.'),
        ],
    },

    ('audit', 'mixed-content'): {
        "intro_html": """
<p>Mixed content is when a page loads over https but pulls in an image, script or stylesheet over plain
http. The padlock disappears, browsers show a security warning, and in many cases the resource is blocked
outright so part of your page simply does not load.</p>
<p>Enter a URL to find every insecure resource the page references.</p>
""",
        "sections": [
            {
                "heading": 'Active and passive',
                "html": """
<p><strong>Active mixed content</strong> is scripts, stylesheets and iframes. Browsers block these
outright, because a script loaded over http could be modified in transit and then run with full access to
your page. When a site breaks after moving to https, this is almost always why.</p>
<p><strong>Passive mixed content</strong> is images, audio and video. Browsers usually still load these
but remove the padlock. Less dangerous, still visible to every visitor.</p>
""",
            },
            {
                "heading": 'Where the insecure links usually come from',
                "html": """
<ul>
<li><strong>Old content in your database.</strong> Posts written before you moved to https often contain
hard-coded http image URLs. A search and replace across the database fixes these in one pass.</li>
<li><strong>Theme and plugin files</strong> that load fonts or scripts from an http address.</li>
<li><strong>Embedded third-party widgets</strong> such as older analytics, chat or advert code.</li>
<li><strong>Hard-coded links in templates,</strong> which are easy to miss because they were correct when
they were written.</li>
</ul>
<p>To find them in your browser, open developer tools and look at the Console. Mixed content warnings
name the exact resource and the line that requested it.</p>
""",
            },
            {
                "heading": 'Fixing it',
                "html": """
<p>Change the URLs to https wherever you control them. If a third-party resource has no https version,
replace it, because there is no safe way to keep loading it.</p>
<p>Protocol-relative URLs starting with two slashes work but are considered outdated. Write https
explicitly.</p>
<p>Once the page is clean, add a Strict-Transport-Security header so browsers stop trying http at all.
You can check whether you have one with the HTTP and Security Header Checker on this site.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Why does my padlock disappear on only some pages?',
             "a": 'Because the insecure resource is only referenced on those pages. It is usually an image embedded in one old post rather than anything site-wide.'},
            {"q": 'Does mixed content affect SEO?',
             "a": 'Indirectly. Blocked scripts can break page functionality and layout, and a browser security warning drives visitors away. Both cost you more than the markup itself.'},
            {"q": 'Will a plugin fix this for me?',
             "a": 'Several rewrite http links to https as the page renders, which works but hides the problem rather than fixing it. Correcting the stored URLs is the better long-term answer.'},
        ],
        "related": [
            _rel('classic_seo.header_checker', 'HTTP & Security Header Checker', 'Check HSTS and other headers alongside your mixed-content audit.'),
            _rel('classic_seo.redirect_checker', 'Bulk Redirect & Status Checker', 'Confirm your HTTP-to-HTTPS redirects are clean, single hops.'),
            _rel('audit.js_dependency', 'JS-Dependency Detector', 'Blocked scripts from mixed content can also break JS-rendered pages.'),
            _rel('audit.broken_links', 'Broken Link Checker', 'Round out your technical audit by checking for dead links too.'),
            _rel('utilities.url_encoder', 'URL Encoder and Decoder', 'Read the encoded resource URLs the checker reports.'),
        ],
    },

    ('audit', 'js-dependency'): {
        "intro_html": """
<p>Search engines fetch your raw HTML first and run JavaScript later, if at all. If your main content
only appears after JavaScript executes, there is a window where crawlers see an almost empty page, and
some never come back to render it.</p>
<p>This tool fetches the unrendered HTML the way a crawler first sees it and flags pages that look like
they depend on JavaScript to show their content.</p>
""",
        "sections": [
            {
                "heading": 'How the check works',
                "html": """
<p>It compares how much visible text is in the raw HTML against the size of the file, and looks for
empty container elements such as a div with an id of root, app or __next. A large HTML file with almost
no readable text, or an empty app container, strongly suggests the content is built in the browser.</p>
<p>This is a heuristic, not proof. Confirm it yourself by opening the page, viewing source, and searching
for a sentence you can see on screen. View source shows the raw HTML, unlike the Inspect panel, which
shows the page after JavaScript has run. If your sentence is missing from view source, it was added by
JavaScript.</p>
""",
            },
            {
                "heading": 'Where to check next',
                "html": """
<ul>
<li><strong>Search Console URL Inspection.</strong> Run a live test and choose View Crawled Page. That
shows the HTML Google actually received, which is the definitive answer.</li>
<li><strong>Disable JavaScript in your browser</strong> and reload. Whatever remains is roughly what a
crawler sees on its first pass.</li>
<li><strong>Compare against a competitor</strong> ranking above you for the same term, to see whether
they render server side.</li>
</ul>
""",
            },
            {
                "heading": 'What to do about it',
                "html": """
<p>Server-side rendering or static generation is the reliable fix. Frameworks like Next.js and Nuxt do
this by default, so the crawler receives finished HTML on the first request.</p>
<p>If a full rewrite is not realistic, prioritise. Your title, meta description, headings, main body text
and internal links should be in the raw HTML. Interactive widgets can safely load later.</p>
<p>Google does render JavaScript, so a client-rendered page can rank. It just costs you crawl budget and
delay, and other search engines and AI crawlers are far less capable at it than Google is.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Can Google index JavaScript pages?',
             "a": 'Yes, in a second pass after the initial crawl. That pass can lag by days on large sites, and other crawlers including several AI systems do not render JavaScript at all.'},
            {"q": 'Is React or Vue bad for SEO?',
             "a": 'Not in themselves. Rendering everything in the browser is the problem. The same frameworks used with server-side rendering produce fully crawlable pages.'},
            {"q": 'Why does the tool flag a page that looks fine to me?',
             "a": 'Because your browser has already run the JavaScript. View source rather than Inspect to see the raw HTML, which is what the tool measured.'},
        ],
        "related": [
            _rel('audit.ai_crawler_access', 'AI Crawler Access Checker', 'Even if content is renderable, confirm AI crawlers are allowed to fetch it at all.'),
            _rel('linkgraph.site_audit', 'Site Crawler & Semantic Audit', 'Audit content depth and structure across every page at once.'),
            _rel('audit.schema_validator', 'Structured Data (JSON-LD) Validator', 'Structured data is typically rendered server-side, making it a reliable fallback signal.'),
            _rel('audit.mixed_content', 'Mixed Content Checker', 'Blocked mixed-content scripts are another way rendered content can silently fail.'),
        ],
    },

    ('audit', 'broken-links'): {
        "intro_html": """
<p>Links rot. Sites move, pages get deleted, and domains lapse. A page you linked to two years ago may
be gone without anything on your end changing.</p>
<p>Enter a URL to check every outbound link on that page and see which ones fail.</p>
""",
        "sections": [
            {
                "heading": 'Reading the results',
                "html": """
<p>404 and 410 mean the page is gone. 410 is a deliberate statement that it will not come back, so those
are not worth waiting on.</p>
<p>5xx codes mean the server had a problem, which may be temporary. Worth re-checking before you act.</p>
<p>Timeouts and connection failures usually mean the domain no longer resolves. Occasionally they mean
the site is blocking automated requests, so open anything surprising in a browser before you change it.</p>
""",
            },
            {
                "heading": 'Where to find pages worth checking',
                "html": """
<ul>
<li><strong>Your oldest and most linked posts.</strong> They have had the longest to accumulate dead
links and the most visitors hitting them.</li>
<li><strong>Search Console.</strong> Under Indexing, open Pages and look at Not found (404) to see which
of your own URLs are being requested and failing.</li>
<li><strong>Your resource and roundup pages,</strong> which are mostly outbound links by nature.</li>
<li><strong>Your analytics.</strong> Look for pages with a 404 title to find broken links people are
actually clicking.</li>
</ul>
""",
            },
            {
                "heading": 'What to do with them',
                "html": """
<p>Point the link at a working replacement where one exists. If the resource has genuinely disappeared,
look it up in the Wayback Machine, which often has an archived copy worth linking to instead.</p>
<p>If nothing suitable exists, remove the link and keep the sentence. Deleting the whole sentence is
usually a bigger loss than the link was.</p>
<p>Broken outbound links are not a direct ranking factor, but they are a clear signal to a reader that a
page has not been maintained, and that judgement affects whether they trust the rest of it.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Do broken links hurt rankings?',
             "a": "Not directly. They waste crawl budget on large sites and they damage the reader's trust, which affects the behaviour signals that do matter."},
            {"q": 'Does this check my whole site?',
             "a": 'It checks one page at a time. For a site-wide crawl, use the Site Crawler and Semantic Audit tool instead.'},
            {"q": 'Some links fail here but work in my browser.',
             "a": 'Certain sites block automated requests and return an error to tools while serving normal pages to browsers. Always open a link yourself before removing it.'},
        ],
        "related": [
            _rel('classic_seo.redirect_checker', 'Bulk Redirect & Status Checker', "See the full redirect chain behind links that aren't outright broken."),
            _rel('outreach.email_finder', 'Email & Contact Finder', "Find the right contact once you've spotted a broken-link outreach opportunity."),
            _rel('linkgraph.site_audit', 'Site Crawler & Semantic Audit', 'Find broken and orphaned pages across an entire site, not just one page.'),
            _rel('audit.mixed_content', 'Mixed Content Checker', 'Another quick technical check worth running alongside this one.'),
            _rel('utilities.line_tools', 'Duplicate Remover and Sorter', 'Deduplicate a URL list before checking it.'),
        ],
    },

    ('audit', 'ai-crawler-access'): {
        "intro_html": """
<p>A growing share of people now get answers from ChatGPT, Claude, Perplexity and Google's AI overviews
rather than from a list of links. Those systems reach your site through their own crawlers, each with its
own user-agent, and your robots.txt decides which ones may read your content.</p>
<p>Enter a domain to see which AI crawlers are currently allowed and which are blocked.</p>
""",
        "sections": [
            {
                "heading": 'The crawlers worth knowing',
                "html": """
<p>They fall into two groups, and the difference matters more than most sites realise.</p>
<p><strong>Training crawlers</strong> collect content to train models. GPTBot, ClaudeBot, CCBot,
Google-Extended and Meta-ExternalAgent are in this group. Blocking them keeps your content out of future
training data and costs you nothing in traffic today.</p>
<p><strong>Live retrieval crawlers</strong> fetch pages at the moment a user asks a question, so the
assistant can cite a current source. ChatGPT-User, Claude-User, OAI-SearchBot, Claude-SearchBot and
PerplexityBot work this way. Blocking these removes you from answers people are asking right now.</p>
<p>Blocking everything is the decision most sites make by accident, usually by copying a robots.txt
snippet without reading it.</p>
""",
            },
            {
                "heading": 'Where to change these settings',
                "html": """
<ul>
<li><strong>Your robots.txt file</strong> at the root of your domain. Edit it directly over FTP, in your
hosting file manager, or through your SEO plugin. Yoast and Rank Math both have a robots.txt editor.</li>
<li><strong>To write the rules,</strong> use the Robots.txt Generator on this site, which lists the AI
crawlers so you can allow or block each one deliberately.</li>
<li><strong>To check whether it is working,</strong> re-run this tool after your change. Some hosts and
CDNs cache robots.txt for a while, so give it a few minutes.</li>
<li><strong>Google-Extended</strong> is not a crawler in its own right. It is a control that decides
whether content Google already crawled may be used in Gemini and AI overviews.</li>
</ul>
""",
            },
            {
                "heading": 'Deciding what to allow',
                "html": """
<p>There is no universally correct answer, and the honest version depends on how you make money.</p>
<p>If your traffic comes from people finding your content, being cited in AI answers is close to what
ranking used to be. Blocking retrieval crawlers removes you from that entirely.</p>
<p>If your content is the product, such as a paid publication or a reference database, keeping it out of
training data is a reasonable commercial decision.</p>
<p>A common middle ground is to allow retrieval crawlers so you can be cited, while blocking training
crawlers so your archive is not absorbed wholesale. This tool shows both groups separately so you can
make that split deliberately.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Does blocking AI crawlers affect my Google rankings?',
             "a": 'Blocking Google-Extended does not affect normal search rankings. It only controls use in Gemini and AI overviews. Blocking Googlebot itself would remove you from search entirely, which is a very different thing.'},
            {"q": 'Do AI companies respect robots.txt?',
             "a": 'The major ones publish their user-agents and state that they honour it. It is a voluntary standard with no enforcement, so treat it as a request rather than a lock.'},
            {"q": 'Will being in AI answers send me traffic?',
             "a": 'Some. Assistants increasingly link their sources, though the visitor numbers are smaller than a search result in the same position would have delivered.'},
        ],
        "related": [
            _rel('geo.llms_txt_generator', 'llms.txt Generator', 'Give allowed AI crawlers a curated summary of your site to work from.'),
            _rel('geo.geo_readiness', 'GEO Readiness Scorer', 'AI crawler access is one of three pillars this score measures.'),
            _rel('audit.robots_sitemap', 'Robots.txt & Sitemap Validator', 'Audit the same robots.txt file for standard search-engine crawlability too.'),
            _rel('classic_seo.header_checker', 'HTTP & Security Header Checker', 'Round out your technical trust and access audit.'),
        ],
    },

    ('generators', 'sitemap-generator'): {
        "intro_html": """
<p>A sitemap is a list of the pages you want search engines to index. Enter a site and this crawls it,
then hands you a finished XML sitemap you can upload.</p>
<p>Useful when your platform does not generate one, when you want to control exactly what goes in, or
when you need a sitemap for a static site with no CMS behind it.</p>
""",
        "sections": [
            {
                "heading": 'What to include',
                "html": """
<p>Only pages you want indexed, each listed once at its canonical address. Leave out anything that
redirects, returns an error, carries a noindex tag, or is canonicalised elsewhere.</p>
<p>Tag and category archives are a judgement call. Include them if they are genuinely useful landing
pages, leave them out if they are thin lists that duplicate your main content.</p>
<p>A sitemap holds up to 50,000 URLs and 50MB uncompressed. Past that you need several sitemaps and an
index file pointing at them.</p>
""",
            },
            {
                "heading": 'Where to put it and how to submit it',
                "html": """
<ol>
<li><strong>Upload it to your site root</strong> so it is reachable at yoursite.com/sitemap.xml. Use FTP,
your host's file manager, or whatever you normally deploy with.</li>
<li><strong>Reference it in robots.txt</strong> by adding a line reading Sitemap followed by the full
URL. Crawlers look there first.</li>
<li><strong>Submit it in Search Console.</strong> Open Sitemaps in the left menu, enter the path, and
submit. Come back a day later to confirm it was read without errors.</li>
<li><strong>Do the same in Bing Webmaster Tools</strong> if Bing traffic matters to you.</li>
</ol>
""",
            },
            {
                "heading": 'Keeping it accurate',
                "html": """
<p>A stale sitemap is worse than none, because it repeatedly points crawlers at pages that no longer
exist. If your platform cannot regenerate automatically, set yourself a reminder to redo it whenever you
publish or delete a batch of pages.</p>
<p>Do not bother tuning the priority and change-frequency values. Google has said it ignores them, so
they are effort with no return.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Does submitting a sitemap guarantee indexing?',
             "a": 'No. It helps pages get discovered, but each page still has to be judged worth indexing on its own merits.'},
            {"q": 'My CMS already makes one. Do I need this?',
             "a": 'Usually not. WordPress, Shopify and most modern platforms generate and update one automatically. This is for static sites, custom builds, and cases where you want manual control.'},
            {"q": 'How often should I regenerate it?',
             "a": 'Whenever your set of pages changes meaningfully. For a site that publishes weekly, monthly is plenty.'},
        ],
        "related": [
            _rel('generators.robots_generator', 'Robots.txt Generator', 'Reference your new sitemap directly from a generated robots.txt.'),
            _rel('audit.robots_sitemap', 'Robots.txt & Sitemap Validator', 'Validate the sitemap you just generated against your robots.txt rules.'),
            _rel('linkgraph.site_audit', 'Site Crawler & Semantic Audit', "Auto-discover your site's URLs instead of listing them by hand."),
            _rel('geo.llms_txt_generator', 'llms.txt Generator', 'A complementary, AI-focused summary file for the same site.'),
            _rel('utilities.slug_generator', 'URL Slug Generator', 'Plan clean URLs before they reach your sitemap.'),
        ],
    },

    ('generators', 'robots-generator'): {
        "intro_html": """
<p>robots.txt tells crawlers which parts of your site they may fetch. It is a small file with large
consequences, and a single stray line can remove a site from search results.</p>
<p>Pick your rules here and get a correctly formatted file to upload, including explicit control over the
AI crawlers.</p>
""",
        "sections": [
            {
                "heading": 'How the rules work',
                "html": """
<p>The file is a list of groups. Each starts with a User-agent line naming a crawler, followed by Allow
and Disallow lines that apply to it. A user-agent of an asterisk means every crawler not named
elsewhere.</p>
<p>The most specific matching group wins, and a crawler only obeys one group. If you write a rule for
Googlebot, Googlebot follows that group and ignores the general one entirely, which surprises people who
expect the two to combine.</p>
<p>Paths are matched from the start of the URL. A Disallow of /admin blocks /admin, /admin/, and anything
beginning with /admin such as /administrator.</p>
""",
            },
            {
                "heading": 'Where to install it and verify it',
                "html": """
<ol>
<li><strong>Upload to the domain root,</strong> so it answers at yoursite.com/robots.txt. Nowhere else
works. A file in a subfolder is invisible to crawlers.</li>
<li><strong>On WordPress,</strong> Yoast and Rank Math both include a robots.txt editor under their tools
menu, which is easier than using FTP.</li>
<li><strong>Check it loads</strong> by visiting the URL yourself before assuming it is live.</li>
<li><strong>Test specific URLs</strong> in Search Console with URL Inspection, which reports whether a
page is blocked and by which rule.</li>
<li><strong>Re-check with the AI Crawler Access Checker</strong> on this site to confirm the AI rules do
what you intended.</li>
</ol>
""",
            },
            {
                "heading": 'Mistakes that cause real damage',
                "html": """
<ul>
<li><strong>Disallow: /</strong> under a user-agent of asterisk blocks your entire site. This is the
single most damaging line in SEO, and it usually reaches production because it was correct on the staging
server and nobody changed it at launch.</li>
<li><strong>Blocking CSS and JavaScript.</strong> Search engines need these to render your pages
properly. Blocking your assets folder makes your site look broken to a crawler.</li>
<li><strong>Expecting it to hide anything.</strong> robots.txt is public, and listing a secret folder in
it advertises that the folder exists. Use real access control for anything private.</li>
<li><strong>Using it to remove pages from search.</strong> It prevents crawling, not indexing. Use a
noindex tag instead, and leave the page crawlable so the tag can be seen.</li>
</ul>
""",
            },
        ],
        "faqs": [
            {"q": 'Do I need a robots.txt file?',
             "a": 'Not strictly. Without one, everything is crawlable, which is fine for many sites. Having one lets you point at your sitemap and control the AI crawlers, so it is usually worth adding.'},
            {"q": 'Will blocking a page remove it from Google?',
             "a": 'No. It stops crawling, and a blocked page can still be indexed from links pointing at it. Use a noindex tag on a crawlable page to remove it.'},
            {"q": 'Should I block AI crawlers?',
             "a": 'It depends on your business. Blocking training crawlers protects your archive, while blocking retrieval crawlers removes you from AI answers people are asking today. The AI Crawler Access Checker explains the split.'},
        ],
        "related": [
            _rel('audit.ai_crawler_access', 'AI Crawler Access Checker', 'Verify the file you generate actually produces the access you intended.'),
            _rel('generators.sitemap_generator', 'XML Sitemap Generator', 'Generate the sitemap this robots.txt file references.'),
            _rel('audit.robots_sitemap', 'Robots.txt & Sitemap Validator', 'Cross-check your new robots.txt against your sitemap for conflicts.'),
            _rel('geo.geo_readiness', 'GEO Readiness Scorer', 'AI crawler access is one of the biggest factors in this score.'),
        ],
    },

    ('generators', 'meta-tag-generator'): {
        "intro_html": """
<p>Every page needs the same handful of tags in its head: a title, a description, a canonical, and the
Open Graph and Twitter Card tags that control how a link looks when someone shares it.</p>
<p>Fill in the fields here and get a finished snippet to paste in.</p>
""",
        "sections": [
            {
                "heading": 'What each tag does',
                "html": """
<ul>
<li><strong>title</strong> is the clickable headline in search results and the text in the browser tab.
The single most important tag on the page.</li>
<li><strong>description</strong> is the grey text under your search result. It does not affect ranking,
but it decides whether anyone clicks.</li>
<li><strong>canonical</strong> names the address you want indexed when the same content is reachable at
several URLs.</li>
<li><strong>og:title, og:description and og:image</strong> control the preview card on Facebook,
LinkedIn, WhatsApp, Slack and most messaging apps.</li>
<li><strong>twitter:card</strong> does the same for X, falling back to the Open Graph tags when it is
absent.</li>
</ul>
""",
            },
            {
                "heading": 'Where to get the values',
                "html": """
<ul>
<li><strong>Title and description:</strong> write them for the page, then check them in the SERP Snippet
Preview on this site to confirm they will not be truncated.</li>
<li><strong>Canonical:</strong> normally the page's own full URL including https and the exact domain
form you serve, with or without www.</li>
<li><strong>og:image:</strong> upload an image to your site and use its full URL. Around 1200 by 630
pixels works everywhere. It must be an absolute URL, since relative paths fail on most platforms.</li>
<li><strong>To check what an existing page already has,</strong> open View Page Source and read the head
section.</li>
</ul>
""",
            },
            {
                "heading": 'Installing and testing',
                "html": """
<p>Paste the snippet inside the head element, before the closing head tag. In WordPress you would
normally set these through your SEO plugin rather than editing the theme, so the values survive a theme
update.</p>
<p>Watch for duplicates. If a plugin already outputs Open Graph tags and you paste in another set, the
platform picks one unpredictably. Check the source after installing.</p>
<p>Test the share preview with Facebook's Sharing Debugger and LinkedIn's Post Inspector. Both cache
aggressively, so use their refresh option after making a change or you will keep seeing the old card.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Do meta keywords still matter?',
             "a": 'No. Google has ignored them for well over a decade. There is no reason to add them.'},
            {"q": 'Why is my share preview showing the wrong image?',
             "a": 'Almost always caching. Facebook and LinkedIn store the first version they fetched. Use their debugging tools to force a refresh.'},
            {"q": 'Do I need both Open Graph and Twitter Card tags?',
             "a": 'X falls back to Open Graph when Twitter tags are missing, so the Open Graph set alone covers most cases. Add the Twitter ones when you want a different image or a large-image card there.'},
        ],
        "related": [
            _rel('classic_seo.serp_preview', 'SERP Snippet Preview', 'See how the title and description you just wrote will actually render in search.'),
            _rel('audit.schema_validator', 'Structured Data (JSON-LD) Validator', 'Add structured data alongside your meta tags for richer results.'),
            _rel('converters.image_converter', 'Image Converter & Resizer', 'Prepare a properly-sized social share image.'),
            _rel('generators.htaccess_generator', '.htaccess Redirect Generator', 'Another quick technical utility for the same deploy.'),
            _rel('utilities.word_counter', 'Word and Character Counter', 'Check tag lengths before they get truncated.'),
            _rel('utilities.html_entities', 'HTML Entity Encoder', 'Escape characters that would break an attribute.'),
        ],
    },

    ('generators', 'htaccess-generator'): {
        "intro_html": """
<p>When you change a URL, the old address needs to send visitors and search engines to the new one. On
Apache servers that is done with redirect rules in a .htaccess file.</p>
<p>Paste your old and new paths as pairs and get rules ready to add.</p>
""",
        "sections": [
            {
                "heading": 'Why 301 and not 302',
                "html": """
<p>A 301 says the move is permanent. Search engines transfer the old page's ranking signals to the new
address and update their index. A 302 says the move is temporary, so the old URL keeps its signals and
stays in the index.</p>
<p>Using a 302 for a permanent move is one of the most common and most costly redirect mistakes, because
everything appears to work while the ranking value stays stranded on a URL nobody visits.</p>
""",
            },
            {
                "heading": 'Where to get your list of old and new URLs',
                "html": """
<ul>
<li><strong>From your old sitemap,</strong> saved before the change. This is why exporting one before a
migration is worth the two minutes it takes.</li>
<li><strong>From Search Console.</strong> Under Indexing, open Pages and look at Not found (404). Those
are old URLs people and crawlers are still requesting.</li>
<li><strong>From your analytics,</strong> filtered to your 404 page, which shows the broken URLs actually
receiving traffic. Fix those first.</li>
<li><strong>From your backlinks,</strong> if you have a tool that lists them. An old URL with links
pointing at it is the most valuable one to redirect.</li>
</ul>
""",
            },
            {
                "heading": 'Installing the rules safely',
                "html": """
<ol>
<li><strong>Download your current .htaccess first.</strong> It lives in your site root and may be hidden,
so enable "show hidden files" in your file manager. Keep the copy somewhere safe.</li>
<li><strong>Add the new rules, do not replace the file.</strong> It almost certainly contains rules your
CMS needs. Overwriting it is a common way to take a site offline.</li>
<li><strong>Put redirects above your CMS rewrite block,</strong> since rules are read in order and the
CMS block often ends the chain.</li>
<li><strong>Test immediately.</strong> A syntax error in .htaccess returns a 500 error for the entire
site, not just the affected page. Load your homepage the moment you save.</li>
<li><strong>Verify with the Bulk Redirect and Status Checker</strong> on this site to confirm each old URL
lands on the right page in one hop.</li>
</ol>
<p>These rules are for Apache and LiteSpeed. Nginx uses a different syntax in its server config and
ignores .htaccess entirely.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'How long should I keep redirects in place?',
             "a": 'At least a year, and permanently if the cost is low. Search engines need several crawls to transfer signals, and old links out on the web never expire.'},
            {"q": 'Do redirects slow my site down?',
             "a": 'One redirect adds an unnoticeable amount. Chains of several are what cause real delay, which is why collapsing them matters.'},
            {"q": 'Can I redirect everything to my homepage?',
             "a": 'You can, but it is usually a poor choice. Search engines often treat mass homepage redirects as soft 404s, and visitors get dropped somewhere unrelated to what they clicked.'},
        ],
        "related": [
            _rel('classic_seo.redirect_checker', 'Bulk Redirect & Status Checker', "Verify your new redirects actually work once they're live."),
            _rel('audit.robots_sitemap', 'Robots.txt & Sitemap Validator', 'Make sure your sitemap reflects the new URLs, not the redirected ones.'),
            _rel('generators.sitemap_generator', 'XML Sitemap Generator', 'Regenerate your sitemap after a URL restructuring.'),
            _rel('generators.duplicate_content', 'Duplicate Content / Page Similarity Checker', "Check old and new pages aren't both still live and duplicating each other."),
            _rel('utilities.slug_generator', 'URL Slug Generator', 'Generate the new slugs you are redirecting to.'),
        ],
    },

    ('generators', 'duplicate-content'): {
        "intro_html": """
<p>When two of your pages cover the same ground, they compete with each other. Search engines pick one
and often not the one you would have chosen, and both end up weaker than a single strong page would have
been.</p>
<p>Enter two URLs to compare how similar their content actually is, measured by word overlap, phrase
overlap and sequence matching.</p>
""",
        "sections": [
            {
                "heading": 'Reading the score',
                "html": """
<p>A high score means the pages share most of their wording. That is expected for a page and its printer
version, and a problem for two articles meant to target different searches.</p>
<p>There is no threshold that triggers a penalty, because ordinary duplicate content is not penalised. It
is filtered. Search engines pick one version to show and set the others aside, so the cost is diluted
signals rather than a punishment.</p>
<p>Judge by intent, not by percentage. Two pages at seventy percent similarity are fine if they genuinely
answer different questions, and a problem if they answer the same one twice.</p>
""",
            },
            {
                "heading": 'Where to find pages worth comparing',
                "html": """
<ul>
<li><strong>Search Console, Performance report.</strong> Filter by a query and see which of your pages
rank for it. Two of your own URLs appearing for the same term is the clearest signal you have.</li>
<li><strong>Your site search.</strong> Search your own domain for a topic and look for near-identical
titles.</li>
<li><strong>Under Indexing, open Pages</strong> and look for Duplicate without user-selected canonical,
which is Google telling you directly that it found copies.</li>
<li><strong>Your own archive.</strong> Sites that have published for years usually have two or three
articles on the same subject written at different times.</li>
</ul>
""",
            },
            {
                "heading": 'Fixing it',
                "html": """
<p><strong>Merge them.</strong> Usually the best answer. Combine the strongest parts into one page and
redirect the other to it with a 301, so the links and ranking signals consolidate.</p>
<p><strong>Or differentiate them.</strong> If both deserve to exist, rewrite each to answer a distinct
question, and link them to each other so the relationship is clear.</p>
<p><strong>Or canonicalise.</strong> When a duplicate has to exist for a technical reason, point its
canonical tag at the version you want indexed.</p>
<p>For duplicates across a whole site rather than a single pair, use the Site Crawler and Semantic Audit,
which finds them in one pass.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Is there a duplicate content penalty?',
             "a": 'No. This is a persistent myth. Ordinary duplication causes filtering, where one version is shown and the rest are set aside. Penalties apply to deliberate scraping and spam, which is a different situation.'},
            {"q": 'What about content syndicated to another site?',
             "a": 'Ask the publishing site to add a canonical tag pointing at your original. Without it, their version may be the one that ranks, especially if their domain is stronger.'},
            {"q": 'Do product pages with similar descriptions count?',
             "a": 'They can. Manufacturer descriptions reused across many retailers are a classic case. Original copy on your highest-value products is usually worth the effort.'},
        ],
        "related": [
            _rel('linkgraph.site_audit', 'Site Crawler & Semantic Audit', 'Run this same kind of check across an entire site at once.'),
            _rel('classic_seo.canonical_hreflang', 'Canonical & Hreflang Checker', 'Fix confirmed duplicates with the right canonical signal.'),
            _rel('generators.htaccess_generator', '.htaccess Redirect Generator', 'Consolidate duplicate pages with a clean 301 redirect.'),
            _rel('linkgraph.internal_links', 'Internal Link Suggestions', 'Once content is deduplicated, make sure linking is clean too.'),
            _rel('utilities.text_diff', 'Text Compare', 'See the exact lines that differ between two versions.'),
        ],
    },

    ('keywords', 'ideas'): {
        "intro_html": """
<p>Most keyword tools start with a seed word and show you what people search for. This one starts with
the same seed and shows you the shapes those searches take: the questions, the comparisons, the
"best of" phrasings and the buying-intent variants.</p>
<p>What you will not get here is search volume. That number only comes from paid data providers, and any
free tool showing it is either guessing or reselling. What you get instead is a map of how people phrase
things, which is what you actually write around.</p>
""",
        "sections": [
            {
                "heading": 'What the tool produces',
                "html": """
<p>Give it a seed phrase and it expands into the patterns real searches follow: questions beginning with
how, what, why, when and can; comparisons using versus, alternative and similar; qualifiers like best,
cheap, near me and for beginners; and commercial phrasings such as buy, price and review.</p>
<p>Question phrasings matter most. They map directly onto headings in an article, and they are the form
most likely to be picked up as a featured snippet or quoted by an AI assistant.</p>
""",
            },
            {
                "heading": 'Where to get your seed keywords',
                "html": """
<ul>
<li><strong>From Search Console.</strong> Open Performance, then the Queries tab. These are phrases you
already rank for, which makes them the strongest seeds you have. Sort by impressions and look for terms
with plenty of impressions but few clicks: you are visible and not being chosen.</li>
<li><strong>From your own site search.</strong> If visitors can search your site, that log is a list of
things people expected to find and possibly did not.</li>
<li><strong>From your support inbox.</strong> Questions customers actually ask are keyword research that
has already been validated by a human.</li>
<li><strong>From a competitor's headings.</strong> Open a page that outranks you and read its H2s. Each
one is a subtopic they decided was worth covering.</li>
<li><strong>From search suggestions.</strong> Start typing your topic into a search box and note what is
suggested. Those come from real query data.</li>
</ul>
""",
            },
            {
                "heading": 'Turning ideas into pages',
                "html": """
<p>Do not build one page per phrase. Several phrasings of the same question belong on one page, because
search engines already treat them as the same intent and splitting them makes both pages weaker.</p>
<p>Group by what the searcher wants, not by wording. Someone asking "how much does X cost" and someone
asking "X price" want the same thing. Someone asking "is X worth it" wants something different, and that
is a separate page.</p>
<p>Use the question phrasings as your headings. It makes the page easier to scan, and it matches the
wording people used to arrive.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Why is there no search volume?',
             "a": "Search volume only comes from paid providers such as Google Ads, Semrush or Ahrefs. A free tool showing volume is either estimating from a stale dataset or reselling someone else's data. We would rather give you nothing than a number you might trust."},
            {"q": 'How do I know which of these are worth writing?',
             "a": 'Check whether you already get impressions for them in Search Console, and look at what currently ranks. If the results are all big brands with deep pages, pick something more specific.'},
            {"q": 'How many keywords should one page target?',
             "a": 'One primary intent, and as many phrasings of it as read naturally. Trying to serve two different intents on one page usually means it serves neither.'},
        ],
        "related": [
            _rel('keywords.clustering', 'Keyword Clustering Tool', 'Group your generated ideas into content-silo clusters.'),
            _rel('content.grader', 'Content Grader & Keyword Optimizer', 'Turn a chosen keyword idea into fully optimized content.'),
            _rel('classic_seo.keyword_density', 'Keyword Density & Readability Analyzer', 'Check keyword usage once your content is written.'),
            _rel('geo.geo_readiness', 'GEO Readiness Scorer', 'Make sure content built around these keywords is AI-search ready too.'),
            _rel('utilities.line_tools', 'Duplicate Remover and Sorter', 'Clean the idea list before clustering it.'),
        ],
    },

    ('keywords', 'clustering'): {
        "intro_html": """
<p>A keyword export with two thousand rows is not a plan. Most of those rows are variations of the same
handful of topics, and the work is deciding which belong together on one page and which deserve their
own.</p>
<p>Paste your list and this groups it by the significant words the phrases share, so you can see the
topics rather than the rows.</p>
""",
        "sections": [
            {
                "heading": 'How the grouping works',
                "html": """
<p>Each phrase is reduced to its meaningful words, with common filler removed, and phrases sharing enough
of those words are grouped together. It is deterministic: the same list always produces the same
clusters, with no machine learning and no external service involved.</p>
<p>That also means it groups by wording rather than by meaning. Two phrases that mean the same thing in
completely different words will land in different clusters, so read the output rather than trusting it
blindly.</p>
""",
            },
            {
                "heading": 'Where to get a keyword list to cluster',
                "html": """
<ul>
<li><strong>Search Console, Performance, Queries tab.</strong> Set the date range to the last 12 months,
click Export, and use the query column. This is the best source you have because it is your own data.</li>
<li><strong>From the Keyword Ideas tool</strong> on this site. Generate phrasings around several seeds,
then paste the combined list here to see the topic structure.</li>
<li><strong>From a paid tool export,</strong> if you have one. Any CSV works; paste the keyword column.</li>
<li><strong>From your site search logs</strong> or your support inbox, which reflect real language.</li>
</ul>
<p>Clean the list first. Running it through the Duplicate Remover on this site removes repeats and
normalises capitalisation, which produces noticeably tighter clusters.</p>
""",
            },
            {
                "heading": 'Using the clusters',
                "html": """
<p>Treat each cluster as a candidate page. The largest cluster is usually your main topic, and the small
ones at the tail are often long-tail articles worth writing precisely because nobody else has.</p>
<p>Watch for two clusters that clearly cover the same ground. That usually means you already have, or are
about to create, two pages competing with each other. Merging them into one stronger page is almost
always the better call. The Duplicate Content Checker will confirm how much overlap exists.</p>
<p>Pick one phrase per cluster as the primary target, usually the one that reads most naturally as a
title, and treat the rest as phrasings to work into headings and body copy.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'How large should a cluster be before it deserves a page?',
             "a": 'There is no threshold. A cluster of three closely related phrases can justify a page if the intent is clear and nobody covers it well. A cluster of thirty loose phrases may be several pages.'},
            {"q": 'Does this use AI?',
             "a": 'No. It is deterministic word-overlap grouping, which means it is fast, free, private, and gives the same answer every time. The tradeoff is that it groups by wording rather than meaning.'},
            {"q": 'Why did two obviously related keywords end up apart?',
             "a": 'Because they share no significant words. Grouping is based on the words themselves, so synonyms are not recognised. Merge those clusters yourself.'},
        ],
        "related": [
            _rel('keywords.ideas', 'Keyword Ideas & Question Generator', 'Generate the raw keyword list to cluster.'),
            _rel('content.grader', 'Content Grader & Keyword Optimizer', 'Optimize a page for the primary keyword in each cluster.'),
            _rel('linkgraph.internal_links', 'Internal Link Suggestions', "Link clustered content pages together once they're built."),
            _rel('linkgraph.site_audit', 'Site Crawler & Semantic Audit', 'Check for cannibalization once your cluster pages are live.'),
            _rel('utilities.line_tools', 'Duplicate Remover and Sorter', 'Deduplicate a keyword export first for tighter clusters.'),
        ],
    },

    ('content', 'grader'): {
        "intro_html": """
<p>Write or paste your draft and watch the score update as you type. The grader checks the things you can
actually control on the page: whether your topic appears where it matters, how readable the writing is,
how well the structure holds up, and whether you have covered the secondary terms you listed.</p>
<p>Everything is computed from your own text in the browser session. No external service sees your draft,
and nothing is stored.</p>
""",
        "sections": [
            {
                "heading": 'What the score is made of',
                "html": """
<ul>
<li><strong>Keyword placement.</strong> Whether your target phrase appears in the title, the opening
paragraph and at least one heading. Placement matters far more than raw count.</li>
<li><strong>Density.</strong> A sanity check, not a target. It flags a phrase repeated so often that it
reads badly.</li>
<li><strong>Readability.</strong> Estimated from sentence and word length. Most audiences are served well
around a ninth grade level.</li>
<li><strong>Structure.</strong> Whether you use headings at all, and whether paragraphs are short enough
to scan.</li>
<li><strong>Secondary coverage.</strong> Which of the related terms you listed actually appear.</li>
</ul>
<p>The score is a checklist, not a verdict. A well-written page that scores 70 beats a mechanically
optimised one that scores 95.</p>
""",
            },
            {
                "heading": 'Where to get your target and secondary keywords',
                "html": """
<ul>
<li><strong>Primary keyword:</strong> from Search Console, Performance, Queries, filtered to the page you
are editing. Use the phrase that actually brings impressions rather than the one you hoped for.</li>
<li><strong>Secondary keywords:</strong> run your primary through the Keyword Ideas tool on this site and
take the question and comparison phrasings.</li>
<li><strong>From competitors:</strong> open two pages that outrank you, copy their body text into the
Keyword Density Analyzer, and note the phrases they cover that you do not.</li>
<li><strong>Editing a live page?</strong> Open it, select the article body, and paste it here. Leave out
the navigation and footer, or you will be grading your menu.</li>
</ul>
""",
            },
            {
                "heading": 'What the grader cannot see',
                "html": """
<p>It cannot tell whether your advice is correct, whether you have first-hand experience of the subject,
or whether the page deserves to rank. Those are the things search engines increasingly weigh, and no
automated score is a substitute for them.</p>
<p>The helpful-content checklist below the score is deliberately manual for that reason. Those questions
cannot be graded automatically, and working through them honestly is worth more than any number on this
page.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'What score should I aim for?',
             "a": 'High enough that nothing important is missing, which usually means the placement and structure checks pass. Chasing the last few points normally means damaging the writing.'},
            {"q": 'Is my draft sent anywhere?',
             "a": 'No. Scoring happens on your own text as you type and nothing is stored or transmitted to a third party.'},
            {"q": 'Does a high score mean the page will rank?',
             "a": 'No. It means the on-page basics are in place. Ranking also depends on the quality of the content, the authority of the site, and how strong the competing pages are.'},
        ],
        "related": [
            _rel('utilities.lorem_ipsum', 'Lorem Ipsum Generator', 'Placeholder copy for mockups before the real draft exists.'),
            _rel('keywords.ideas', 'Keyword Ideas & Question Generator', 'Find the keyword to grade your content against.'),
            _rel('classic_seo.keyword_density', 'Keyword Density & Readability Analyzer', 'A simpler, non-live version of the keyword/readability checks.'),
            _rel('geo.geo_readiness', 'GEO Readiness Scorer', "Check the same content's readiness for AI answer engines."),
            _rel('linkgraph.internal_links', 'Internal Link Suggestions', "Once content is written, make sure it's well linked internally too."),
            _rel('utilities.word_counter', 'Word and Character Counter', 'Quick counts and reading time for a draft.'),
        ],
    },

    ('geo', 'llms-txt-generator'): {
        "intro_html": """
<p>AI assistants read pages differently from search crawlers. An llms.txt file is a proposed convention
for giving them a clean, structured summary of your site in Markdown, so they can find the important
pages without wading through your navigation, adverts and cookie banner.</p>
<p>Enter your site and this builds one from your sitemap, which you can then edit and upload.</p>
""",
        "sections": [
            {
                "heading": 'What the file contains',
                "html": """
<p>A title, a short description of what the site is, and a curated list of links with a line of context
each. It is written in Markdown because that is what the convention specifies and because it is the
format language models handle most reliably.</p>
<p>The summary at the top matters most. It is the first thing an assistant reads, and often the only
thing it reads before deciding whether your site is relevant. Write it as a plain description of what you
do and who you do it for.</p>
""",
            },
            {
                "heading": 'Where to get the pages to include',
                "html": """
<ul>
<li><strong>Your sitemap</strong> is the starting point, and the tool reads it for you. It normally lives
at /sitemap.xml.</li>
<li><strong>Search Console, Performance, Pages tab.</strong> Sort by clicks and include your best
performing pages first. If a page earns no traffic and answers no question, leave it out.</li>
<li><strong>Your own judgement.</strong> Include what you would show a knowledgeable visitor: your main
guides, your reference pages, your product or service pages. Leave out tag archives, pagination and
thin pages.</li>
</ul>
<p>Curate rather than dump. A list of forty well chosen pages with a line of context each is far more
useful than four hundred raw URLs.</p>
""",
            },
            {
                "heading": 'Installing it and setting expectations',
                "html": """
<p>Upload the file to the root of your domain so it answers at yoursite.com/llms.txt, the same place
robots.txt lives. Edit the descriptions before you upload, since generated ones are a starting point
rather than finished copy.</p>
<p>Be clear about the status of this. llms.txt is a proposed convention, not a standard, and no major AI
provider has committed to reading it. Adding one costs very little and may help; treating it as a
requirement would be overstating things.</p>
<p>What definitely does matter is whether AI crawlers can reach your pages at all. Check that with the AI
Crawler Access Checker on this site, which reads your robots.txt against the crawlers that exist today.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Do AI companies actually read llms.txt?',
             "a": 'There is no public commitment from any major provider that they do. It is a proposed convention with growing adoption among site owners. Add it because it is cheap, not because it is guaranteed to work.'},
            {"q": 'Is this the same as robots.txt?',
             "a": 'No. robots.txt controls who may crawl, and is honoured by the major crawlers. llms.txt describes your content for machines that are already allowed in.'},
            {"q": 'How often should I update it?',
             "a": 'Whenever your important pages change meaningfully. It lists your best content, not every URL, so it changes far less often than a sitemap.'},
        ],
        "related": [
            _rel('audit.ai_crawler_access', 'AI Crawler Access Checker', 'Make sure the AI crawlers that would read your llms.txt can actually reach your site.'),
            _rel('geo.geo_readiness', 'GEO Readiness Scorer', 'Score your overall readiness for AI answer engines, not just this one file.'),
            _rel('audit.robots_sitemap', 'Robots.txt & Sitemap Validator', 'The sitemap this tool crawls to build your llms.txt file.'),
            _rel('audit.schema_validator', 'Structured Data (JSON-LD) Validator', 'Structured data gives AI systems another direct, unambiguous signal.'),
        ],
    },

    ('geo', 'geo-readiness'): {
        "intro_html": """
<p>Being cited in an AI answer works differently from ranking in a list of links. The assistant has to be
able to fetch your page, read it without executing JavaScript, find a clear answer near the top, and
identify who wrote it.</p>
<p>Enter a URL to score how well the page meets those conditions, with the specific reasons behind
each score.</p>
""",
        "sections": [
            {
                "heading": 'What gets checked',
                "html": """
<ul>
<li><strong>Can AI crawlers reach the page?</strong> Your robots.txt is checked against the retrieval
crawlers that fetch pages when someone asks a question. Blocking these removes you from answers being
given right now.</li>
<li><strong>Is the content in the raw HTML?</strong> Most AI crawlers do not run JavaScript. If your text
only appears after scripts execute, they see an empty page.</li>
<li><strong>Is there a clear answer near the top?</strong> Assistants quote the passage that most directly
answers the question. A page that opens with three paragraphs of preamble rarely gets quoted.</li>
<li><strong>Is the structure readable?</strong> Real headings, short paragraphs and lists make it far
easier to extract a specific answer.</li>
<li><strong>Is authorship identifiable?</strong> Author, date and structured data help a machine decide
whether to trust and attribute the page.</li>
</ul>
""",
            },
            {
                "heading": 'Where to find pages worth checking',
                "html": """
<ul>
<li><strong>Start with your question-answering pages.</strong> Guides, FAQs, definitions and how-tos are
the pages assistants quote most.</li>
<li><strong>Search Console, Performance.</strong> Filter queries to those containing question words such
as how, what and why, then check the pages ranking for them.</li>
<li><strong>Ask an assistant your own question.</strong> Put a question you should be the best answer for
to ChatGPT, Claude or Perplexity and see who gets cited. If it is a competitor, open their page and
compare its structure with yours.</li>
<li><strong>Check one page of each template type,</strong> since these issues are usually structural and
affect every page built the same way.</li>
</ul>
""",
            },
            {
                "heading": 'Improving the score',
                "html": """
<p><strong>Answer the question in the first paragraph.</strong> The single highest-value change. Lead with
the answer, then explain. This helps human readers just as much.</p>
<p><strong>Render content on the server.</strong> If the JS Dependency Detector flags your pages, this is
the fix with the largest effect, though also the largest effort.</p>
<p><strong>Use headings that match real questions.</strong> A heading phrased as the question someone
actually asks gives an assistant an obvious passage to quote.</p>
<p><strong>Say who wrote it and when.</strong> A visible author and date, backed by structured data, is a
small change that affects whether you are attributed.</p>
<p><strong>Decide your crawler policy deliberately.</strong> Use the AI Crawler Access Checker to see
which crawlers you currently allow, and make it a choice rather than an accident.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Will a good score get me cited?',
             "a": 'It makes you eligible and easier to quote. Whether you are actually cited depends on the question, the competition, and how well your page answers it.'},
            {"q": 'Is this different from normal SEO?',
             "a": 'It overlaps heavily. Clear structure, server-rendered content and a direct answer help both. The differences are that most AI crawlers do not run JavaScript, and that the passage-level answer matters more than the whole page.'},
            {"q": 'Should I block AI crawlers instead?',
             "a": 'It depends on your business. If traffic and visibility matter, blocking retrieval crawlers removes you from answers people are asking today. If your content is the product, keeping it out of training data is reasonable. The AI Crawler Access Checker explains the split.'},
        ],
        "related": [
            _rel('audit.ai_crawler_access', 'AI Crawler Access Checker', "See the full crawler-by-crawler breakdown behind this score's biggest factor."),
            _rel('geo.llms_txt_generator', 'llms.txt Generator', 'Give AI assistants an even more direct, curated summary of your site.'),
            _rel('audit.schema_validator', 'Structured Data (JSON-LD) Validator', 'Dig into exactly which schema fields are complete or missing.'),
            _rel('classic_seo.keyword_density', 'Keyword Density & Readability Analyzer', 'Check the readability and structure of the content behind this score.'),
            _rel('utilities.json_formatter', 'JSON Formatter and Validator', 'Check the JSON-LD that identifies your author and dates.'),
        ],
    },

    ('linkgraph', 'site-audit'): {
        "intro_html": """
<p>Some problems only appear when you look at a whole site at once. A single page cannot tell you that
four articles are competing for the same search, that one section has no links pointing into it, or that
your best page is five clicks from the homepage.</p>
<p>Enter a site and this crawls it, scores the content, finds pages that overlap, suggests internal links,
and draws the whole thing as a graph you can explore.</p>
""",
        "sections": [
            {
                "heading": 'What the crawl produces',
                "html": """
<ul>
<li><strong>A content score per page,</strong> combining readability, topic depth and how much substance
the page carries.</li>
<li><strong>Cannibalisation pairs:</strong> pages whose meaning overlaps enough that they are likely
competing with each other.</li>
<li><strong>Internal link suggestions,</strong> based on which pages are genuinely related in meaning
rather than which share a keyword.</li>
<li><strong>Title, meta description and H1 checks</strong> across every page, which is where duplicates
and missing tags show up in bulk.</li>
<li><strong>An interactive link graph,</strong> where isolated pages and over-linked hubs are visible at a
glance.</li>
</ul>
<p>Similarity is measured on meaning rather than wording, so it finds two articles covering the same
ground in different words, which a keyword comparison would miss.</p>
""",
            },
            {
                "heading": 'Where to point it, and what to expect',
                "html": """
<ul>
<li><strong>Start with your blog or resource section</strong> rather than the whole site. That is where
overlap and orphan pages usually live.</li>
<li><strong>Use the page limit</strong> to keep the first run quick. A few hundred pages gives you a
reliable picture; you can raise it once you know the crawl works on your site.</li>
<li><strong>Run it after a migration</strong> to confirm the new structure links together the way you
intended.</li>
<li><strong>Cross-check against Search Console.</strong> Under Indexing, the Pages report tells you what
Google actually indexed; this tells you what your own linking looks like. Pages that are indexed but
orphaned in the graph are the ones losing out.</li>
</ul>
<p>Large crawls take time and memory, since every page has to be fetched and compared with every other
page. That comparison grows quadratically, which is why the page cap exists.</p>
""",
            },
            {
                "heading": 'What to fix first',
                "html": """
<p><strong>Cannibalisation.</strong> Two pages splitting the same intent means neither ranks as well as
one merged page would. Merge and redirect, or rewrite each to answer a distinct question.</p>
<p><strong>Orphan pages.</strong> A page nothing links to is hard to find for both crawlers and readers.
Link to it from something relevant.</p>
<p><strong>Weak content scores on important pages.</strong> Take the lowest scoring pages that matter
commercially and run them through the Content Grader.</p>
<p><strong>Missing or duplicated titles.</strong> The cheapest fix in the whole report, and often the one
with the most immediate effect.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'How long does a crawl take?',
             "a": 'It depends on the page count and how fast the site responds. A few hundred pages usually finishes in a few minutes. Very large crawls take considerably longer because every page is compared with every other page.'},
            {"q": 'Does it change anything on my site?',
             "a": 'No. It only reads pages, exactly as a search engine crawler would. Every suggestion is yours to apply or ignore.'},
            {"q": 'What similarity counts as cannibalisation?',
             "a": 'The tool flags pairs above a high similarity threshold, but treat that as a prompt to look rather than a verdict. Two genuinely different articles on one subject can score high and still both deserve to exist.'},
        ],
        "related": [
            _rel('audit.broken_links', 'Broken Link Checker', "A faster, single-page check for one specific page's outbound links."),
            _rel('audit.robots_sitemap', 'Robots.txt & Sitemap Validator', 'Check crawlability before or after a full site audit.'),
            _rel('geo.geo_readiness', 'GEO Readiness Scorer', "Score an individual page's AI-search readiness in more depth."),
            _rel('classic_seo.domain_age', 'Domain Age Checker', 'Quick context on a domain before committing to a full crawl.'),
        ],
    },

    ('linkgraph', 'internal-links'): {
        "intro_html": """
<p>Internal links are the part of SEO you fully control. No outreach, no waiting, no permission needed.
The problem is remembering what you have already written, which gets harder with every article.</p>
<p>Give this a page you want to strengthen and it crawls the rest of your site to find the pages that
should link to it, ranked by how closely they relate in meaning.</p>
""",
        "sections": [
            {
                "heading": 'How the suggestions are chosen',
                "html": """
<p>Every page on the site is compared with your target page on meaning rather than keyword overlap, so it
surfaces genuinely related articles even when they use different vocabulary.</p>
<p>The result is a list of pages that could sensibly link to your target, ordered by relevance. You decide
which ones actually make sense, because a link only helps if a reader would want to follow it.</p>
""",
            },
            {
                "heading": 'Where to find pages worth strengthening',
                "html": """
<ul>
<li><strong>Search Console, Performance.</strong> Filter to positions 5 to 20. Those pages already rank
and are close to the traffic. Internal links are one of the few levers that reliably moves them.</li>
<li><strong>Your commercial pages.</strong> Service and product pages usually have far fewer internal
links than blog posts, simply because nobody thinks to link to them.</li>
<li><strong>Anything new.</strong> A freshly published article has no internal links at all until you add
them, which is the easiest win available.</li>
<li><strong>Orphan pages from the Site Audit,</strong> which are the extreme case of this problem.</li>
</ul>
""",
            },
            {
                "heading": 'Adding the links well',
                "html": """
<ul>
<li><strong>Write anchor text that describes the destination.</strong> "Read our guide to X" tells both
the reader and the search engine what they will get. "Click here" tells neither.</li>
<li><strong>Vary the wording.</strong> Identical anchor text on every link looks manufactured.</li>
<li><strong>Put the link where it belongs in the sentence,</strong> not in a block of related links at the
bottom. Links inside the body carry more weight and get clicked far more often.</li>
<li><strong>Add a few strong links rather than many weak ones.</strong> Five links from genuinely related
articles beat thirty from tangential ones.</li>
<li><strong>Check it reads naturally.</strong> If the sentence only exists to carry the link, rewrite it.</li>
</ul>
""",
            },
        ],
        "faqs": [
            {"q": 'How many internal links should a page have?',
             "a": 'There is no correct number. Link where a reader would genuinely want to go next. A long guide might naturally carry a dozen; a short post might carry two.'},
            {"q": 'Do internal links really affect rankings?',
             "a": 'Yes, and more predictably than most tactics, because you control them entirely. They pass signals between your pages and help search engines understand which pages matter.'},
            {"q": 'Should I link from new pages to old, or old to new?',
             "a": 'Both, but linking from your established pages to a new one is usually more valuable, since those pages already have authority to pass on.'},
        ],
        "related": [
            _rel('linkgraph.site_audit', 'Site Crawler & Semantic Audit', 'The full site-wide version of this same linking analysis.'),
            _rel('generators.duplicate_content', 'Duplicate Content / Page Similarity Checker', 'Check for cannibalization on the same page in more detail.'),
            _rel('content.grader', 'Content Grader & Keyword Optimizer', "Strengthen the page's content alongside its internal linking."),
            _rel('audit.broken_links', 'Broken Link Checker', "Make sure the page's existing outbound links all still work."),
        ],
    },

    ('converters', 'csv-json'): {
        "intro_html": """
<p>CSV is what spreadsheets and exports speak. JSON is what APIs and config files speak. Moving between
them by hand is tedious and easy to get wrong, particularly when values contain commas or quotes.</p>
<p>Paste either format, pick a direction, and get the other one back.</p>
""",
        "sections": [
            {
                "heading": 'How the conversion works',
                "html": """
<p>Going from CSV to JSON, the first row is treated as the field names and each following row becomes an
object. Quoted values containing commas are handled correctly, which is where hand-rolled conversions
usually break.</p>
<p>Going the other way, a JSON array of objects becomes rows, with the union of all keys as the header.
Objects missing a key get an empty cell rather than a shifted row.</p>
<p>Everything comes back as text. Numbers stay as they were written, because guessing types is how a
product code like 007 turns into 7.</p>
""",
            },
            {
                "heading": 'Where to get the data',
                "html": """
<ul>
<li><strong>From a spreadsheet:</strong> in Excel or Google Sheets choose File, then Download or Save As,
and pick CSV. Or select the range, copy, and paste directly.</li>
<li><strong>From an API response:</strong> open browser developer tools, go to the Network tab, click the
request, and copy the response body. Run it through the JSON Formatter first if it is minified.</li>
<li><strong>From a database export:</strong> most tools offer CSV export. Paste the file contents in.</li>
<li><strong>From Search Console or analytics:</strong> both export CSV. Convert to JSON if you need to
feed the data into something that expects it.</li>
</ul>
""",
            },
            {
                "heading": 'Things that commonly go wrong',
                "html": """
<ul>
<li><strong>Semicolon separators.</strong> Excel in some regions writes semicolons instead of commas.
Find and replace them before pasting.</li>
<li><strong>Smart quotes.</strong> Copying through a word processor or chat app can replace straight
quotes with curly ones, which are not valid in JSON.</li>
<li><strong>Nested JSON.</strong> CSV is flat by nature, so deeply nested structures do not survive the
trip. Flatten before converting.</li>
<li><strong>A missing header row.</strong> Without one, your first data row becomes the field names.</li>
</ul>
""",
            },
        ],
        "faqs": [
            {"q": 'Is my data uploaded anywhere?',
             "a": 'It is sent to this server to be converted and returned. Nothing is stored afterwards. For genuinely sensitive data, use a local tool instead of any website, including this one.'},
            {"q": 'Does it handle nested JSON?',
             "a": 'Only shallowly. CSV has no way to express nesting, so flatten your structure first if it goes more than one level deep.'},
            {"q": 'Why did my leading zeros disappear?',
             "a": 'They should not here, because values are kept as text. If they vanished, it happened in the spreadsheet before export. Format the column as text before saving.'},
        ],
        "related": [
            _rel('converters.pdf_text', 'PDF Text Extractor', 'Pull text out of a PDF before reshaping it into CSV or JSON.'),
            _rel('converters.image_converter', 'Image Converter & Resizer', 'Another quick, no-limit format conversion utility.'),
            _rel('outreach.email_finder', 'Email & Contact Finder', 'Export and reshape your outreach prospect lists.'),
            _rel('linkgraph.site_audit', 'Site Crawler & Semantic Audit', 'Generates its own CSV/JSON-style data you may want to reshape further.'),
            _rel('utilities.json_formatter', 'JSON Formatter and Validator', 'Tidy or validate the JSON side of the conversion.'),
        ],
    },

    ('converters', 'image-converter'): {
        "intro_html": """
<p>Images are usually the heaviest thing on a page, and the easiest to fix. Converting to a modern format
and resizing to the size actually displayed often cuts a page's weight by more than half.</p>
<p>Upload an image, choose a format and an optional maximum width, and get the converted file back.</p>
""",
        "sections": [
            {
                "heading": 'Which format to choose',
                "html": """
<ul>
<li><strong>WebP</strong> is the sensible default for the web. Substantially smaller than JPEG at the same
quality, supports transparency, and works in every current browser.</li>
<li><strong>JPEG</strong> for photographs where you need maximum compatibility, including old email
clients and some older software.</li>
<li><strong>PNG</strong> for screenshots, logos and anything needing sharp edges or transparency. Poor
choice for photographs, where it produces very large files.</li>
</ul>
<p>The single biggest saving is usually resizing rather than reformatting. A 4000 pixel wide photo
displayed in a 800 pixel column is carrying five times the data it needs.</p>
""",
            },
            {
                "heading": 'Working out the right width',
                "html": """
<ol>
<li>Open your page and right click the image, then choose Inspect.</li>
<li>Hover over the image element and the browser shows its displayed size.</li>
<li>Set the maximum width to roughly twice that number, which keeps it sharp on high-resolution screens
without carrying data nobody sees.</li>
</ol>
<p>If a page is slow, run it through PageSpeed Insights or your browser's Lighthouse panel. Both list
oversized images specifically, with the saving each one would give you.</p>
""",
            },
            {
                "heading": 'After converting',
                "html": """
<p>Write real alt text. It is how the image is described to screen readers and to search engines, and it
is the only part of an image they can read. Describe what the image shows, not what keyword you want.</p>
<p>Add width and height attributes in your HTML. Without them the page shifts as images load, which is
both irritating and measured directly by Core Web Vitals.</p>
<p>Use lazy loading for images below the fold so they do not compete with the content someone can
actually see.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Does converting lose quality?',
             "a": 'Converting between lossy formats such as JPEG and WebP re-encodes and loses a little each time. Convert from the original wherever possible rather than from a file that has already been through the process.'},
            {"q": 'Is WebP safe to use?',
             "a": 'Yes. Every current browser supports it. Only genuinely ancient software is a problem, and if that matters to your audience, use JPEG.'},
            {"q": 'What about AVIF?',
             "a": 'Smaller again than WebP, but encoding is slow and support is less universal. WebP remains the better default for most sites today.'},
        ],
        "related": [
            _rel('converters.pdf_text', 'PDF Text Extractor', 'Another quick file-processing utility for content workflows.'),
            _rel('converters.csv_json', 'CSV ⇄ JSON Converter', 'Reshape structured data alongside your image assets.'),
            _rel('audit.mixed_content', 'Mixed Content Checker', 'Make sure your newly converted images are served securely.'),
            _rel('audit.js_dependency', 'JS-Dependency Detector', 'Check that image-heavy pages still render core content without JavaScript.'),
            _rel('utilities.color_converter', 'Colour Converter', 'Check contrast for text placed over an image.'),
        ],
    },

    ('converters', 'pdf-text'): {
        "intro_html": """
<p>Pull the text out of a PDF so you can search it, edit it, or run it through another tool. Upload the
file and get plain text back.</p>
""",
        "sections": [
            {
                "heading": 'What it can and cannot read',
                "html": """
<p>It reads PDFs where the text is real text, which covers anything exported from a word processor, a web
page, or most report generators.</p>
<p>It cannot read a scanned document. A scan is a picture of a page, and there is no text in the file to
extract. Those need optical character recognition, which is a different job entirely. If you upload a
scan you will get little or nothing back, and that is the reason.</p>
<p>To tell which you have: open the PDF and try to select a sentence with your mouse. If it highlights
word by word, it is real text. If you get a rectangle over the whole area, it is an image.</p>
""",
            },
            {
                "heading": 'What to do with the extracted text',
                "html": """
<ul>
<li><strong>Check length and readability</strong> with the Word and Character Counter.</li>
<li><strong>Compare two versions of a document</strong> by extracting both and using the Text Compare
tool.</li>
<li><strong>Repurpose a report as web content,</strong> which is usually worth doing since a PDF ranks
poorly and is awkward to read on a phone.</li>
<li><strong>Check a document you have been sent</strong> without opening it in an editor.</li>
</ul>
""",
            },
            {
                "heading": 'A note on PDFs and search',
                "html": """
<p>Search engines can index PDFs, but a PDF is almost always the weaker option. It loads slowly, reads
badly on mobile, cannot carry proper internal links or structured data, and gives you far less control
over how it appears in results.</p>
<p>If a PDF is earning traffic, that is usually a sign the content deserves a real page. Extract the text,
build a page around it, and offer the PDF as a download for people who want it.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Why did I get nothing back?',
             "a": 'Almost certainly a scanned document, where the page is an image rather than text. You need OCR software for those.'},
            {"q": 'Is the formatting preserved?',
             "a": 'No. You get plain text. Tables and multi-column layouts in particular come out in reading order rather than visual order.'},
            {"q": 'Can it extract from a password-protected PDF?',
             "a": 'Not while it is protected. Remove the password first with the PDF Password tool, which requires you to know the password.'},
        ],
        "related": [
            _rel('converters.csv_json', 'CSV ⇄ JSON Converter', 'Reshape any structured data you pull out of a PDF.'),
            _rel('converters.image_converter', 'Image Converter & Resizer', 'Handle image assets alongside your document workflow.'),
            _rel('classic_seo.keyword_density', 'Keyword Density & Readability Analyzer', 'Analyze extracted PDF text the same way you would a normal page.'),
            _rel('linkgraph.site_audit', 'Site Crawler & Semantic Audit', 'Audit your live HTML content quality alongside your PDF library.'),
            _rel('utilities.word_counter', 'Word and Character Counter', 'Count the text you extracted.'),
        ],
    },

    ('converters', 'pdf-merge'): {
        "intro_html": """
<p>Combine several PDFs into one file, in the order you choose. Upload the files and download the merged
document.</p>
""",
        "sections": [
            {
                "heading": 'How merging works',
                "html": """
<p>Pages are copied across as they are. Nothing is re-encoded, so text stays selectable, images keep their
original quality, and the result is essentially the source files placed end to end.</p>
<p>Order follows the order you provide the files in, so arrange them before uploading.</p>
<p>The merged file is roughly the sum of the originals. If that is larger than you want, run it through
the PDF Compress tool afterwards.</p>
""",
            },
            {
                "heading": 'When this is the right tool',
                "html": """
<ul>
<li>Combining chapters or sections that were written separately.</li>
<li>Putting a cover page in front of an existing report.</li>
<li>Gathering scanned pages that came out as separate files.</li>
<li>Assembling supporting documents into one attachment, which is far easier for a recipient than six
separate files.</li>
</ul>
<p>If you only need part of a document, split it first and merge the pieces you want. Merging everything
and then removing pages is more work.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Is there a limit on how many files I can merge?',
             "a": 'Practically it is bounded by total upload size rather than file count. Very large batches are better done in a couple of passes.'},
            {"q": 'Does merging reduce quality?',
             "a": 'No. Pages are copied without re-encoding, so quality is unchanged.'},
            {"q": 'What happens to bookmarks and form fields?',
             "a": 'Page content transfers reliably. Interactive features such as bookmarks, form fields and annotations may not survive, so check the result if your documents rely on them.'},
        ],
        "related": [
            _rel('converters.pdf_split', 'PDF Split', 'Break a merged file back apart if you need to.'),
            _rel('converters.pdf_compress', 'PDF Compress', "Shrink the merged file's size afterward."),
            _rel('converters.images_to_pdf', 'Image to PDF', 'Combine images into a PDF before merging it with others.'),
            _rel('converters.pdf_password', 'PDF Password Protect & Unlock', "Protect the merged document once it's assembled."),
        ],
    },

    ('converters', 'pdf-split'): {
        "intro_html": """
<p>Pull specific pages out of a PDF into a new file. Useful when you need to send one section of a long
document rather than the whole thing.</p>
""",
        "sections": [
            {
                "heading": 'Choosing pages',
                "html": """
<p>Give the pages you want as individual numbers, ranges, or a mix of both. Page numbering follows the
PDF itself, counting from one at the first page of the file.</p>
<p>Watch for documents whose printed page numbers differ from their file positions. A report with a cover
and two pages of front matter has its "page 1" as file page 4. Check in your PDF viewer, which shows the
file position, before choosing.</p>
""",
            },
            {
                "heading": 'Common reasons to split',
                "html": """
<ul>
<li>Sending one chapter or section instead of a whole manual.</li>
<li>Removing pages that contain information the recipient should not see. Splitting is the safe way to do
this, because deleting text from a PDF often leaves it recoverable underneath.</li>
<li>Separating a batch scan into individual documents.</li>
<li>Cutting a large file down to something small enough to email.</li>
</ul>
""",
            },
        ],
        "faqs": [
            {"q": 'Does the original file change?',
             "a": 'No. A new file is created and your original is untouched.'},
            {"q": 'Can I reorder pages as well as select them?',
             "a": 'This tool extracts pages. To reorder, split into the pieces you want and merge them back in the order you prefer.'},
            {"q": 'Is splitting a safe way to redact?',
             "a": 'It is safe for removing whole pages, which is genuinely removed. It is not redaction: to remove part of a page you need a proper redaction tool, because covering text with a black box leaves the text in the file.'},
        ],
        "related": [
            _rel('converters.pdf_merge', 'PDF Merge', 'Recombine split pages, or merge extracted ranges into a new file.'),
            _rel('converters.pdf_to_images', 'PDF to Images', 'Convert specific pages to images instead of separate PDFs.'),
            _rel('converters.pdf_rotate', 'PDF Rotate', 'Fix orientation on pages before or after splitting.'),
            _rel('converters.pdf_text', 'PDF Text Extractor', 'Pull the text out of a specific extracted section.'),
        ],
    },

    ('converters', 'pdf-compress'): {
        "intro_html": """
<p>Shrink a PDF so it fits an upload limit or attaches to an email. Upload the file and get a smaller one
back.</p>
""",
        "sections": [
            {
                "heading": 'How the size is reduced',
                "html": """
<p>Compression removes redundancy in the file's internal structure and streams. It works best on documents
with a lot of repeated or verbose content, which describes most reports and exports.</p>
<p>How much you save depends entirely on what is in the file. A text-heavy document can shrink
substantially. A file that is mostly high-resolution photographs will barely move, because the images are
already compressed and they are the bulk of the file.</p>
""",
            },
            {
                "heading": 'When compression will not be enough',
                "html": """
<p>If the file is dominated by images, the real fix is the images. Two options:</p>
<ul>
<li><strong>Rebuild it.</strong> Convert the pages to images with the PDF to Images tool, resize and
convert them with the Image Converter, then reassemble with Image to PDF. More steps, far bigger saving.</li>
<li><strong>Split it.</strong> If the recipient only needs part of the document, sending 8 pages instead
of 80 beats any compression.</li>
</ul>
<p>Going back to the source is better still. Re-exporting from the original document at a lower image
resolution usually beats compressing the finished PDF.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Will compression reduce quality?',
             "a": 'This removes structural redundancy rather than re-encoding your images, so visible quality is preserved. That is also why savings are modest on image-heavy files.'},
            {"q": 'Why did my file barely shrink?',
             "a": 'It is probably mostly images, which are already compressed. See the section above for what actually helps.'},
            {"q": 'Can I compress the same file twice?',
             "a": 'You can, but the second pass gains almost nothing. The redundancy is already gone.'},
        ],
        "related": [
            _rel('converters.pdf_to_images', 'PDF to Images', "An alternative path for image-heavy PDFs where stream compression alone isn't enough."),
            _rel('converters.image_converter', 'Image Converter & Resizer', 'Compress images separately for maximum size reduction.'),
            _rel('converters.pdf_merge', 'PDF Merge', 'Compress files before or after combining them.'),
            _rel('converters.pdf_password', 'PDF Password Protect & Unlock', 'Secure your compressed file before sharing it.'),
        ],
    },

    ('converters', 'pdf-rotate'): {
        "intro_html": """
<p>Rotate every page of a PDF by a fixed angle. Handy for scans that came out sideways or upside down.</p>
""",
        "sections": [
            {
                "heading": 'Choosing the angle',
                "html": """
<p>Rotation is clockwise. A page lying on its left side needs 90 degrees; one on its right needs 270; an
upside-down page needs 180.</p>
<p>The rotation applies to the whole document. If only some pages are wrong, split out the affected pages,
rotate those, and merge everything back together.</p>
""",
            },
            {
                "heading": 'Why scans come out rotated',
                "html": """
<p>Scanners record the orientation the paper went through in, not the orientation you meant. Feeding a
landscape page into a portrait scanner produces a sideways result even though the scan itself is perfect.</p>
<p>Rotation here is stored as page metadata rather than by re-drawing the page, so nothing is re-encoded
and no quality is lost. Every standard PDF viewer honours it.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Can I rotate only some pages?',
             "a": 'Not in one pass. Split out the pages that need it, rotate them, then merge everything back in order.'},
            {"q": 'Does rotating lose quality?',
             "a": 'No. The rotation is recorded as page metadata and the content is untouched.'},
            {"q": 'Why does it still look wrong in one program?',
             "a": 'A few older or unusual viewers ignore the rotation flag. Nearly all modern software honours it correctly.'},
        ],
        "related": [
            _rel('converters.pdf_split', 'PDF Split', 'Isolate a single page to rotate independently.'),
            _rel('converters.pdf_merge', 'PDF Merge', 'Recombine pages after fixing their orientation.'),
            _rel('converters.pdf_to_images', 'PDF to Images', 'Convert corrected pages to images if needed.'),
            _rel('converters.pdf_compress', 'PDF Compress', 'Shrink the file size after fixing orientation.'),
        ],
    },

    ('converters', 'pdf-watermark'): {
        "intro_html": """
<p>Stamp text across every page of a PDF. Useful for marking a document as a draft, a copy, or
confidential before you send it.</p>
""",
        "sections": [
            {
                "heading": 'What the watermark looks like',
                "html": """
<p>Your text is drawn diagonally across each page in large, light grey type, which is the conventional
draft-stamp appearance most documents use. It sits behind the content so the text underneath stays
readable.</p>
<p>The wording is yours to choose; the styling is fixed. Short words work best. A long sentence has to be
rendered small to fit, which defeats the purpose.</p>
""",
            },
            {
                "heading": 'What a watermark does and does not do',
                "html": """
<p>It sets expectations. Someone opening a page marked DRAFT knows not to treat it as final, and someone
who sees CONFIDENTIAL knows not to forward it. That is genuinely useful.</p>
<p>It is not protection. A watermark can be removed by anyone with the right software, and it does not
stop copying, printing or sharing. If a document must not be redistributed, control who receives it and
consider password protection.</p>
<p>Common uses: marking drafts, labelling copies sent for review, dating a version, and adding a client
name to a proposal.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Can I change the colour, angle or position?',
             "a": 'Not currently. The styling is fixed to the standard diagonal grey stamp; only the text is configurable.'},
            {"q": 'Can a watermark be removed?',
             "a": 'Yes, by anyone with suitable PDF software. Treat it as a label, not as security.'},
            {"q": 'Will it cover my content?',
             "a": 'It is drawn light and behind the text, so content stays readable. Very dense pages will look busier.'},
        ],
        "related": [
            _rel('converters.pdf_password', 'PDF Password Protect & Unlock', 'Add password protection alongside a visible watermark.'),
            _rel('converters.pdf_merge', 'PDF Merge', 'Watermark documents before combining them.'),
            _rel('converters.pdf_compress', 'PDF Compress', 'Shrink the file size after watermarking.'),
            _rel('converters.pdf_rotate', 'PDF Rotate', 'Fix page orientation before adding a watermark.'),
        ],
    },

    ('converters', 'pdf-to-images'): {
        "intro_html": """
<p>Turn each page of a PDF into a separate image file. Useful when you need a page as a picture rather
than a document.</p>
""",
        "sections": [
            {
                "heading": 'When you need images instead of a PDF',
                "html": """
<ul>
<li>Putting a page into a slide deck or a social post, which handle images and not PDFs.</li>
<li>Showing a page on a web page without forcing a download.</li>
<li>Getting a thumbnail or preview of a document.</li>
<li>Sending a single page to someone on a phone, where images are far easier than PDFs.</li>
</ul>
<p>Remember that the text stops being text. Nobody can select or search it, and neither can a search
engine. If the words matter, extract them with the PDF Text Extractor as well.</p>
""",
            },
            {
                "heading": 'After converting',
                "html": """
<p>The images come out at full page resolution, which is usually larger than you need. Run them through
the Image Converter to resize and convert to WebP before putting them on a web page, or you will be
serving a very heavy image.</p>
<p>Write alt text describing what the page shows. An image of a page is completely opaque to screen
readers and to search engines without it.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'What resolution are the images?',
             "a": 'Full page resolution, which is generous. Resize with the Image Converter before using them online.'},
            {"q": 'Can I convert just one page?',
             "a": 'Split that page out first, then convert the single-page file.'},
            {"q": 'Can I go back from images to a PDF?',
             "a": 'Yes, with the Image to PDF tool. The text will not come back though, because it became pixels on the way out.'},
        ],
        "related": [
            _rel('converters.images_to_pdf', 'Image to PDF', 'Reverse this conversion. Combine images back into a PDF.'),
            _rel('converters.image_converter', 'Image Converter & Resizer', 'Convert or resize the extracted images further.'),
            _rel('converters.pdf_split', 'PDF Split', 'Extract a single page before converting it to an image.'),
            _rel('converters.pdf_text', 'PDF Text Extractor', 'Pull out the text instead of a visual image.'),
        ],
    },

    ('converters', 'images-to-pdf'): {
        "intro_html": """
<p>Combine one or more images into a single PDF. Each image becomes a page, in the order you provide
them.</p>
""",
        "sections": [
            {
                "heading": 'When a PDF beats sending images',
                "html": """
<ul>
<li><strong>Photographed documents.</strong> Six phone photos of a contract are awkward; one PDF is a
document.</li>
<li><strong>Anything official.</strong> Receipts, forms and applications are usually expected as PDF, and
some systems reject images outright.</li>
<li><strong>Keeping order.</strong> Images sent separately arrive in whatever order the recipient's app
decides. A PDF fixes the sequence.</li>
<li><strong>Printing.</strong> A PDF prints predictably; loose images do not.</li>
</ul>
""",
            },
            {
                "heading": 'Getting a good result',
                "html": """
<ul>
<li><strong>Name your files in order</strong> before uploading, such as 01, 02, 03. Order follows the
order you provide.</li>
<li><strong>Crop and straighten first.</strong> A photographed page looks far more like a document once
the desk around it is cropped out.</li>
<li><strong>Do not over-compress beforehand.</strong> Text in a photograph goes blurry quickly, and blurry
text in an official document tends to get rejected.</li>
<li><strong>Check the file size afterwards.</strong> Photos make large PDFs. Run it through PDF Compress
if it needs to fit an upload limit.</li>
</ul>
<p>The result contains pictures of pages, not text. Nobody can search or select the words in it, and if
you need that you would need OCR software.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'What image formats can I use?',
             "a": 'The common web and camera formats, including JPEG, PNG and WebP. If something is rejected, convert it with the Image Converter first.'},
            {"q": 'How do I control the page order?',
             "a": 'Order follows the order the files are provided in, so name them numerically before uploading.'},
            {"q": 'Will the text in my photos be searchable?',
             "a": 'No. The pages are images, so there is no text in the file. That needs OCR, which is a different kind of tool.'},
        ],
        "related": [
            _rel('converters.pdf_to_images', 'PDF to Images', 'Reverse this conversion. Extract images back out of a PDF.'),
            _rel('converters.image_converter', 'Image Converter & Resizer', 'Prepare and resize your images before combining them.'),
            _rel('converters.pdf_merge', 'PDF Merge', 'Combine your new image-based PDF with other documents.'),
            _rel('converters.pdf_compress', 'PDF Compress', "Shrink the resulting file size if it's image-heavy."),
        ],
    },

    ('converters', 'pdf-password'): {
        "intro_html": """
<p>Add a password to a PDF so it cannot be opened without one, or remove a password from a PDF you already
have the password for.</p>
""",
        "sections": [
            {
                "heading": 'What password protection actually does',
                "html": """
<p>An open password encrypts the file. Without it the contents cannot be read at all, which is real
protection rather than a warning label.</p>
<p>What it does not do is control what happens after someone opens it. A recipient with the password can
copy, print, forward, and share both the file and the password. Encryption protects the file in transit
and at rest; it cannot follow the document around afterwards.</p>
<p>Never send the password in the same message as the file. An email containing both offers no protection
at all, since anyone reading the message has everything. Send the file one way and the password another.</p>
""",
            },
            {
                "heading": 'Removing a password',
                "html": """
<p>You need the current password. This tool unlocks a document you can already open; it does not break
encryption and cannot recover a forgotten password.</p>
<p>If you have genuinely lost the password to your own file, there is no honest shortcut here. Recovery
tools work by guessing, which takes anywhere from minutes to never depending on the password. Going back
to whoever created the document is usually faster.</p>
""",
            },
            {
                "heading": 'Choosing a password',
                "html": """
<p>Length is what matters. A long passphrase beats a short scramble of symbols, and it is easier to read
out over the phone, which you will probably end up doing.</p>
<p>Do not reuse a password you use anywhere else. This one gets shared with recipients by design, which
makes it the worst possible candidate for reuse.</p>
<p>The Password Generator on this site will produce one, and its look-alike option is worth ticking if
someone will have to type it from a screen.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Can this remove a password I do not know?',
             "a": 'No. It requires the correct password to unlock a file. It does not break encryption.'},
            {"q": 'How strong is PDF encryption?',
             "a": 'Modern PDF encryption with a long password is genuinely strong. The weak point is almost always the password itself, or sending it alongside the file.'},
            {"q": 'Can I stop people printing or copying instead?',
             "a": 'PDF permissions exist, but most viewers treat them as advisory and plenty ignore them. Only the open password provides real protection.'},
        ],
        "related": [
            _rel('converters.pdf_merge', 'PDF Merge', 'Combine documents before adding password protection.'),
            _rel('converters.pdf_watermark', 'PDF Watermark', 'Add a visible watermark alongside password protection.'),
            _rel('converters.pdf_compress', 'PDF Compress', 'Shrink the file size before or after protecting it.'),
            _rel('converters.pdf_split', 'PDF Split', 'Extract just the pages that actually need protecting.'),
            _rel('utilities.password_generator', 'Password Generator', 'Generate a strong password to protect the file with.'),
        ],
    },

    ('utilities', 'word-counter'): {
        "intro_html": """
<p>Word and character counts matter in more places than people expect. A meta description has a hard
limit, a magazine brief has a word count, and a conference talk has a time slot. This gives you all of
them at once, along with the words you lean on most.</p>
<p>Everything is counted from the text you paste. Nothing is stored.</p>
""",
        "sections": [
            {
                "heading": 'Which number matters when',
                "html": """
<ul>
<li><strong>Characters with spaces</strong> is what search engines count for titles and meta
descriptions, and what most social platforms count for post limits.</li>
<li><strong>Words</strong> is what editors and briefs use.</li>
<li><strong>Reading time</strong> sets expectations on a blog post. It assumes 200 words a minute, which
is a common average rather than a measurement of any particular reader.</li>
<li><strong>Speaking time</strong> assumes 130 words a minute, which is a comfortable presenting pace.
Useful for checking a script fits its slot.</li>
</ul>
""",
            },
            {
                "heading": 'Reading the word frequency table',
                "html": """
<p>Common words like "the" and "and" topping the list is normal and means nothing. What is worth noticing
is a content word taking an unusually large share, which usually reads as repetitive.</p>
<p>If you want that analysis properly, the Keyword Density Analyzer breaks out two and three word phrases
as well, which is closer to how people actually search.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'How long should a blog post be?',
             "a": 'There is no correct length. Cover the subject properly and stop. Long posts often rank well because thorough answers rank well, not because length itself helps.'},
            {"q": 'How many characters can a meta description be?',
             "a": 'Around 155 to 160 before it gets cut, though the real limit is pixel width. Check yours in the SERP Snippet Preview, which shows the truncation.'},
            {"q": 'Is my text stored anywhere?',
             "a": 'No. It is counted and returned, and nothing is kept.'},
        ],
        "related": [
            _rel('classic_seo.keyword_density', 'Keyword Density Analyzer', 'See which phrases you repeat, not just single words.'),
            _rel('classic_seo.serp_preview', 'SERP Snippet Preview', 'Check a title or description against the real truncation point.'),
            _rel('content.grader', 'Content Grader', 'Score a full draft for structure and readability, not just length.'),
            _rel('utilities.text_diff', 'Text Compare', 'See exactly what changed between two drafts.'),
        ],
    },

    ('utilities', 'case-converter'): {
        "intro_html": """
<p>Switching text between casing styles by hand is slow and error prone, especially across a list. This
converts between eleven styles, including the naming conventions used in code.</p>
""",
        "sections": [
            {
                "heading": 'Title case, and why tools disagree',
                "html": """
<p>There is no single title case rule. Different style guides capitalise different words. The convention
here is the most widely used one: capitalise everything except short joining words such as "of", "and",
"the" and "for", unless they are the first or last word.</p>
<p>If your house style differs, treat the output as a starting point rather than a verdict.</p>
""",
            },
            {
                "heading": 'Acronyms in code casing',
                "html": """
<p>Converting <code>myXMLParser</code> to snake_case should give <code>my_xml_parser</code>, not
<code>my_xmlparser</code>. That requires splitting a run of capitals from the word that follows it, which
plenty of converters get wrong.</p>
<p>This one handles it, so acronyms survive the trip in both directions.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Which case should I use for URLs?',
             "a": 'kebab-case, all lowercase with hyphens. The URL Slug Generator does this properly, including accents and punctuation.'},
            {"q": 'Does it change my text in any other way?',
             "a": 'No. Only capitalisation and, for the code styles, the separators between words.'},
            {"q": 'Can I convert a whole list at once?',
             "a": 'Yes. Paste as many lines as you like; every line is converted.'},
        ],
        "related": [
            _rel('utilities.slug_generator', 'URL Slug Generator', 'Turn titles into clean URLs, handling accents and punctuation.'),
            _rel('utilities.line_tools', 'Duplicate Remover and Sorter', 'Clean the list before or after converting it.'),
            _rel('generators.meta_tag_generator', 'Meta Tag Generator', 'Build the head tags once your titles are formatted.'),
        ],
    },

    ('utilities', 'slug-generator'): {
        "intro_html": """
<p>A slug is the readable part of a URL after the domain. Good ones are short, lowercase, hyphenated and
describe the page. This turns titles into slugs in bulk, handling the accents and punctuation that break
naive conversions.</p>
""",
        "sections": [
            {
                "heading": 'What makes a good slug',
                "html": """
<ul>
<li><strong>Hyphens, not underscores.</strong> Search engines read hyphens as word separators reliably.</li>
<li><strong>Short.</strong> Three to five words. A slug someone can read aloud is easier to share.</li>
<li><strong>Descriptive.</strong> It should make sense on its own, without the page title next to it.</li>
<li><strong>Stable.</strong> Changing a slug changes the URL, which breaks every link pointing at it.</li>
</ul>
<p>Accented characters are converted to their plain equivalents, so a title with them keeps its words
instead of losing them.</p>
""",
            },
            {
                "heading": 'Changing a slug on a live page',
                "html": """
<p>Once a page is published, its URL is a promise. Other sites link to it, people bookmark it, and search
engines have indexed it. Changing the slug without a redirect throws all of that away.</p>
<p>If you must change one, set up a 301 redirect from the old URL to the new one. The htaccess Redirect
Generator will write the rule, and the Bulk Redirect Checker will confirm it works in a single hop.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Should I include the date in a URL?',
             "a": 'Usually not. It makes the page look stale as soon as the year turns, and it adds length without adding meaning.'},
            {"q": 'Do keywords in the URL help rankings?',
             "a": 'Slightly, and far less than most people assume. Readability matters more, because the URL is visible in search results and when shared.'},
            {"q": 'How long is too long?',
             "a": 'There is no hard limit, but past about 60 characters it stops being readable, which is the point of a slug.'},
        ],
        "related": [
            _rel('generators.htaccess_generator', 'htaccess Redirect Generator', 'Write the 301 rule before changing a live slug.'),
            _rel('classic_seo.redirect_checker', 'Bulk Redirect Checker', 'Confirm the old URL lands on the new one in one hop.'),
            _rel('utilities.case_converter', 'Case Converter', 'Reformat titles before turning them into slugs.'),
            _rel('generators.sitemap_generator', 'XML Sitemap Generator', 'Rebuild your sitemap after URLs change.'),
        ],
    },

    ('utilities', 'line-tools'): {
        "intro_html": """
<p>Most SEO work involves lists: keywords, URLs, contacts, redirects. This does the tedious operations on
them, including removing duplicates, sorting, stripping blanks and numbering.</p>
""",
        "sections": [
            {
                "heading": 'Capitalisation and duplicates',
                "html": """
<p>By default <code>Apple</code> and <code>apple</code> count as different lines. For keyword lists, URLs
and email addresses that is usually not what you want, so untick the capitalisation option and they will
be treated as the same. The first version of each is kept.</p>
<p>Trimming spaces is on by default, because a trailing space is invisible and makes two identical lines
look different to any tool comparing them.</p>
""",
            },
            {
                "heading": 'Where this fits in a workflow',
                "html": """
<p>Cleaning a list first makes everything downstream better. A keyword export with duplicates produces
messy clusters; a URL list with trailing spaces produces false failures in a redirect check.</p>
<p>Run the list through here, then send it to the Keyword Clustering tool, the Bulk Redirect Checker, or
whichever tool you actually need.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Is the original order preserved when removing duplicates?',
             "a": 'Yes. The first occurrence of each line stays where it was and later repeats are removed.'},
            {"q": 'Can I sort numerically?',
             "a": 'Sorting is alphabetical or by line length. Numbers sort as text, so 10 comes before 9. Pad with leading zeros if that matters.'},
            {"q": 'How large a list can I paste?',
             "a": 'Large lists are fine. Everything runs in one pass, so there is no per-line overhead.'},
        ],
        "related": [
            _rel('keywords.clustering', 'Keyword Clustering', 'Group a cleaned keyword list into topics.'),
            _rel('classic_seo.redirect_checker', 'Bulk Redirect Checker', 'Run a deduplicated URL list through a redirect check.'),
            _rel('utilities.text_diff', 'Text Compare', 'Compare two lists side by side once both are sorted.'),
            _rel('outreach.email_finder', 'Email and Contact Finder', 'Feed it a cleaned list of domains.'),
        ],
    },

    ('utilities', 'text-diff'): {
        "intro_html": """
<p>Comparing two versions of a text by eye is unreliable, and the change you miss is usually the one that
mattered. This lines both versions up and marks every line that was added, removed or edited.</p>
""",
        "sections": [
            {
                "heading": 'Using the ignore options',
                "html": """
<p><strong>Ignore spacing</strong> is the one you will want most often. If one version came from a system
that re-wraps lines, every line looks changed without it, and the real edits disappear in the noise.</p>
<p><strong>Ignore capitalisation</strong> is useful when comparing lists that came from different sources
with different conventions.</p>
<p>Both affect the comparison only. The text shown is always what you pasted.</p>
""",
            },
            {
                "heading": 'Comparing lists rather than prose',
                "html": """
<p>Diffing two unsorted lists produces a mess, because a moved line reads as one removal plus one
addition. Sort both lists first with the Line Tools page and the comparison becomes genuinely readable.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Does it compare word by word?',
             "a": 'It compares line by line. A line with one changed word shows as a changed line, with both versions side by side so you can see which word.'},
            {"q": 'What does the similarity percentage mean?',
             "a": 'How much of the two texts matches overall. It is a rough guide, most useful for telling a small edit from a rewrite.'},
            {"q": 'Can I compare two live pages?',
             "a": 'Copy the body text of each into the two boxes. To compare pages for SEO overlap instead, use the Duplicate Content Checker, which compares by meaning.'},
        ],
        "related": [
            _rel('generators.duplicate_content', 'Duplicate Content Checker', 'Compare two live pages for overlap rather than exact text.'),
            _rel('utilities.line_tools', 'Duplicate Remover and Sorter', 'Sort both lists first so the comparison is readable.'),
            _rel('utilities.json_formatter', 'JSON Formatter', 'Sort keys in both files before diffing JSON.'),
        ],
    },

    ('utilities', 'json-formatter'): {
        "intro_html": """
<p>JSON is easy to read when it is formatted and almost impossible when it is not. This tidies it up,
minifies it, sorts keys, and tells you exactly which line broke when it will not parse.</p>
""",
        "sections": [
            {
                "heading": 'Why sorting keys is worth doing',
                "html": """
<p>Two JSON files can be identical in content and completely different in key order, which makes comparing
them by eye useless. Sort both, then run them through the Text Compare tool, and the real differences
stand out immediately.</p>
""",
            },
            {
                "heading": 'Structured data specifically',
                "html": """
<p>If you are working on JSON-LD for a page, this checks the syntax but not the schema rules. A block can
be perfectly valid JSON and still be missing fields the type requires.</p>
<p>Use the Structured Data Validator for that, which checks required fields against schema.org types
rather than just parsing the file.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Why does my JSON fail with a trailing comma?',
             "a": 'JavaScript allows a trailing comma after the last item; JSON does not. It is the single most common parse error.'},
            {"q": 'Are comments allowed in JSON?',
             "a": 'No. JSON has no comment syntax, so a // or /* */ line will fail to parse.'},
            {"q": 'Why did copying from a document break it?',
             "a": 'Word processors and chat apps replace straight quotes with curly ones. They look almost identical and are not valid JSON.'},
        ],
        "related": [
            _rel('utilities.uuid_generator', 'UUID Generator', 'Generate identifiers for seed and test data.'),
            _rel('audit.schema_validator', 'Structured Data Validator', 'Check JSON-LD against schema.org requirements, not just syntax.'),
            _rel('converters.csv_json', 'CSV and JSON Converter', 'Move data between spreadsheet and JSON formats.'),
            _rel('utilities.text_diff', 'Text Compare', 'Diff two JSON files once both have sorted keys.'),
        ],
    },

    ('utilities', 'utm-builder'): {
        "intro_html": """
<p>Without campaign tags, analytics lumps most of your traffic into vague buckets and you cannot tell
which newsletter, post or partner actually sent someone. UTM parameters fix that, provided you use them
consistently.</p>
""",
        "sections": [
            {
                "heading": 'Consistency is the whole game',
                "html": """
<p>Analytics tools treat tag values as literal text. <code>Facebook</code>, <code>facebook</code> and
<code>FaceBook</code> become three rows in your report, splitting one campaign three ways and making each
look smaller than it was.</p>
<p>That is why lowercase is on by default and spaces are turned into hyphens. Agree a naming convention
before you start, write it down, and stick to it. Most messy analytics data comes from three people
inventing three spellings of the same thing.</p>
""",
            },
            {
                "heading": 'Never tag internal links',
                "html": """
<p>Putting UTM parameters on links between pages of your own site restarts the visitor's session and
overwrites the original source. You lose the record of how they actually found you, and your reports start
showing your own site as a top referrer.</p>
<p>Tag only links that arrive from outside: emails, social posts, adverts, partner sites, printed QR
codes.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Which parameters are required?',
             "a": 'Source and medium. Analytics groups traffic by that pair, so a tag without them tells you nothing. Campaign is strongly recommended.'},
            {"q": 'Do UTM tags affect SEO?',
             "a": 'They create additional URLs for the same page, which is why the canonical tag matters. With a correct canonical, the tagged versions consolidate to the real page.'},
            {"q": 'Where do I see the results?',
             "a": 'In Google Analytics under Reports, then Acquisition, then Traffic acquisition. Your tags appear as Session source and Session medium.'},
        ],
        "related": [
            _rel('classic_seo.canonical_hreflang', 'Canonical Checker', 'Make sure tagged URLs consolidate to the real page.'),
            _rel('utilities.url_encoder', 'URL Encoder', 'Encode values that contain spaces or ampersands.'),
            _rel('classic_seo.redirect_checker', 'Bulk Redirect Checker', 'Confirm tagged links are not passing through redirects.'),
        ],
    },

    ('utilities', 'color-converter'): {
        "intro_html": """
<p>Convert a colour between HEX, RGB and HSL, check whether text on it will be readable, and get a ready
made set of tints and shades to build a palette from.</p>
""",
        "sections": [
            {
                "heading": 'Contrast is an accessibility requirement',
                "html": """
<p>Accessibility guidelines ask for a contrast ratio of at least 4.5 to 1 for normal body text and 3 to 1
for large text. Below that, a meaningful number of people simply cannot read it, including anyone in
bright sunlight on a phone.</p>
<p>The two ratios shown tell you whether black or white text works on your colour. If neither clears 4.5,
the colour will not work as a text background, though it may still be fine for a border or a block.</p>
""",
            },
            {
                "heading": 'Why HSL is worth learning',
                "html": """
<p>HEX and RGB are hard to adjust by eye. HSL is not: hue is the colour, saturation is how vivid, and
lightness is how bright. To build a hover state, keep hue and saturation and drop lightness by ten
percent. To build a palette, keep hue and vary the other two.</p>
<p>The tints and shades below the conversion do exactly that, giving you a consistent set to work from.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Which format should I use in CSS?',
             "a": 'Any of them works. HEX is most common in design handoffs, HSL is easiest to adjust by hand. Pick one and be consistent.'},
            {"q": 'What is the alpha value?',
             "a": 'Opacity, from 0 fully transparent to 1 fully opaque. An 8-digit HEX carries it in the last two characters.'},
            {"q": 'Does contrast affect SEO?',
             "a": 'Not directly. It affects whether people can read your page, and browser tools flag low-contrast text as an accessibility failure.'},
        ],
        "related": [
            _rel('audit.js_dependency', 'JS Dependency Detector', 'Check whether your styled content is visible without JavaScript.'),
            _rel('generators.meta_tag_generator', 'Meta Tag Generator', 'Set the Open Graph image and theme for shared links.'),
        ],
    },

    ('utilities', 'base64'): {
        "intro_html": """
<p>Base64 rewrites data using 64 safe characters so it can pass through systems that expect plain text.
Encode text into it, or decode a string back into something readable.</p>
""",
        "sections": [
            {
                "heading": 'Base64 is not encryption',
                "html": """
<p>This is the single most important thing to understand about it. Anyone can decode Base64 in seconds,
including on this page. It hides nothing.</p>
<p>Never use it to store passwords, API keys or anything else that needs to stay private. If you find
credentials stored as Base64 in a config file or a database, treat them as plaintext, because that is
effectively what they are.</p>
""",
            },
            {
                "heading": 'The URL-safe variant and padding',
                "html": """
<p>Standard Base64 uses <code>+</code> and <code>/</code>, both of which have meaning inside a URL. The
URL-safe variant swaps them for <code>-</code> and <code>_</code>. If you pulled a value out of a URL and
decoding fails, tick that box.</p>
<p>Many systems also strip the trailing <code>=</code> padding. This tool restores it automatically, so
paste what you have rather than trying to fix it first.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Why is the encoded version longer?',
             "a": 'Base64 uses four characters for every three bytes, so output is about a third larger. That is why embedding large images as Base64 usually makes a page slower, not faster.'},
            {"q": 'Can I decode any Base64 string?',
             "a": 'Only if it decodes to text. If the original was binary, such as an image, you get a message saying so rather than readable output.'},
            {"q": 'Should I embed images as Base64 in CSS?',
             "a": 'Only very small ones, such as an icon. Beyond a couple of kilobytes the size increase and the loss of caching outweigh saving one request.'},
        ],
        "related": [
            _rel('utilities.url_encoder', 'URL Encoder', 'The right tool for making text safe inside a URL.'),
            _rel('utilities.hash_generator', 'Hash Generator', 'One-way fingerprints, for when you need to compare rather than recover.'),
            _rel('audit.mixed_content', 'Mixed Content Checker', 'Find insecure resources that embedding can sometimes hide.'),
        ],
    },

    ('utilities', 'url-encoder'): {
        "intro_html": """
<p>URLs can only contain a limited set of characters. Everything else has to be percent-encoded. This
converts text into that form, or decodes an encoded URL back into something you can read.</p>
""",
        "sections": [
            {
                "heading": 'The ampersand problem',
                "html": """
<p>Inside a URL, <code>&amp;</code> separates one parameter from the next. If a value you are inserting
contains one and you do not encode it, everything after it is read as a separate parameter.</p>
<p>The link still loads, which is what makes this so easy to miss. It just silently carries the wrong
data, and the report built from it is wrong in a way nobody notices for weeks.</p>
""",
            },
            {
                "heading": 'Encoding a value versus a whole URL',
                "html": """
<p>Keep the reserved-character option ticked when you are encoding one piece of a URL, such as a search
term. Untick it when you are encoding a complete URL and want the <code>:</code> and <code>/</code> to
stay readable.</p>
<p>Getting this backwards is a common cause of double-encoded links, where <code>%20</code> becomes
<code>%2520</code> and the destination breaks.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Why do I see %20 instead of a space?',
             "a": 'That is the encoded form of a space. Some systems use a plus sign instead, which means the same thing in a query string but not in a path.'},
            {"q": 'Is URL encoding the same as HTML encoding?',
             "a": 'No. URL encoding makes text safe inside a web address. HTML encoding makes characters display as text on a page. Use the HTML Entity tool for the second.'},
            {"q": 'Do encoded URLs affect SEO?',
             "a": 'Correctly encoded ones are fine. Double-encoded ones create broken or duplicate URLs, which is worth checking with the redirect and canonical tools.'},
        ],
        "related": [
            _rel('utilities.base64_tool', 'Base64 Encoder and Decoder', 'Decode tokens and config values you find inside URLs.'),
            _rel('utilities.html_entities', 'HTML Entity Encoder', 'For making characters display as text on a page.'),
            _rel('utilities.utm_builder', 'UTM Link Builder', 'Builds correctly encoded campaign URLs for you.'),
            _rel('classic_seo.canonical_hreflang', 'Canonical Checker', 'Check that parameter variants point at one canonical page.'),
        ],
    },

    ('utilities', 'html-entities'): {
        "intro_html": """
<p>Some characters mean something to a browser. A <code>&lt;</code> starts a tag and an <code>&amp;</code>
starts an entity. To show them as themselves you have to encode them. This converts in both directions.</p>
""",
        "sections": [
            {
                "heading": 'When you need this',
                "html": """
<p>Most often when writing about code. To show a reader an example tag, it has to be encoded, or the
browser renders the tag instead of displaying it.</p>
<p>Also when placing a value inside an HTML attribute. An unencoded quote closes the attribute early and
breaks the tag, which is both a display bug and, with untrusted input, a security hole.</p>
""",
            },
            {
                "heading": 'Double encoding',
                "html": """
<p>If you see <code>&amp;amp;</code> or <code>&amp;#39;</code> appearing literally on your live pages, the
text was encoded twice. Something encoded it, then something else encoded the result.</p>
<p>It is a common CMS bug, usually caused by a plugin encoding content that was already safe. Decode the
affected text here to confirm, then find the layer doing it twice rather than patching the output.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Which characters must be encoded?',
             "a": 'At minimum the less-than sign, greater-than sign and ampersand. Quotes as well when the text goes inside an attribute.'},
            {"q": 'Are named entities better than numeric ones?',
             "a": 'Named entities are more readable. Numeric ones work for any character. Both are equally valid.'},
            {"q": 'Does encoding affect SEO?',
             "a": 'Correct encoding is invisible to search engines. Double encoding is not, because the literal entity text appears in your content and in search results.'},
        ],
        "related": [
            _rel('utilities.url_encoder', 'URL Encoder', 'For making text safe inside a web address instead.'),
            _rel('audit.schema_validator', 'Structured Data Validator', 'Check JSON-LD blocks that often contain encoded text.'),
            _rel('generators.meta_tag_generator', 'Meta Tag Generator', 'Produces correctly escaped head tags.'),
        ],
    },

    ('utilities', 'hash-generator'): {
        "intro_html": """
<p>A hash turns any input into a fixed-length fingerprint. Change one character and the output changes
completely, which makes hashes useful for checking whether two things are identical.</p>
""",
        "sections": [
            {
                "heading": 'Which algorithm to use',
                "html": """
<p><strong>SHA-256</strong> is the sensible default. Use it unless something specifically asks for
another.</p>
<p><strong>MD5 and SHA-1</strong> are broken for security purposes: researchers can deliberately produce
two different inputs with the same hash. They are still fine for non-security jobs such as spotting
duplicate files, and you will still meet them because plenty of software publishes MD5 checksums.</p>
""",
            },
            {
                "heading": 'Never hash passwords with these',
                "html": """
<p>Password storage needs a deliberately slow algorithm built for the job, such as bcrypt, scrypt or
Argon2. The algorithms here are fast by design, which is exactly the wrong property when someone is
working through a stolen database at billions of guesses a second.</p>
<p>If you are choosing a password rather than storing one, the Password Generator is the tool you want.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Can a hash be reversed?',
             "a": 'No. Hashing only goes one way. Common inputs can be looked up in precomputed tables, which is a different thing and another reason not to use these for passwords.'},
            {"q": 'Why do two files with the same content have different hashes?',
             "a": 'Something differs, usually invisible whitespace or line endings. Windows and Unix line endings produce different bytes and therefore different hashes.'},
            {"q": 'Can I hash a file?',
             "a": 'This hashes text. For a text file you can paste the contents; for images or binaries you need a local tool, since the exact bytes matter.'},
        ],
        "related": [
            _rel('utilities.password_generator', 'Password Generator', 'For creating a password rather than hashing one.'),
            _rel('utilities.base64_tool', 'Base64 Encoder', 'Reversible encoding, for when you need the original back.'),
            _rel('classic_seo.header_checker', 'Security Header Checker', "Check the other half of your site's security posture."),
        ],
    },

    ('utilities', 'password-generator'): {
        "intro_html": """
<p>Generate strong random passwords using the operating system's cryptographic random source. Nothing is
stored or logged.</p>
""",
        "sections": [
            {
                "heading": 'Length beats complexity',
                "html": """
<p>A long password made only of lowercase letters is stronger than a short one stuffed with symbols. If
you have to choose, choose longer. The entropy figure shown is roughly how many bits of randomness each
password carries; anything above 80 is far beyond what brute force can reach.</p>
<p>If a site rejects certain symbols, untick symbols and add ten more characters. You end up with a
stronger password either way.</p>
""",
            },
            {
                "heading": 'What actually protects an account',
                "html": """
<ul>
<li><strong>A different password everywhere.</strong> Most account takeovers come from a password reused
from a site that was breached, not from one that was guessed.</li>
<li><strong>A password manager.</strong> Generating a strong password is easy; remembering forty is not,
and that is what pushes people back into reuse.</li>
<li><strong>Two-factor authentication.</strong> It protects the account even if the password does leak.</li>
</ul>
<p>If you are cautious about generating passwords on any website, that is a reasonable instinct. A
password manager generates them locally and is the better habit.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Are these passwords stored?',
             "a": 'No. They are generated, returned, and not written to disk or to any log.'},
            {"q": 'What is the look-alike option for?',
             "a": 'It removes characters that are easy to confuse, such as capital O and zero. Worth using if someone will have to read the password off a screen and type it elsewhere.'},
            {"q": 'How long should a password be?',
             "a": 'Sixteen characters is a reasonable floor for anything that matters, and twenty or more for important accounts. Length is the lever that matters.'},
        ],
        "related": [
            _rel('utilities.hash_generator', 'Hash Generator', 'Understand why fast hashes are wrong for password storage.'),
            _rel('converters.pdf_password', 'PDF Password Protect', 'Somewhere you will actually need to share a password.'),
            _rel('classic_seo.header_checker', 'Security Header Checker', 'Check the security headers your site sends.'),
        ],
    },

    ('utilities', 'uuid-generator'): {
        "intro_html": """
<p>A UUID is a 128-bit identifier you can generate anywhere, with no central authority handing out
numbers, and still be confident nobody else generated the same one.</p>
""",
        "sections": [
            {
                "heading": 'What they are good for',
                "html": """
<p>Identifying things across systems that cannot coordinate: records created offline, rows merged from
several databases, tracking parameters, test fixtures.</p>
<p>Version 4 UUIDs, which this generates, are almost entirely random. The chance of a collision is small
enough to ignore in practice.</p>
""",
            },
            {
                "heading": 'Two things to know',
                "html": """
<p><strong>They are random, not secret.</strong> A UUID is fine as an identifier but should never be used
on its own as a password, session token or access key.</p>
<p><strong>They sort poorly.</strong> Because version 4 UUIDs are random, using one as a primary key on a
large table can hurt insert performance. If that matters, look at UUID version 7, which sorts by time.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Could two UUIDs ever collide?',
             "a": 'Mathematically yes, practically no. You would need to generate billions per second for many years before it became worth worrying about.'},
            {"q": 'Why do some systems want braces or uppercase?',
             "a": 'Windows and .NET tooling commonly use that format. The options here match whatever format you have been given.'},
            {"q": 'Is a UUID safe to expose in a URL?',
             "a": 'As an identifier, yes. As the only thing protecting private data, no. Anything sensitive needs a real access check.'},
        ],
        "related": [
            _rel('utilities.password_generator', 'Password Generator', 'For secrets, which a UUID is not.'),
            _rel('utilities.hash_generator', 'Hash Generator', 'Deterministic fingerprints rather than random identifiers.'),
            _rel('utilities.json_formatter', 'JSON Formatter', 'Tidy the test data you seed with them.'),
        ],
    },

    ('utilities', 'lorem-ipsum'): {
        "intro_html": """
<p>Placeholder text for mockups and layout tests. Nonsense on purpose, so people review the design rather
than the writing.</p>
""",
        "sections": [
            {
                "heading": 'Why nonsense works better than real copy',
                "html": """
<p>Fill a mockup with readable text and reviewers start editing the words. Fill it with lorem ipsum and
the conversation stays on spacing, line length and hierarchy, which is what a mockup is for.</p>
<p>It also roughly matches the letter and word length distribution of English, so a block takes up about
as much room as the real copy eventually will.</p>
""",
            },
            {
                "heading": 'Never let it reach a live page',
                "html": """
<p>Search engines index placeholder text like any other content, and a page full of lorem ipsum looks
abandoned to anyone who lands on it. It is a genuinely common launch bug.</p>
<p>Search your site for the word "lorem" before going live. If the site is already up, the Site Crawler
will find pages carrying it, since they score badly on content depth for obvious reasons.</p>
""",
            },
        ],
        "faqs": [
            {"q": 'Does lorem ipsum mean anything?',
             "a": 'It is scrambled Latin derived from a classical text, deliberately altered so it does not read as meaningful language.'},
            {"q": 'How much should I generate?',
             "a": 'Count the words in the real copy you plan to use and match it, so the mockup reflects reality rather than a comfortable fiction.'},
            {"q": 'Will it hurt my SEO if it goes live?',
             "a": 'Yes, indirectly. It is thin content with no value to a reader, and it signals an unfinished site.'},
        ],
        "related": [
            _rel('linkgraph.site_audit', 'Site Crawler and Audit', 'Find thin or placeholder pages already published.'),
            _rel('utilities.word_counter', 'Word and Character Counter', 'Match your placeholder length to the real copy.'),
            _rel('content.grader', 'Content Grader', 'Score the real copy once it replaces the placeholder.'),
        ],
    },
}


def get_seo_content(category_slug, tool_slug):
    return SEO_CONTENT.get((category_slug, tool_slug))
