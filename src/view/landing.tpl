{% extends "base.tpl" %}

{% block content %}
    {% set lang_src, lang_dst = dictionary["name"].split("-", 1) %}
    {% set name = language(lang_src) if lang_src == lang_dst else "%s - %s" % (language(lang_src), language(lang_dst)) %}

    <h1 class="center typo-4">{{ name }} Dictionary</h1>

	<div class="space-1"></div>

    <p class="typo-6">
        {{ "Updated on <span class='color-flint'>{0}</span>, the <b>{1}</b> dictionary contains {2:,}&nbsp;words.".format(last_updated, name, dictionary["words"]) }}
        <br>
        <br>
        Curious about what <a href="/#features">awesome features</a> this dictionary has, and maybe do you want to see <a href="/#showcase">screenshots</a>?
        <br>
        There is also a comprehensive <a href="/#faq">Frequently Asked Questions</a> section where you will discover supported devices & apps.
        <br>
        <br>
        Become <a href="/#reviews">part of <b>reader.dict</b> the community</a>, and go get your great <b>{{ name }}</b> dictionary.
    </p>
    <p class="center"><a class="button" href="/#{{ dictionary['name'] }}">Get Your <b>{{ name }}</b> Dictionary Now</a></p>

    <div class="space-1"></div>

{% endblock %}
