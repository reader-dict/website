{% extends "base.tpl" %}

{% block content %}
    <section>
        <h2 class="section-title">{{ tr("error-title") }}</h2>
        <p style="font-size: 1.2em">{{ tr("error-%s" % error) }}</p>
        <p>{{ tr("error-back-home") }}</p>
    </section>
{% endblock %}
