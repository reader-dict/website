{%- extends "base.tpl" -%}

{%- block styles -%}
    <link rel="stylesheet" href="/asset/style/home.css?v={{ version }}" />
{%- endblock -%}

{%- block content -%}
	<div class="center">
		<div class="typo-4">Understand every word,<br>anywhere, anytime</div>
		<div class="space-1"></div>
		<div class="typo-6">Massive word coverage. Flawless inflection support. High compatibility across devices.</div>
		<div class="space-1"></div>
		<div class="get-yours"><a class="button" href="/#buy">Get yours</a></div>
    </div>

	<div class="space-3"></div>

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

	<div class="space-3"></div>

	<div class="brands">
		<a href="https://read.amazon.com" target="_blank"><img width="134" height="29" loading="lazy" src="/asset/img/amazon-kindle.svg?v={{ version }}" alt="Amazon Kindle" title="Dictionaries for Amazon Kindle" /></a>
		<a href="https://www.kobo.com" target="_blank"><img width="82" height="23" loading="lazy" src="/asset/img/rakuten-kobo.svg?v={{ version }}" alt="Rakuten Kobo" title="Dictionaries for Rakuten Kobo" /></a>
		<a href="https://pocketbook.ch" target="_blank"><img width="136" height="21" loading="lazy" src="/asset/img/pocketbook.svg?v={{ version }}" alt="PocketBook" title="Dictionaries for PocketBook" /></a>
		<a href="https://www.vivlio.com" target="_blank"><img width="135" height="31" loading="lazy" src="/asset/img/vivlio.svg?v={{ version }}" alt="Vivlio" title="Dictionaries for Vivlio" /></a>
		<a href="https://www.boox.com" target="_blank"><img width="135" height="13" loading="lazy" src="/asset/img/onyx-boox.svg?v={{ version }}" alt="Onyx Boox" title="Dictionaries for Onyx Boox" /></a>
		<a href="https://koreader.rocks" target="_blank"><img width="90" height="29" loading="lazy" src="/asset/img/koreader.svg?v={{ version }}" alt="KOReader" title="Dictionaries for KOReader" /></a>
	</div>

	<div class="space-2"></div>

	<div class="compat typo-6">
		<div class="left">Compatible with Kindle, Kobo, KOReader, GoldenDict, and more.</div>
		<div class="right"><a href="#faq-supported-devices" class="unstyled">View all compatibility →</a></div>
	</div>

	<div class="space-5"></div>

	<div id="features" class="center">
		<div class="typo-4">Expand your language<br>comprehension and learning</div>
		<br>
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

	<div class="space-5"></div>

	<div class="center typo-4">Do more with {{ constants.PROJECT }}</div>
	<div class="space-2"></div>
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

	<div class="space-5"></div>

	<div id="buy" class="center">
		<div class="typo-4">Simple pricing to suit your needs</div>
		<br>
		<div class="typo-6 color-flint">Choose your source language and select a destination, the price is unique and you'll have a lifetime access to updates.</div>
	</div>
	<div class="space-1"></div>
	<div class="langs">
		<div class="left">
			<label class="typo-4">Source language</label>
			<select id="lang-src" name="lang-src">
				<option value="all" title="Universal dictionary">All - Universal</option>
                {%- for lang_src in dictionaries if lang_src != "all" -%}
                    {%- set lang = language(lang_src) -%}
                    <option value="{{ lang_src }}" title="{{ "%s dictionary" % lang }}">{{ lang_src|upper }} - {{ lang }}</option>
                {%- endfor -%}
			</select>
		</div>
		<div class="right">
			<label class="typo-4">Destination language</label>
			<select id="lang-dst" name="lang-dst"></select>
		</div>
	</div>
    <div class="support">
        <div id="missing-mobi"><i class="ph-fill ph-warning"></i> Kindle support via KOReader only.</div>
        <div id="missing-pocket"><i class="ph-fill ph-warning"></i> PocketBook/Vivlio support via KOReader only.</div>
    </div>
	<div class="space-1"></div>
	<div class="purchase-card">
		<div class="title typo-4">One-time licence</div>
		<div class="description typo-6">Bi-monthly updates, improvements, and evolving word coverage.</div>
		<div class="price typo-4">€{{ constants.PRICE_UNIQUE }}</div>
		<div class="benefits">
			<div class="item">
				<div class="icon"><i class="ph ph-check"></i></div>
				<div class="info typo-6">Unlimited access to latest version</div>
			</div>
			<div class="item">
				<div class="icon"><i class="ph ph-check"></i></div>
				<div class="info typo-6">Bi-monthly updates and improvements</div>
			</div>
			<div class="item">
				<div class="icon"><i class="ph ph-check"></i></div>
				<div class="info typo-6">High priority support response time</div>
			</div>
			<div class="item">
				<div class="icon"><i class="ph ph-book-open-text"></i></div>
				<div class="info typo-6">Words count: <span id="words-count"></span></div>
			</div>
			<div class="item">
				<div class="icon"><i class="ph ph-download-simple"></i></div>
				<div class="info typo-6">Wiktionary export: <span id="wiktionary-snapshot"></span></div>
			</div>
		</div>
		<a class="button" id="buy-link" data-cid="{{ client_id }}" data-url="{{ constants.BUY_URL }}">Buy now</a>
	</div>

	<div class="space-1"></div>

	<div class="monolingual">
		<div class="left">
			<div class="title typo-5">Or get a monolingual version for free</div>
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

	<div class="space-5"></div>

	<div id="reviews" class="center">
		<div class="typo-4">Trusted by curious readers everywhere</div>
		<br>
		<div class="typo-6 color-flint">What savvy readers across platforms are saying about our dictionaries.</div>
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
                    <div class="device typo-6">{{ review["device"] }}</div>
                    <div class="dictionary typo-6">{{ review["dictionaries"] | join(", ") }}</div>
                </div>
            </div>
        {% endfor %}
	</div>

	<div class="space-5"></div>

	<div id="faq" class="center typo-4">Frequently asked questions</div>
	<div class="space-2"></div>
	<div class="faq">
		<details name="exclusive" id="faq-supported-devices" open>
			<summary class="typo-5">Which devices are supported?</summary>
			<article class="typo-6"><sup><a href="#faq-supported-devices" title="Link to this FAQ entry"><i class="ph ph-anchor-simple"></i></a></sup> Kobo, Kindle, Pocketbook, Vivlio, Onyx Boox, Bookeen Cybook Odissey, and many more … A wide range of applications are also supported like KOReader, GoldenDict, Plato, ColorDict, FlowDict; you name it.</article>
		</details>
		<details name="exclusive" id="faq-support-pocketbook-vivlio">
			<summary class="typo-5">What about native support for Pocketbook/Vivlio devices?</summary>
			<article class="typo-6"><sup><a href="#faq-support-pocketbook-vivlio" title="Link to this FAQ entry"><i class="ph ph-anchor-simple"></i></a></sup> Creating dictionaries for these devices is not feasible with the current knowledge/tools shared on the Internet. So far, we haven't had a chance to get any answers at all from PocketBook nor Vivlio. You can repost <a href="https://x.com/__tiger222__/status/1921036630648934492" target="_blank" class="external">this tweet</a> to ping them, or better, open a support ticket asking for knowledge sharing (point them to this website).</article>
		</details>
		<details name="exclusive" id="faq-available-files">
			<summary class="typo-5">Which file formats are provided?</summary>
			<article class="typo-6"><sup><a href="#faq-available-files" title="Link to this FAQ entry"><i class="ph ph-anchor-simple"></i></a></sup> DICT.org, DictFile, DictHTML (for Kobo), MobiPocket (for Kindle), and StarDict (for KOReader, and a wide range of applications).</article>
		</details>
		<details name="exclusive" id="faq-howto-install-kobo">
			<summary class="typo-5">How to install on Kobo?</summary>
			<article class="typo-6"><sup><a href="#faq-howto-install-kobo" title="Link to this FAQ entry"><i class="ph ph-anchor-simple"></i></a></sup> Copy the compressed dictionary file (<code>dicthtml-XX-YY.zip</code>) inside the <code>.kobo/custom-dict/</code> folder on your Kobo. Do not decompress it.</article>
		</details>
		<details name="exclusive" id="faq-howto-install-mobi">
			<summary class="typo-5">How to install on Kindle?</summary>
			<article class="typo-6"><sup><a href="#faq-howto-install-mobi" title="Link to this FAQ entry"><i class="ph ph-anchor-simple"></i></a></sup> Decompress the dictionary file (<code>dict-XX-YY.mobi.zip</code>), and copy the resulting <code>dict-XX-YY.mobi</code> file inside the <code>documents/dictionaries/</code> folder on your Kindle.</article>
		</details>
		<details name="exclusive" id="faq-howto-install-koreader">
			<summary class="typo-5">How to install on KOReader?</summary>
			<article class="typo-6">
				<sup><a href="#faq-howto-install-koreader" title="Link to this FAQ entry"><i class="ph ph-anchor-simple"></i></a></sup> Download a dictionary in the <code>StarDict</code> format (<code>dict-XX-YY.zip</code>), decompress it, and copy resulting files (<code>dict-data.dict.dz</code>, <code>dict-data.idx</code>, <code>dict-data.ifo</code>, and <code>dict-data.syn</code> when present) inside a <code>dict-XX-YY</code> sub-folder at the appropriate location on your device:
				<ul>
					<li>Android: <code>/sdcard/koreader/data/dict</code></li>
					<li>Cervantes: <code>/mnt/private/koreader/data/dict/</code></li>
					<li>Kindle: <code>koreader/data/dict/</code></li>
					<li>Kobo: <code>.adds/koreader/data/dict/</code></li>
					<li>PocketBook & Vivlio: <code>applications/koreader/data/dict/</code></li>
					<li>Linux: <code>$HOME/.config/koreader/data/dict/</code></li>
					<li>macOS: <code>$HOME/Library/Application Support/koreader/data/dict/</code></li>
				</ul>
            </article>
		</details>
		<details name="exclusive" id="faq-refund">
			<summary class="typo-5">What's the refund politic?</summary>
			<article class="typo-6"><sup><a href="#faq-refund" title="Link to this FAQ entry"><i class="ph ph-anchor-simple"></i></a></sup> A refund is possible on the sole condition that no file was downloaded. Logs are kept on the server side, and will be used to resolve any disputes.</article>
		</details>
		<details name="exclusive" id="faq-groups">
			<summary class="typo-5">What about group and promotions?</summary>
			<article class="typo-6"><sup><a href="#faq-groups" title="Link to this FAQ entry"><i class="ph ph-anchor-simple"></i></a></sup> Are you an institution, a teacher, or do you simply want to buy several copies? Would you like to offer coupons to your users? Get in touch!</article>
		</details>
	</div>
{%- endblock -%}

{%- block scripts -%}
    <script defer src="/asset/script/home.js?v={{ version }}"></script>
{%- endblock -%}
