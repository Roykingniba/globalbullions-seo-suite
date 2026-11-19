"""Central catalog of tools. Drives the nav menu and the homepage directory
so both stay in sync with whatever blueprints/routes actually exist."""

TOOL_CATEGORIES = [
    {
        "slug": "outreach",
        "name": "Outreach & Link Building",
        "icon": "📬",
        "tools": [
            {
                "slug": "email-finder",
                "name": "Email & Contact Finder",
                "endpoint": "outreach.email_finder",
                "description": "Scan a list of domains for contact and guest-post pages and pull out email addresses for outreach.",
            },
            {
                "slug": "broken-link-finder",
                "name": "Broken-Link Outreach Finder",
                "endpoint": "outreach.broken_link_finder",
                "description": "Scan resource pages in bulk for broken outbound links. Ready-made link-building outreach opportunities.",
            },
            {
                "slug": "social-profile-finder",
                "name": "Social Profile Finder",
                "endpoint": "outreach.social_profile_finder",
                "description": "Find a domain's linked social media profiles (X, LinkedIn, Facebook, Instagram, and more) in bulk.",
            },
            {
                "slug": "pitch-personalizer",
                "name": "Guest Post Pitch Personalizer",
                "endpoint": "outreach.pitch_personalizer",
                "description": "Bulk-personalize outreach pitch templates using each target site's own name.",
            },
        ],
    },
    {
        "slug": "classic-seo",
        "name": "Classic SEO Tools",
        "icon": "🔍",
        "tools": [
            {
                "slug": "serp-preview",
                "name": "SERP Snippet Preview",
                "endpoint": "classic_seo.serp_preview",
                "description": "Preview how a page's title and meta description will look in Google search results, with length warnings.",
            },
            {
                "slug": "keyword-density",
                "name": "Keyword Density & Readability Analyzer",
                "endpoint": "classic_seo.keyword_density",
                "description": "Analyze keyword frequency, n-grams, and Flesch reading ease for any page or pasted text.",
            },
            {
                "slug": "redirect-checker",
                "name": "Bulk Redirect & Status Checker",
                "endpoint": "classic_seo.redirect_checker",
                "description": "Check a list of URLs for status codes, redirect chains, and redirect loops.",
            },
            {
                "slug": "canonical-hreflang",
                "name": "Canonical & Hreflang Checker",
                "endpoint": "classic_seo.canonical_hreflang",
                "description": "Inspect canonical tags and hreflang annotations for conflicts, missing self-references, and reciprocity errors.",
            },
            {
                "slug": "header-checker",
                "name": "HTTP & Security Header Checker",
                "endpoint": "classic_seo.header_checker",
                "description": "Fetch raw response headers and flag missing security headers (HSTS, CSP, X-Frame-Options, etc.).",
            },
            {
                "slug": "domain-age",
                "name": "Domain Age Checker",
                "endpoint": "classic_seo.domain_age",
                "description": "Look up a domain's registration and last-updated dates via RDAP.",
            },
        ],
    },
    {
        "slug": "audit",
        "name": "Technical Audit Tools",
        "icon": "🛠️",
        "tools": [
            {
                "slug": "robots-sitemap",
                "name": "Robots.txt & Sitemap Validator",
                "endpoint": "audit.robots_sitemap",
                "description": "Fetch robots.txt and XML sitemaps, then cross-check sitemap URLs against disallow rules to flag blocked or orphaned pages.",
            },
            {
                "slug": "schema-validator",
                "name": "Structured Data (JSON-LD) Validator",
                "endpoint": "audit.schema_validator",
                "description": "Extract JSON-LD blocks from a page and check required fields for common schema.org types.",
            },
            {
                "slug": "mixed-content",
                "name": "Mixed Content Checker",
                "endpoint": "audit.mixed_content",
                "description": "Scan an HTTPS page for insecure http:// resource references (images, scripts, stylesheets).",
            },
            {
                "slug": "js-dependency",
                "name": "JS-Dependency Detector",
                "endpoint": "audit.js_dependency",
                "description": "Heuristically flag pages whose content likely depends on client-side JavaScript rendering.",
            },
            {
                "slug": "broken-links",
                "name": "Broken Link Checker",
                "endpoint": "audit.broken_links",
                "description": "Crawl a single page's outbound links and report broken (4xx/5xx) or unreachable links.",
            },
            {
                "slug": "ai-crawler-access",
                "name": "AI Crawler Access Checker",
                "endpoint": "audit.ai_crawler_access",
                "description": "Check robots.txt against GPTBot, ClaudeBot, PerplexityBot, Google-Extended and other AI crawlers to see who can access your content.",
            },
        ],
    },
    {
        "slug": "generators",
        "name": "Generators & Technical Tools",
        "icon": "⚙️",
        "tools": [
            {
                "slug": "sitemap-generator",
                "name": "XML Sitemap Generator",
                "endpoint": "generators.sitemap_generator",
                "description": "Generate a valid XML sitemap from a pasted list of URLs.",
            },
            {
                "slug": "robots-generator",
                "name": "Robots.txt Generator",
                "endpoint": "generators.robots_generator",
                "description": "Build a robots.txt file with custom disallow rules, a sitemap reference, and per-AI-crawler access control.",
            },
            {
                "slug": "meta-tag-generator",
                "name": "Meta Tag & Open Graph Generator",
                "endpoint": "generators.meta_tag_generator",
                "description": "Generate a ready-to-paste title, meta description, canonical, Open Graph, and Twitter Card tag snippet.",
            },
            {
                "slug": "htaccess-generator",
                "name": ".htaccess Redirect Generator",
                "endpoint": "generators.htaccess_generator",
                "description": "Generate Apache .htaccess 301 redirect rules from a list of old-path to new-path pairs.",
            },
            {
                "slug": "duplicate-content",
                "name": "Duplicate Content / Page Similarity Checker",
                "endpoint": "generators.duplicate_content",
                "description": "Compare two live pages for content similarity to spot near-duplicate or cannibalizing content.",
            },
        ],
    },
    {
        "slug": "keywords",
        "name": "Keyword Research",
        "icon": "🔑",
        "tools": [
            {
                "slug": "ideas",
                "name": "Keyword Ideas & Question Generator",
                "endpoint": "keywords.ideas",
                "description": "Expand a seed keyword into autocomplete-based suggestions, questions, and comparison phrases.",
            },
            {
                "slug": "clustering",
                "name": "Keyword Clustering Tool",
                "endpoint": "keywords.clustering",
                "description": "Group a flat keyword list into topic clusters based on shared significant words.",
            },
        ],
    },
    {
        "slug": "content",
        "name": "Content Optimization",
        "icon": "✍️",
        "tools": [
            {
                "slug": "grader",
                "name": "Content Grader & Keyword Optimizer",
                "endpoint": "content.grader",
                "description": "Grade content against a target keyword in real time as you edit. Keyword placement, density, readability, and keyword suggestions.",
            },
        ],
    },
    {
        "slug": "geo",
        "name": "AI Search / GEO Tools",
        "icon": "🤖",
        "tools": [
            {
                "slug": "llms-txt-generator",
                "name": "llms.txt Generator",
                "endpoint": "geo.llms_txt_generator",
                "description": "Crawl a sitemap and generate a spec-compliant llms.txt file summarizing your site for AI assistants.",
            },
            {
                "slug": "geo-readiness",
                "name": "GEO Readiness Scorer",
                "endpoint": "geo.geo_readiness",
                "description": "Score a page's readiness for AI answer engines: AI crawler access, structured data, and answer-first content structure.",
            },
        ],
    },
    {
        "slug": "linkgraph",
        "name": "Site Crawler & Internal Links",
        "icon": "🕸️",
        "tools": [
            {
                "slug": "site-audit",
                "name": "Site Crawler & Semantic Audit",
                "endpoint": "linkgraph.site_audit",
                "description": "Crawl a site to detect content cannibalization, find internal link opportunities, and audit titles/meta/H1s. With an interactive link graph.",
            },
            {
                "slug": "internal-links",
                "name": "Internal Link Suggestions",
                "endpoint": "linkgraph.internal_links",
                "description": "Find which existing pages should link to a specific page, and which pages it should link out to.",
            },
        ],
    },
    {
        "slug": "converters",
        "name": "File Converters",
        "icon": "🔄",
        "tools": [
            {
                "slug": "csv-json",
                "name": "CSV ⇄ JSON Converter",
                "endpoint": "converters.csv_json",
                "description": "Convert CSV to JSON or JSON to CSV.",
            },
            {
                "slug": "image-converter",
                "name": "Image Converter & Resizer",
                "endpoint": "converters.image_converter",
                "description": "Convert images between PNG, JPEG, WEBP, GIF, and BMP, with optional resizing.",
            },
            {
                "slug": "pdf-text",
                "name": "PDF Text Extractor",
                "endpoint": "converters.pdf_text",
                "description": "Extract plain text from a PDF file.",
            },
            {
                "slug": "pdf-merge",
                "name": "PDF Merge",
                "endpoint": "converters.pdf_merge",
                "description": "Combine multiple PDF files into a single PDF.",
            },
            {
                "slug": "pdf-split",
                "name": "PDF Split",
                "endpoint": "converters.pdf_split",
                "description": "Split a PDF into individual pages, or extract a specific page range.",
            },
            {
                "slug": "pdf-compress",
                "name": "PDF Compress",
                "endpoint": "converters.pdf_compress",
                "description": "Shrink a PDF's file size by compressing its internal content streams.",
            },
            {
                "slug": "pdf-rotate",
                "name": "PDF Rotate",
                "endpoint": "converters.pdf_rotate",
                "description": "Rotate every page of a PDF by 90, 180, or 270 degrees.",
            },
            {
                "slug": "pdf-watermark",
                "name": "PDF Watermark",
                "endpoint": "converters.pdf_watermark",
                "description": "Add a diagonal text watermark to every page of a PDF.",
            },
            {
                "slug": "pdf-to-images",
                "name": "PDF to Images",
                "endpoint": "converters.pdf_to_images",
                "description": "Convert every page of a PDF into a PNG or JPEG image.",
            },
            {
                "slug": "images-to-pdf",
                "name": "Image to PDF",
                "endpoint": "converters.images_to_pdf",
                "description": "Combine one or more images into a single PDF file.",
            },
            {
                "slug": "pdf-password",
                "name": "PDF Password Protect & Unlock",
                "endpoint": "converters.pdf_password",
                "description": "Add or remove password protection on a PDF file.",
            },
        ],
    },
    {
        "slug": "utilities",
        "name": "Text & Data Utilities",
        "icon": "🧰",
        "tools": [
            {
                "slug": "word-counter",
                "name": "Word & Character Counter",
                "endpoint": "utilities.word_counter",
                "description": "Count words, characters, sentences and paragraphs, with reading time and the words you repeat most.",
            },
            {
                "slug": "case-converter",
                "name": "Case Converter",
                "endpoint": "utilities.case_converter",
                "description": "Switch text between sentence case, title case, camelCase, snake_case, kebab-case and more.",
            },
            {
                "slug": "slug-generator",
                "name": "URL Slug Generator",
                "endpoint": "utilities.slug_generator",
                "description": "Turn page titles into clean URL slugs in bulk, handling accents, punctuation and length limits.",
            },
            {
                "slug": "line-tools",
                "name": "Duplicate Remover & List Sorter",
                "endpoint": "utilities.line_tools",
                "description": "Remove duplicate lines, sort a list, strip blank lines, shuffle or number any block of text.",
            },
            {
                "slug": "text-diff",
                "name": "Text Compare (Diff Checker)",
                "endpoint": "utilities.text_diff",
                "description": "Compare two versions of a text side by side and see which lines were added, removed or changed.",
            },
            {
                "slug": "json-formatter",
                "name": "JSON Formatter & Validator",
                "endpoint": "utilities.json_formatter",
                "description": "Tidy up messy JSON or minify it, with errors that point at the exact line that broke.",
            },
            {
                "slug": "utm-builder",
                "name": "UTM Campaign Link Builder",
                "endpoint": "utilities.utm_builder",
                "description": "Build tagged campaign URLs so your analytics reports show where visitors really came from.",
            },
            {
                "slug": "color-converter",
                "name": "Colour Converter & Contrast Checker",
                "endpoint": "utilities.color_converter",
                "description": "Convert a colour between HEX, RGB and HSL, check its contrast, and get matching tints and shades.",
            },
            {
                "slug": "base64",
                "name": "Base64 Encoder & Decoder",
                "endpoint": "utilities.base64_tool",
                "description": "Encode text to Base64 or decode it back, including the URL-safe variant.",
            },
            {
                "slug": "url-encoder",
                "name": "URL Encoder & Decoder",
                "endpoint": "utilities.url_encoder",
                "description": "Percent-encode text for safe use in a URL, or decode an encoded URL back into plain text.",
            },
            {
                "slug": "html-entities",
                "name": "HTML Entity Encoder & Decoder",
                "endpoint": "utilities.html_entities",
                "description": "Convert characters to HTML entities so they display as text, or decode entities back.",
            },
            {
                "slug": "hash-generator",
                "name": "Hash Generator",
                "endpoint": "utilities.hash_generator",
                "description": "Generate MD5, SHA-1, SHA-256, SHA-384 and SHA-512 hashes from any text.",
            },
            {
                "slug": "password-generator",
                "name": "Password Generator",
                "endpoint": "utilities.password_generator",
                "description": "Generate strong random passwords with control over length and character types.",
            },
            {
                "slug": "uuid-generator",
                "name": "UUID Generator",
                "endpoint": "utilities.uuid_generator",
                "description": "Generate random version 4 UUIDs in bulk, with options for case, braces and hyphens.",
            },
            {
                "slug": "lorem-ipsum",
                "name": "Lorem Ipsum Generator",
                "endpoint": "utilities.lorem_ipsum",
                "description": "Generate placeholder paragraphs, sentences or words for mockups and layout tests.",
            },
        ],
    },
]


def find_tool(category_slug, tool_slug):
    for cat in TOOL_CATEGORIES:
        if cat["slug"] == category_slug:
            for tool in cat["tools"]:
                if tool["slug"] == tool_slug:
                    return cat, tool
    return None, None
