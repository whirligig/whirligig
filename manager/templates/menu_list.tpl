{% if items|length %}
{% for menu in items %}
<div class="menu">
	<div class="menu_title">{{ menu }}</div>
	<ul class="menu-list">
		{% for i in items.menu %}
		<li>
			<div class="block nav_head">{{ i.2 }} <div class="nav_meta">[<span class="edit">edit</span>] <span class="remove">&#10006;</span></div></div>
			<div class="nav_edit">
				<table>
					<tr><td colspan="2" class="msg"></td></tr>
					<tr><th>Menu name</th><td>
						<input class="edit_pk" type="hidden" name="edit_pk" value="{{ i.0 }}" />
						<select class="form-text edit_menu" name="edit_menu">
							{% for menu in menu_list %}<option value="{{ menu.0 }}" {% if menu.0 == i.5 %}selected{% endif %}>{{ menu.1 }}</option>{% endfor %}
						</select>
					</td></tr>
					<tr><th>Title</th><td><input class="form-text edit_title" type="text" name="edit_title" value="{{ i.2 }}" /></td></tr>
					<tr><th>URL</th><td>
						<select class="edit_url" name="edit_url">
							{% for o in options %}<option value="{{ o.0 }}" {% if o.0 == i.3 %}selected{% endif %}>{{ o.1 }}</option>{% endfor %}
						</select>
					</td></tr>
					<tr><td colspan="2">
						<input class="edit_order" type="hidden" name="edit_order" value="{{ i.4 }}" />
						<input class="form-submit" type="button" name="submit" value="Save" />
					</td></tr>
				</table>
			</div>
		</li>
		{% endfor %}
	</ul>
</div>
{% endfor %}
{% endif %}

{% if items|length|is_none %}<div class="empty-list">Menu list is empty.<br />To create them, add items on the right side.</div>{% endif %}