{% extends "manager/templates/base.tpl" %}

{% block title %}DASHBOARD PAGE{% endblock %}

{% block content %}
DASHBOARD PAGE
<table class="dashboard">
    <tr>
        <td class="stats">
        </td>
        <td class="sitemap">
            <div class="help">After all the changes we recommend to update your sitemap.</div>
            <div>
                <input type="button" class="form-submit" name="sitemap" value="Update sitemap" />
                <div class="waiting"></div>
            </div>
        </td>
    </tr>
</table>
{% endblock %}