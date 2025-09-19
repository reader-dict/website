{% extends "base.tpl" %}

{% block content %}
    {% set lang_src, lang_dst = dictionary["name"].split("-", 1) %}
    {% set name = language(lang_src) if lang_src == lang_dst else "%s - %s" % (language(lang_src), language(lang_dst)) %}

    <h1 class="center typo-4">{{ name }} Dictionary</h1>

	<div class="space-1"></div>

    <p class="typo-6">
        {{ "Updated on <span class='color-flint'>{0}</span>: our <b>{1}</b> dictionary now contains {2:,}&nbsp;words.".format(last_updated, name, dictionary["words"]) }}
        <br>
        <br>
        Discover <a class="underline" href="/#features">powerful features</a> and explore <a class="underline" href="/#see-it-in-action">see the dictionary in action on multiple devices</a>.
        <br>
        Find answers to your questions in our comprehensive <a class="underline" href="/#faq">FAQ</a>, including supported devices and apps.
        <br>
        <br>
        Join the <a class="underline" href="/#reviews"><b>reader.dict</b> community</a> and get your premium <b>{{ name }}</b> dictionary today!
    </p>
    <p class="center"><a class="button" href="/#{{ dictionary['name'] }}">Get Your <b>{{ name }}</b> Dictionary Now</a></p>

    <div class="space-1"></div>

{% endblock %}
