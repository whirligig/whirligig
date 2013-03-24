<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <meta name="description" content="{{ SITEDESC }}">
  <meta name="keywords" content="{{ KEYWORDS }}">
  <title>{% block title %}{% endblock %} {% if SITEDESC_SHORT %} - {{ SITEDESC_SHORT }}{% endif %}</title>
  <link rel="stylesheet" type="text/css" href="/static/{{ THEME }}/style.css" media="all" />
  <link rel="stylesheet" type="text/css" href="/static/commons.css" media="all" />

  {% block extra_head %}{% endblock %}
</head>

<body>
  <div id="container" class="block">
    <div id="wrapper" class="block">
      <div class="header block">
        <div class="sitename left"><h1><a href="/">{{ SITENAME }}</a></h1></div>
        <div class="block right">{{ print_menu('main',REQUEST) }}</div>
      </div>
      
      <div id="content" class="block">{% block content %}{% endblock %}</div>
    </div>
  </div>
  <div class="footer block">
    <div class="block center">{{ print_menu('bottom') }}</div>
    <div id="signature">FOOTER</div>
  </div>

<div id="overlay" class="hide"></div>
</body>
</html>