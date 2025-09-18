{% extends "base.tpl" %}

{% block styles %}
	<link rel="preload" href="/asset/style/download.css?v={{ version }}" as="style" onload="this.onload=null;this.rel='stylesheet'">
	<noscript><link rel="stylesheet" href="/asset/style/download.css?v={{ version }}" /></noscript>
{% endblock %}

{% block content %}
    {% set lang_src, lang_dst = dictionary["name"].split("-", 1) %}
    {% set name = language(lang_src) if lang_src == lang_dst else "%s - %s" % (language(lang_src), language(lang_dst)) %}

    <h1 class="center typo-4">{{ name }} Dictionary</h1>

	<div class="space-1"></div>

    {%- if lang_src == lang_dst -%}
    <p class="typo-6">We know you're enjoying this wonderful dictionary. Show your support with a <a href="https://donate.stripe.com/9B600j2cheU905LdaE2cg01" target="_blank">donation</a>.</p>
    <div class="space-1"></div>
    {%- endif -%}

    <p class="typo-6">{{ "Updated on <span class='color-flint'>{0}</span>, the <b>{1}</b> dictionary contains {2:,}&nbsp;words.".format(last_updated, name, dictionary["words"]) }}</p>

    <div class="space-1"></div>

    <dl>
    {% for fmt, (pretty_fmt, file_name_full, file_name_noetym, link_full, link_noetym) in links.items() %}
        <dt class="typo-5">{{ pretty_fmt }}</dt>
        <dd>
            <div class="color-flint">Full version: <a class="unstyled" href="/file/{{ link_full }}" title="Download">{{ file_name_full }} <i class="ph ph-download-simple"></i></a></div>
            <div class="color-flint">Etymology-free version: <a class="unstyled" href="/file/{{ link_noetym }}" title="Download">{{ file_name_noetym }} <i class="ph ph-download-simple"></i></a></div>
            {%- if fmt in ("kobo", "mobi") -%}
            <div><i class="ph ph-book-open-text"></i> <a class="unstyled" href="/#faq-howto-install-{{ fmt }}" target="_blank">How to install?</a></div>
            {% endif %}
        </dd>
        <div class="space-1"></div>
    {% endfor %}
    </dl>
{% endblock %}
