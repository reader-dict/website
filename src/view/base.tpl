<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="author" content="Mickaël Schoentgen">
	<meta name="description" content="{{ description_full }}">
	<meta name="keywords" content="{{ tr("tags", constants.KEYWORDS) }}">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">

	<meta property="og:description" content="{{ description_full }}">
	<meta property="og:image" content="/asset/img/favicon.svg">
	<meta property="og:locale" content="en_EN">
	<meta property="og:site_name" content="{{ constants.PROJECT }}">
	<meta property="og:title" content="{{ constants.PROJECT }} — {{ description }}">
	<meta property="og:type" content="website">
	<meta property="og:url" content="{{ url_pure }}">

	<meta name="twitter:card" content="summary_large_image">
	<meta name="twitter:title" content="{{ constants.PROJECT }} — {{ description }}">
	<meta name="twitter:description" content="{{ description_full }}">
	<meta name="twitter:image" content="/asset/img/favicon.svg">
	<meta property="twitter:domain" content="{{ constants.WWW }}">
	<meta property="twitter:url" content="{{ url_pure }}">

	<link rel="author" href="/humans.txt" />
	<link rel="canonical" href="{{ url_pure }}">
	<link rel="icon" href="/asset/img/favicon.svg">
	<link rel="publisher" href="https://www.{{ constants.WWW }}" />
	<link rel="stylesheet" href="/asset/style/common.css?v={{ version }}" />
	{%- block styles -%}{%- endblock %}
	<title>{{ constants.PROJECT }} - {{ title }}</title>
</head>
<body>
	<header>
		<h1><img src="/asset/img/logo-reader-dict.svg" width="32" height="32" loading="lazy" alt="Logo"/>{{ constants.PROJECT }}</h1>
		<p>{{ tr("header-slogan-pretty") }}</p>
	</header>
	<div class="space"></div>
	<div class="content">{% block content required %} {% endblock %}</div>
	<div class="space"></div>
	<footer>
		<p>
			&copy;&nbsp;{{ year }} {{ constants.PROJECT }}
			<br/>
			<a href="{{ constants.GITHUB_URL_TRACKER }}" target="_blank">{{ tr("bug-tracker") }}</a>
			&nbsp;•&nbsp;
			<a href="mailto:contact@reader-dict.com">{{ tr("contact") }}</a>
		</p>
	</footer>
	{%- block scripts -%} {%- endblock -%}
	{%- if not debug -%}
		<script src="https://browser.sentry-cdn.com/9.22.0/bundle.min.js" crossorigin="anonymous"></script>
		<script>
			Sentry.init({
				dsn: "{{ constants.SENTRY_DSN_FRONTEND }}",
				environment: "{{ sentry_environment }}",
				release: "{{ sentry_release }}",
			});
		</script>
		<script>
			var _paq = window._paq = window._paq || [];
			_paq.push(["setDomains", ["*.www.reader-dict.com/metrics"]]);
			_paq.push(['trackPageView']);
			_paq.push(['enableLinkTracking']);
			(function() {const u="//www.{{ constants.WWW }}/metrics/";_paq.push(['setTrackerUrl', u+'matomo.php']);_paq.push(['setSiteId', '1']);var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];g.async=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);})();
		</script>
		<noscript><p><img referrerpolicy="no-referrer-when-downgrade" src="//www.reader-dict.com/metrics/matomo.php?idsite=1&rec=1" style="border:0;" alt="" /></p></noscript>
	{%- endif -%}
	</body>
</html>
