{% extends "base.tpl" %}

{% block styles %}
    <link rel="stylesheet" href="/asset/style/home.css?v={{ version }}" />
{% endblock %}

{% block content %}

    <section id="dictionaries">
        <h2 class="section-title">{{ tr("home-dict-title") }}</h2>
        <p>{{ tr("home-dict-content-0") }}</p>
        <ul>
            <li>🔮</li>
                <li>{{ tr("home-dict-content--1") }}</li>
            {% for idx in range(1, 15) %}
                <li>{{ tr("home-dict-content-%d" % idx) }}</li>
            {% endfor %}
            <li>🧞</li>
        </ul>
    </section>

    <div class="space separator"></div>

    <section id="subscribe">
        <h2 class="section-title">{{ tr("home-sub-title") }}</h2>
        <div>
            <div>
                <form>
                    <div class="form-group">
                        <label for="lang-src">① {{ tr("home-sub-lang-src") }}</label>
                        <select id="lang-src" name="lang-src">
                            {% for lang_src in dictionaries %}
                                {% set lang = tr(lang_src) %}
                                <option value="{{ lang_src }}" title="{{ tr("dictionary-x", lang) }}">[{{ lang_src|upper }}] {{ lang }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="lang-dst">② {{ tr("home-sub-lang-dst") }}</label>
                        <select id="lang-dst" name="lang-dst"></select>
                        <span id="missing-mobi">{{ tr("no-kindle-support") }}</span>
                    </div>
                </form>
                <p>{{ tr("home-sub-metrics") }}<span id="this-is-monolingual"><br/>{{ tr("home-sub-monolingual") }}</span></p>
            </div>
            <div>
                <div class="paypal-buttons">
                    <p>③ {{ tr("home-sub-enjoy") }}</p>
                    <div class="subscribe">
                        <div id="paypal-button-subscription"></div>
                    </div>
                    <div class="or">&mdash; {{ tr("this_or_that") }} &mdash;</div>
                    <p>③ {{ tr("home-buy-enjoy") }}</p>
                    <div class="purchase">
                        <div id="paypal-button-purchase"></div>
                    </div>
                </div>
                <p>{{ tr("home-paypal-no-thanks") }}</p>
            </div>
        </div>
    </section>

    <div class="space separator"></div>
    
    <section id="about-me">
        <h2 class="section-title">{{ tr("home-about-title") }}</h2>
        <div class="profile-picture-wrapper">
            <img src="/asset/img/mickael-schoentgen.jpg" width="200" height="200" loading="lazy" alt="Profile Picture" class="profile-picture"/>
        </div>
        <div class="about-me-content">
            <p>{{ tr("home-about-content") }}</p>
            <div class="social-icon">
                {{ tr("home-connect") }} &nbsp;
                <a href="https://linkedin.com/in/mschoentgen" title="LinkedIn" target="_blank"><img src="/asset/img/linkedin.svg" width="32" height="32" loading="lazy" alt="LinkedIn"/></a>
                <a href="https://github.com/BoboTiG" title="GitHub" target="_blank"><img src="/asset/img/github.svg" width="32" height="32" loading="lazy" alt="GitHub"/></a>
            </div>
        </div>
    </section>
{% endblock %}

{% block scripts %}
    <script src="https://www.paypal.com/sdk/js?client-id={{ constants.PAYPAL_CLIENT_ID }}&components=buttons&currency=EUR&intent=subscription&vault=true" data-namespace="paypal_subscription"></script>
    <script src="https://www.paypal.com/sdk/js?client-id={{ constants.PAYPAL_CLIENT_ID }}&components=buttons&currency=EUR" data-namespace="paypal_purchase"></script>
    <script defer src="/asset/script/home.js?v={{ version }}"></script>
{% endblock %}
