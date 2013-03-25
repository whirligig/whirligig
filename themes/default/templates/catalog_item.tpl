{% extends "base.tpl" %}

{% block title %}CATALOG PAGE{% endblock %}

{% block extra_head %}
<link href="/static/pirobox/style.css" rel="stylesheet" type="text/css" />
  <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.0/jquery.min.js"></script>
  <script type="text/javascript" src="/static/pirobox/pirobox.js"></script>
  <script type="text/javascript">
    $(document).ready(function() {
      $.piroBox_ext({
        piro_speed :700,
        bg_alpha : 0.9,
        gb_color : '#000',
        piro_scroll : true,
        piro_drag :false,
        piro_nav_pos: 'bottom'
      });
    });
  </script>
{% endblock %}

{% block content %}
<table class="item_table">
    <tr>
        <td class="item_images">
        <div class="wrap block">
            <div class="main">
                <a href="{{ item|main_image|get_original_image }}" rel="gallery"  class="pirobox_gall" title="">
                    <img src="{{ item|main_image|get_small_image }}" alt="" title="" />
                </a>
            </div>
            {% if item|extra_images|length %}
            <div class="extra block">
                {% for image in item|extra_images %}
                <div class="frame">
                    <div class="crop">
                        <a href="{{ image|get_big_image }}" rel="gallery"  class="pirobox_gall" title="">
                            <img src="{{ image|get_mini_image }}" alt="" title="" />
                        </a>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </div>
        </td>
        <td class="item_info">
        {% if item|length %}
        <table>
        {% for field in item|custom_fields %}
                <tr><td class="item_field_name">{{ field.0 }}:</td><td class="item_field_value">{{ field.1 }}</td></tr>
        {% endfor %}
        </table>
        {% endif %}
        </td>
    </tr>
</table>

{% endblock %}