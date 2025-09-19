{%- extends "base.tpl" -%}

{%- block styles -%}
	<link rel="preload" href="/asset/style/home.css?v={{ version }}" as="style" onload="this.onload=null;this.rel='stylesheet'">
	<noscript><link rel="stylesheet" href="/asset/style/home.css?v={{ version }}" /></noscript>
{%- endblock -%}

{%- block content -%}
	<div class="center">
		<h1 class="typo-4">{{ constants.HEADER_SLOGAN_SPLIT }}</h1>
		<div class="typo-6">{{ constants.HEADER_DESC }}</div>
		<div class="space-1"></div>
		<div class="get-yours"><a class="button" href="/#buy">Get Yours</a></div>
    </div>

	<div class="space-3"></div>

	<div id="reviews" class="center">
		<h2 class="typo-4">Trusted by Curious Readers Everywhere</h2>
		<div class="typo-6 color-flint">
			What savvy readers across platforms are saying about our dictionaries.
			<br>
			<a href="{{ constants.GOOGLE_REVIEWS }}" target="_blank" rel="noopener noreferrer" class="external underline">Share your experience →</a>
		</div>
	</div>
	<div class="space-1"></div>
	<div class="reviews">
		{% for review in reviews %}
            <div>
                <div class="stars" title="Note: {{ review["stars"] }}/5">
                    {{ '<i class="ph-fill ph-star"></i>' * 4 }}
					{%- if review["stars"] >= 5 -%}
                    <i class="ph-fill ph-star"></i>
					{%- else -%}
                    <i class="ph-fill ph-star-half"></i>
					{%- endif -%}
                </div>
                {%- if "review_original" in review -%}
                    <div class="review typo-6">{{ review["review_original"] }}</div>
                    <div class="review-original typo-6"><i class="ph ph-translate" title="English translation of the original review"></i> “{{ review["review"] }}”</div>
                {%- else -%}
                    <div class="review typo-6">{{ review["review"] }}</div>
                {%- endif -%}
                <div class="details">
                    <div class="reader typo-5">{{ review["reader"] }}</div>
                    {%- if review["device"] -%}
					<div class="device typo-6 color-flint">{{ review["device"] }}</div>
                    {%- endif -%}
                    {%- if review["dictionaries"] -%}
                    <div class="dictionary typo-6 color-flint"><i class="ph ph-books"></i> {{ review["dictionaries"] | join(", ") }}</div>
                    {%- endif -%}
                </div>
            </div>
        {% endfor %}
	</div>

	<div class="space-4"></div>

	<div id="buy" class="center">
		<h2 class="typo-4">One Price. Unlimited Dictionary Access.</h2>
		<div class="typo-6 color-flint">Select your languages, pay a one-time fee, and get unlimited access to evolving dictionaries with bi-monthly updates.</div>
	</div>
	<div class="space-1"></div>
	<div class="langs">
		<div class="left">
			<label for="lang-src" class="typo-4">Source language</label>
			<select id="lang-src" name="lang-src">
				<option value="all" title="Universal dictionary">All - Universal</option>
                {%- for lang_src in dictionaries if lang_src != "all" -%}
                    {%- set lang = language(lang_src) -%}
                    <option value="{{ lang_src }}" title="{{ "%s dictionary" % lang }}">{{ lang_src|upper }} - {{ lang }}</option>
                {%- endfor -%}
			</select>
		</div>
		<div class="right">
			<label for="lang-dst" class="typo-4">Destination language</label>
			<select id="lang-dst" name="lang-dst"></select>
		</div>
	</div>
    <div class="support">
        <div id="missing-pocket"><i class="ph-fill ph-warning"></i> PocketBook/Vivlio support via KOReader only.</div>
        <div id="missing-mobi"><i class="ph-fill ph-warning"></i> Kindle support via KOReader only.</div>
    </div>
	<div class="space-1"></div>
	<div class="purchase-card">
		<div class="title typo-4 center">Lifetime Access</div>
		<div class="description typo-6"><b>Instant download</b> & <b>lifetime updates</b> with a single link!</div>
		<div class="price center typo-4">{{ constants.PRICE_HTML }}</div>
		<div class="benefits">
			<div class="item">
				<div class="icon"><i class="ph ph-check"></i></div>
				<div class="info typo-6">Pay once, get instant download link</div>
			</div>
			<div class="item">
				<div class="icon"><i class="ph ph-check"></i></div>
				<div class="info typo-6">Bi-monthly updates & improvements</div>
			</div>
			<div class="item">
				<div class="icon"><i class="ph ph-check"></i></div>
				<div class="info typo-6">Priority support</div>
			</div>
			<div class="item">
				<div class="icon"><i class="ph-fill ph-credit-card"></i></div>
				<div class="info typo-6">Local and international payments accepted</div>
			</div>
			<div class="item">
				<div class="icon"><i class="ph-fill ph-lock"></i></div>
				<div class="info typo-6">Secure payment via Stripe</div>
			</div>
			<div class="item">
				<div class="icon"><i class="ph ph-book-open-text"></i></div>
				<div class="info typo-6">Contains <span id="words-count"></span> words</div>
			</div>
			<div class="item">
				<div class="icon"><i class="ph ph-download-simple"></i></div>
				<div class="info typo-6">Wiktionary data as of <span id="wiktionary-snapshot"></span></div>
			</div>
		</div>
		<a class="button" id="buy-link"><i class="ph-fill ph-stripe-logo"></i> Get Your Dictionary Now</a>
	</div>
	<div class="space-1"></div>
	<div class="monolingual">
		<div class="left">
			<div class="title typo-5"><label for="lang-mono">Or get a monolingual version for free</label></div>
		</div>
		<div class="right">
			<select id="lang-mono" name="lang-mono">
				<option disabled selected value>Choose language</option>
                {%- for lang_src in dictionaries if lang_src in dictionaries[lang_src] -%}
                    {%- set lang = language(lang_src) -%}
                    <option value="{{ lang_src }}" title="{{ "%s dictionary" % lang }}">{{ lang }}</option>
                {%- endfor -%}
			</select>
		</div>
	</div>

	<div class="space-4"></div>

	<div id="features" class="center">
		<h2 class="typo-4">Expand Your Language<br>Comprehension and Learning</h2>
		<div class="typo-6 color-flint">Whether you're reading literature, science, or poetry, our dictionaries unlock deep understanding through advanced features not found in standard built-ins.</div>
	</div>

	<div class="space-3"></div>

	<div class="tab">
		<div class="icons">
			<a class="unstyled icon active"><i class="ph ph-arrows-merge"></i></a>
			<a class="unstyled icon"><i class="ph ph-arrows-in-cardinal"></i></a>
			<a class="unstyled icon"><i class="ph ph-books"></i></a>
			<a class="unstyled icon"><i class="ph ph-text-superscript"></i></a>
			<a class="unstyled icon"><i class="ph ph-table"></i></a>
		</div>
	</div>
	<div class="space-2"></div>
	<div class="tab-content">
		<div class="active">
			<div class="typo-5">Singular forms from plurals</div>
			<div class="typo-6 color-flint">When selecting a plural word, its singular form is displayed.</div>
			<div class="example"><img width="486" height="428" loading="lazy" src="/asset/img/preview-singular.svg?v={{ version }}" alt="Loading preview …" title="Example of a plural word selected: its singular form is displayed." /></div>
		</div>
		<div>
			<div class="typo-5">Infinitive forms from conjugated verbs</div>
			<div class="typo-6 color-flint">When selecting a conjugated verb, the infinitive form is shown.</div>
			<div class="example"><img width="486" height="392" loading="lazy" src="/asset/img/preview-infinitive.svg?v={{ version }}" alt="Loading preview …" title="Example of a conjugated word selected: its infinitive form is displayed." /></div>
		</div>
		<div>
			<div class="typo-5">Multiple grammatical forms shown together</div>
			<div class="typo-6 color-flint">When a word is both a plural form and a verb form, all relevant versions are displayed.</div>
			<div class="example"><img width="486" height="376" loading="lazy" src="/asset/img/preview-multiple.svg?v={{ version }}" alt="Loading preview …" title="Example of a selected word that has multiple targets: all forms are shown." /></div>
		</div>
		<div>
			<div class="typo-5">Optimized rendering for scientific content</div>
			<div class="typo-6 color-flint">Mathematical, and chemical, formulas are beautifully rendered.</div>
			<div class="example"><img width="486" height="319" loading="lazy" src="/asset/img/preview-formula.svg?v={{ version }}" alt="Loading preview …" title="Example of a mathematical formula beautifully rendered." /></div>
		</div>
		<div>
			<div class="typo-5">Tables support</div>
			<div class="typo-6 color-flint">When a word entry includes any table, they are displayed correctly.</div>
			<div class="example"><img width="486" height="359" loading="lazy" src="/asset/img/preview-table.svg?v={{ version }}" alt="Loading preview …" title="Example of a mathematical formula beautifully rendered." /></div>
		</div>
	</div>

	<div class="space-4"></div>

	<h2 class="center typo-4">Do More With {{ constants.PROJECT }}</h2>
	<div class="space-1"></div>
	<div class="more">
		<div>
			<div class="icon"><i class="ph ph-link-simple"></i></div>
			<div class="right">
				<div class="title typo-5">Redirects are supported</div>
				<div class="description color-flint">Conjugated forms and variant spellings are redirected to their correct base entries — even when multiple levels deep.</div>
			</div>
		</div>
		<div>
			<div class="icon"><i class="ph ph-user-sound"></i></div>
			<div class="right">
				<div class="title typo-5">Multiple genders and pronunciations</div>
				<div class="description color-flint">If a word has more than one pronunciation or grammatical gender, all are displayed clearly.</div>
			</div>
		</div>
		<div>
			<div class="icon"><i class="ph ph-scribble-loop"></i></div>
			<div class="right">
				<div class="title typo-5">Hieroglyphs are supported</div>
				<div class="description color-flint">Ancient Egyptian characters are fully rendered when present in etymologies or word origins.</div>
			</div>
		</div>
		<div>
			<div class="icon"><i class="ph ph-toggle-right"></i></div>
			<div class="right">
				<div class="title typo-5">Etymology-free versions</div>
				<div class="description color-flint">Dictionaries are available in two flavors: one including etymologies, and one without — perfect for readers who want depth over clarity.</div>
			</div>
		</div>
	</div>

	<div class="space-3"></div>

	<div class="brands">
		<a href="https://read.amazon.com" target="_blank" rel="noopener noreferrer"><img width="134" height="29" loading="lazy" src="/asset/img/amazon-kindle.svg?v={{ version }}" alt="Amazon Kindle" title="Dictionaries for Amazon Kindle" /></a>
		<a href="https://www.kobo.com" target="_blank" rel="noopener noreferrer"><img width="82" height="23" loading="lazy" src="/asset/img/rakuten-kobo.svg?v={{ version }}" alt="Rakuten Kobo" title="Dictionaries for Rakuten Kobo" /></a>
		<a href="https://pocketbook.ch" target="_blank" rel="noopener noreferrer"><img width="136" height="21" loading="lazy" src="/asset/img/pocketbook.svg?v={{ version }}" alt="PocketBook" title="Dictionaries for PocketBook" /></a>
		<a href="https://www.vivlio.com" target="_blank" rel="noopener noreferrer"><img width="135" height="31" loading="lazy" src="/asset/img/vivlio.svg?v={{ version }}" alt="Vivlio" title="Dictionaries for Vivlio" /></a>
		<a href="https://www.boox.com" target="_blank" rel="noopener noreferrer"><img width="135" height="13" loading="lazy" src="/asset/img/onyx-boox.svg?v={{ version }}" alt="Onyx Boox" title="Dictionaries for Onyx Boox" /></a>
		<a href="https://koreader.rocks" target="_blank" rel="noopener noreferrer"><img width="90" height="29" loading="lazy" src="/asset/img/koreader.svg?v={{ version }}" alt="KOReader" title="Dictionaries for KOReader" /></a>
	</div>

	<div class="space-2"></div>

	<div class="compat typo-6">
		<div class="left color-flint">Compatible with Kindle, Kobo, KOReader, GoldenDict, and more.</div>
		<div class="right color-flint"><a href="#faq-supported-devices">View all compatibility →</a></div>
	</div>

	<div class="space-4"></div>

	<div id="showcase">
		<div class="large color-1">
			<div class="top-bar color-2">
				<div class="buttons">
					<div class="button color-3"></div>
					<div class="button color-3"></div>
					<div class="button color-3"></div>
				</div>
			</div>
			<div class="screen">
                <picture>
                    <source srcset="/asset/img/showcase-dark.png?v={{ version }}" media="(prefers-color-scheme: dark)">
                    <img src="/asset/img/showcase.png?v={{ version }}" loading="lazy" alt="Loading preview …"/>
                </picture>
			</div>
		</div>
		<div class="medium color-1">
			<div class="screen">
                <picture>
                    <source srcset="/asset/img/showcase-dark.png?v={{ version }}" media="(prefers-color-scheme: dark)">
                    <img src="/asset/img/showcase.png?v={{ version }}" loading="lazy" alt="Loading preview …"/>
                </picture>
				<div class="bottom-bar color-3"></div>
			</div>
		</div>
		<div class="small color-1">
			<div class="top-bar color-2">
                <div class="button color-3"></div>
            </div>
			<div class="screen">
                <picture>
                    <source srcset="/asset/img/showcase-dark.png?v={{ version }}" media="(prefers-color-scheme: dark)">
                    <img src="/asset/img/showcase.png?v={{ version }}" loading="lazy" alt="Loading preview …"/>
                </picture>
			</div>
			<div class="bottom-bar color-2"></div>
		</div>
	</div>

	<div class="space-4"></div>

	<h2 id="faq" class="center typo-4">Frequently Asked Questions</h2>
	<div class="space-1"></div>
	<div class="faq">
		{% for entry in faq_json["mainEntity"] %}
			<details name="exclusive" id="{{ entry['anchor'] }}"{% if loop.index0 == 0 %} open{% endif %}>
				<summary class="typo-5">{{ entry['name'] }}</summary>
				<article class="typo-6">
					<sup><a href="#{{ entry['anchor'] }}" title="Link to this FAQ entry"><i class="ph ph-anchor-simple"></i></a></sup> {{ entry['acceptedAnswer']['text'] }}
				</article>
			</details>
		{% endfor %}
		<div class="space-1"></div>
		<div class="center">
			<b>Still have questions?</b>
			<br>
			<br>
			<a class="button" href="mailto:contact@reader-dict.com">Contact our team</a>
		</div>
	</div>

	{# Google enriched result #}
	<script type="application/ld+json">{{ faq_json }}</script>
{%- endblock -%}

{%- block scripts -%}
    <script defer src="/asset/script/home.js?v={{ version }}"></script>
{%- endblock -%}
