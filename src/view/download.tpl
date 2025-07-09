{% extends "base.tpl" %}

{% block styles %}
    <link rel="stylesheet" href="/asset/style/download.css?v={{ version }}" />
{% endblock %}

{% block content %}
    <section>
        <h2 class="section-title">{{ tr("download-title", name) }}</h2>
        <p>
            {% if kind == "bilingual" %}
                {% if not order.is_purchase and order.status != "active" %}
                    <div class="subscription-countdown">{{ tr("subscription-countdown", '<span id="subscription-end" data-end="{0}"></span>'.format(order.status_update_time)) }}</div>
                {% endif %}
                <p>{{ tr("download-expire") }}</p>
            {% else %}
                {{ tr("download-support", "/#%s" % (dictionary["name"])) }}
            {% endif %}
        </p>
        <div class="downloads">
            <p>{{ tr("download-metrics", dictionary["updated"], dictionary["name"]|upper, dictionary["words"]) }}</p>
            <dl>
            {% for fmt, (pretty_fmt, file_name_full, file_name_noetym, link_full, link_noetym) in links.items() %}
                <dt>{{ pretty_fmt }}</dt>
                <dd>
                    <div>{{ tr("download-full")}} <a href="/file/{{ link_full }}">{{ file_name_full }} <img src="/asset/img/download.svg" width="18" height="18" loading="lazy" alt="{{ tr("download") }}"/></a></div>
                    <div>{{ tr("download-etym-free")}} <a href="/file/{{ link_noetym }}">{{ file_name_noetym }} <img src="/asset/img/download.svg" width="20" height="20" loading="lazy" alt="{{ tr("download") }}"/></a></div>
                    {%- if fmt in ("kobo", "mobi") -%}
                    <div><a href="/faq#howto-install-{{ fmt }}" target="_blank">{{ tr("download-howto") }}</a></div>
                    {% endif %}
                </dd>
            {% endfor %}
            </dl>
        </div>
    </section>
{% endblock %}

{% block scripts %}
    <script defer src="/asset/script/download.js?v={{ version }}"></script>
{% endblock %}
