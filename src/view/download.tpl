{% extends "base.tpl" %}

{% block styles %}
    <link rel="stylesheet" href="/asset/style/download.css?v={{ version }}" />
{% endblock %}

{% block content %}
    <div class="center typo-4">Your dictionary is ready</div>

	<div class="space-2"></div>

    {% set lang_src, lang_dst = dictionary["name"].split("-", 1) %}
    {% set name = language(lang_src) if lang_src == lang_dst else "%s - %s" % (language(lang_src), language(lang_dst)) %}
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
