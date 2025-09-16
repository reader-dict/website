{%- extends "base.tpl" -%}

{% block styles %}
	<link rel="preload" href="/asset/style/sponsor.css?v={{ version }}" as="style" onload="this.onload=null;this.rel='stylesheet'">
	<noscript><link rel="stylesheet" href="/asset/style/sponsor.css?v={{ version }}" /></noscript>
{% endblock %}

{%- block content -%}
	<div class="center typo-4">Sponsors</div>

	<div class="space-2"></div>

	{%- for tiers, data in sponsors.items() if data -%}
		<div id="{{ tiers }}" class="typo-5">{{ tiers | title }}</div>
		<div class="space-1"></div>
		<div class="names">
			{%- for name, url, amount in data -%}
				<span{% if debug %} title="€{{ amount | int }}"{% endif %}>
				{%- if tiers != "gold" and url -%}
				<a href="{{ url }}" target="_blank" class="external">{{ name }}</a></span>
				{%- else -%}
				{{ name }}
				{%- endif -%}
				</span>
			{%- endfor -%}
		</div>
		<div class="space-2"></div>
	{%- endfor -%}
{%- endblock -%}
