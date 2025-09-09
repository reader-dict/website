<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="author" content="Mickaël Schoentgen — {{ constants.PROJECT }}">
	<meta name="description" content="{{ constants.HEADER_DESC }}">
	<meta name="keywords" content="bilingual dictionary,universal dictionary,monolingual dictionary,e-reader dictionary,ebook dictionary,
	dictionary,dictionaries,wiktionary,kobo,kindle,onyx boox,pocketbook,dict.org,dictorg,dictfile,dicthtml,mobi,stardict,koreader,goldendict,plato,colordict,flowdict,bookeen,cybook,odissey">
	<meta name="viewport" content="width=device-width">

	<meta property="og:description" content="{{ constants.HEADER_DESC }}">
	<meta property="og:image" content="/asset/img/favicon.svg">
	<meta property="og:locale" content="en_EN">
	<meta property="og:site_name" content="{{ constants.PROJECT }}">
	<meta property="og:title" content="{{ constants.PROJECT }} — {{ constants.HEADER_DESC }}">
	<meta property="og:type" content="website">
	<meta property="og:url" content="{{ url_pure }}">

	<meta name="twitter:card" content="summary_large_image">
	<meta name="twitter:title" content="{{ constants.PROJECT }} — {{ constants.HEADER_DESC }}">
	<meta name="twitter:description" content="{{ constants.HEADER_DESC }}">
	<meta name="twitter:image" content="/asset/img/favicon.svg">
	<meta property="twitter:domain" content="{{ constants.WWW }}">
	<meta property="twitter:url" content="{{ url_pure }}">

	<link rel="author" href="/humans.txt" />
	<link rel="canonical" href="{{ url_pure }}">
	<link rel="icon" href="/asset/img/favicon.svg">
	<link rel="publisher" href="https://www.{{ constants.WWW }}" />
	<link rel="stylesheet" href="/asset/style/common.css?v={{ version }}" />
	{%- block styles -%}{%- endblock -%}
	<title>{{ constants.PROJECT }} - {{ title }}</title>
</head>
<body>
	<header>
		<div class="brand">
			<a href="/" title="Back to home">
				<picture>
					<source srcset="/asset/img/header-logo-negative.svg?v={{ version }}" media="(prefers-color-scheme: dark)">
					<img src="/asset/img/header-logo.svg?v={{ version }}" width="529" height="126" loading="lazy" alt="{{ constants.PROJECT }}"/>
				</picture>
			</a>
		</div>
		<div class="get-yours"><a class="button" href="/#buy">Get yours</a></div>
	</header>

	<div class="space-2"></div>
	{%- block content -%}{%- endblock -%}
	<div class="space-5"></div>

	<footer>
		<div class="line-top">
			<div class="left">
				<a class="unstyled" href="{{ constants.GOOGLE_REVIEWS }}" target="_blank">Post a review</a>
				&nbsp;&nbsp;&nbsp;&nbsp;
				<a class="unstyled" href="/list">Full list</a>
				&nbsp;&nbsp;&nbsp;&nbsp;
				<a class="unstyled" href="mailto:contact@reader-dict.com">Contact</a>
			</div>
			<div class="right">
				<a class="unstyled" href="{{ constants.GITHUB_URL }}" target="_blank">GitHub</a>
			</div>
		</div>
		<div class="space-1"></div>
		<div class="separator"></div>
		<div class="space-1"></div>
		<div>&copy; 2020-{{ year }} <span>{{ constants.PROJECT }}</span>. All Rigths Reserved.</div>
	</footer>
	{%- block scripts -%}{%- endblock -%}
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
