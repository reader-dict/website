{%- extends "base.tpl" -%}

{%- block content -%}
	<h1 class="center typo-4">The Dictionaries List</h1>

	<div class="space-1"></div>

	<h2 id="bilingual" class="typo-5">Bilingual</h2>
	<ol>
		{%- for lang_src in dictionaries if lang_src != "all" -%}
			<div id="{{ lang_src }}" class="typo-6 color-flint"><a href="#{{ lang_src }}">{{ lang_src|upper }}</a> - {{ language(lang_src) }}</div>
			{%- for lang_dst in dictionaries[lang_src] if lang_src != lang_dst -%}
				<li><a href="/#{{ lang_src }}-{{ lang_dst }}">{{ "Bilingual <b>%s - %s</b> dictionary" % (language(lang_src), language(lang_dst)) }}</a></li>
			{%- endfor -%}
		<div class="space-1"></div>
		{%- endfor -%}
	</ol>

	<h2 id="universal" class="typo-5">Universal</h2>
	<ol>
		{%- for lang_dst in dictionaries["all"] -%}
			<li><a href="/#all-{{ lang_dst }}">{{ "Universal <b>%s</b> dictionary" % language(lang_dst) }}</a></li>
		{%- endfor -%}
	</ol>

	<h2 class="space-1"></h2>

	<div id="monolingual" class="typo-5">Monolingual</div>
	<ol>
		{%- for lang_src in dictionaries if lang_src in dictionaries[lang_src] -%}
			<li><a href="/download/{{ lang_src }}">{{ "Monolingual <b>%s</b> dictionary" % language(lang_src) }}</a></li>
		{%- endfor -%}
	</ol>
{%- endblock -%}
