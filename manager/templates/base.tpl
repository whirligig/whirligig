<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <title>{% block title %}{% endblock %}</title>

  <link href='http://fonts.googleapis.com/css?family=PT+Sans&subset=latin,cyrillic' rel='stylesheet' type='text/css'>
  <link rel="stylesheet" type="text/css" href="{{ MANAGER_URL }}static/commons.css" media="all" />
  <link rel="stylesheet" type="text/css" href="{{ MANAGER_URL }}static/manager.css" media="all" />
  <link rel="stylesheet" type="text/css" href="{{ MANAGER_URL }}static/jquery.wysiwyg.css" media="all" />
  <link rel="stylesheet" type="text/css" href="{{ MANAGER_URL }}static/jquery.ui.all.css" media="all" />

  <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.0/jquery.min.js"></script>
  <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.23/jquery-ui.js"></script>
{% block extra_head %}{% endblock %}
  <script type="text/javascript" src="{{ MANAGER_URL }}static/jquery.json.js"></script>
  <script type="text/javascript" src="{{ MANAGER_URL }}static/jquery.color.js"></script>
  <script type="text/javascript" src="{{ MANAGER_URL }}static/jquery.form.js"></script>
  <script type="text/javascript" src="{{ MANAGER_URL }}static/jquery.wysiwyg.js"></script>
  <script type="text/javascript" src="{{ MANAGER_URL }}static/jquery.combobox.js"></script>
  <script type="text/javascript" src="{{ MANAGER_URL }}static/manager.js"></script>
</head>

<body>
  <div id="container">
    <div id="header" class="block">
      <span id="site_title">{{ SITENAME }}</span>
      <span id="manager_title"><a href="{{ MANAGER_URL }}">Manager panel</a></span>
      {% if is_auth(request) %}<div id="manager-nav">{{ manager_nav(request) }}</div>{% endif %}
    </div>
    <div id="content" class="clearfix">
      <div id="notificator"></div>
      {% block content %}{% endblock %}
    </div>
  </div>
  <footer>
    <div id="develop-date">2013</div>
  </footer>
  <div id="overlay" class="hide"></div>
</body>
</html>