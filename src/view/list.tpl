{%- extends "base.tpl" -%}

{%- block content -%}
	<div class="center typo-4">The dictionaries list</div>

	<div class="space-2"></div>

	<div id="universal" class="typo-5">Universal</div>
	<ol>
		{%- for lang_dst in dictionaries["all"] -%}
			<li><a href="/#all-{{ lang_dst }}" class="unstyled">{{ "Universal <b>%s</b> dictionary" % language(lang_dst) }}</a></li>
		{%- endfor -%}
	</ol>
	
	<div class="space-2"></div>
	
	<div id="bilingual" class="typo-5">Bilingual</div>
	<ol>
		{%- for lang_src in dictionaries if lang_src != "all" -%}
			<div id="{{ lang_src }}" class="typo-6 color-flint"><a href="#{{ lang_src }}">{{ lang_src|upper }}</a> - {{ language(lang_src) }}</div>
			{%- for lang_dst in dictionaries[lang_src] if lang_src != lang_dst -%}
				<li><a href="/#{{ lang_src }}-{{ lang_dst }}" class="unstyled">{{ "Bilingual <b>%s - %s</b> dictionary" % (language(lang_src), language(lang_dst)) }}</a></li>
			{%- endfor -%}
		<div class="space-1"></div>
		{%- endfor -%}
	</ol>
	
	<div class="space-2"></div>
	
	<div id="monolingual" class="typo-5">Monolingual</div>
	<ol>
		{%- for lang_src in dictionaries if lang_src in dictionaries[lang_src] -%}
			<li><a href="/download/{{ lang_src }}" class="unstyled">{{ "Monolingual <b>%s</b> dictionary" % language(lang_src) }}</a></li>
		{%- endfor -%}
	</ol>
{%- endblock -%}
