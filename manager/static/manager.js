$(function(){
    $("td.sitemap input[name='sitemap']").bind('click', function(){
        var $this = $(this);
        var $waiting = $this.parent().find('.waiting');
        $this.css({'display': 'none'});

        i = 0;
        var interval = setInterval(function() {
            i = ++i % 7;
            $waiting.html(Array(i+1).join("."));
        }, 500);

        $.post('/admin/seo/sitemap/', {'action': 'create'}, function(data){
            if (data == 'created') {
                clearInterval(interval);
                $waiting.text('OK');
            };
        });
    });

	$("#nav_list li div span.edit").live('click', function(){
		var $el = $(this).parent().parent().next();
		if ($el.is(":visible")) {
			$el.slideUp('slow');
		} else {
			$(".nav_edit").slideUp('slow');
			$el.slideToggle('slow');
		}
	});

	$("#nav_list li div span.remove").live('click', function(){
		var pk = $(this).parent().parent().next().find(".edit_pk").val();
		var $li = $(this).parent().parent().parent();
		$.post('/admin/nav/remove/', {'pk': pk}, function(data){
			if (data['error']) {
				$("#notificator").notification({
					text: data['error'],
					type: 'error'
				});
			} else {
				$("#nav_list").html(data['html']);
				sort_menu_items();
				$(".nav_edit .edit_url").eComboBox();
			}
		});
	});

	$("#nav_list .form-submit").live('click', function(){
		$table = $(this).parent().parent().parent();
		var pk = $table.find(".edit_pk").val();
		var menu_name = $table.find(".edit_menu").val();
		var title = $table.find(".edit_title").val();
		var url = $table.find(".edit_url").val();
		var order_num = $table.find(".edit_order").val();
		$.post('/admin/nav/' + pk + '/', {'menu_name': menu_name, 'title': title, 'url': url, 'order_num': order_num}, function(data){
			if (data['error']) {
				$("#notificator").notification({
					text: data['error'],
					type: 'error'
				});
			} else {
				$("#nav_list").html(data['html']);
				sort_menu_items();
				$(".nav_edit .edit_url").eComboBox();
			}
		});
	});

	$("#nav_new .new_url").eComboBox();
	$(".nav_edit .edit_url").eComboBox();

	$("#nav_new .form-submit").bind('click', function(){
		$table = $(this).parent().parent().parent();
		var menu_name = $table.find(".new_menu").val();
		var title = $table.find(".new_title").val();
		var url = $table.find(".new_url").val();
		var order_num = $table.find(".new_order").val();
		$.post('/admin/nav/', {'menu_name': menu_name, 'title': title, 'url': url, 'order_num': order_num}, function(data){
			if (data['error']) {
				$("#notificator").notification({
					text: data['error'],
					type: 'error'
				});
			} else {
				$("#nav_list").html(data['html']);
				sort_menu_items();
				$(".nav_edit .edit_url").eComboBox();
			}
		});
	});

	$(".page-list .page_edit").bind('click', function(){
		$(this).find("form").submit();
	});
	$(".page-list .page_delete").bind('click', function(){
		$(this).find("form").submit();
	});

	$("#page-title-form").change(function(){
		var $this = $(this);
		var $name = $("#page-name-form");
		var $save = $("#status #save");
		$name.val('');
		$name.attr('disabled', true);
		$save.attr('disabled', true);
		$.post('/admin/pages/url/', {'text': $this.val()}, function(data){
			$name.attr('disabled', false);
			$name.val(data);
			$save.attr('disabled', false);
		}).error(function(){
			$name.attr('disabled', false);
			$name.val('');
			$save.attr('disabled', false);
		});
	});

//	var $editor = $('#editor textarea').wysiwyg({
//		css : "/static/style.css",
//		iFrameClass : "editor_iframe"
//	});

	$('#layout_title').disableSelection();

	$('#layout_btn input').bind('click', function(){
		$('#layouts .columnwrapper').slideToggle('fast');
	});

	$('#layouts .column li').bind('mouseenter', function(){
		$(this).css('background-color', '#f7f1c8');
		$(this).css('border', '1px solid #8f4237');
	});

	$('#layouts .column li').bind('mouseleave', function(){
		$(this).css('background-color', '#fff');
		$(this).css('border', '1px solid #fff');
	});

	$('#layouts .layout_img').bind('click', function(){
		var name = $(this).parent().find(".layout_name").html();
		$.post('/admin/pages/layout/', {'action': 'load', 'name': name}, function(data){
			var $editor = $('#editor textarea');
			$editor.wysiwyg('clear');
			$editor.wysiwyg('setContent', data['content']);
		});
	});

	$(".checkbox").change(function(){
		if($(this).is(":checked"))
			$(this).next("label").addClass("label-selected").html('Page is active');
		else
			$(this).next("label").removeClass("label-selected").html('Page is hidden');
    });

	$("#delete").bind('click', function(){
		var pk = $("#pk").val();
		$(".delete_form").append('<input type="hidden" name="pk" value="' + pk + '" />').submit();
	});

	$("#save").bind('click', function(){
		var pk = $("#pk").val();
		var name = $("#page-name-form").val();
		var title = $("#page-title-form").val();
		var content = $(".editor_iframe").contents().find('body').html();
		var status = 'off';
		if ($("#active").attr('checked')) status = 'on';
		$.post('/admin/page/save/', {'pk': pk, 'name': name, 'title': title, 'content': content, 'status': status}, function(data){
			if (data['result'] == 'created') {
				$("#pk").val(data['pk']);
				$("#notificator").notification({
					text: 'Page has beed created',
					type: 'info'
				});
			}
			if (data['result'] == 'updated') {
				$("#notificator").notification({
					text: 'Page has beed updated',
					type: 'info'
				});
			}
			if (data['result'] == 'error') {
				$("#notificator").notification({
					text: 'Error saving page',
					type: 'error'
				});
			}
			$("html, body").animate({ scrollTop: 0 }, "slow");
		});
	});

	$("#preview").bind('click', function(){
		if ($("#page_edit").is(':visible')) {
			$("#page_edit").animate({ 'left': '1000px' }, 500, function() {
				$(this).hide();
				$("#pk").after('<div class="wrapper page-canvas"></div>');
				$("#pk").after('<form action="/admin/page/preview/" id="preview_frame" target="preview_frame" method="post"><input type="hidden" name="content" value="" /></form>');
				$(".wrapper").html('<iframe name="preview_frame" width="100%" height="700" frameBorder="0"></iframe>');
				$("#preview_frame input").val($(".editor_iframe").contents().find('body').html());
				$("#preview_frame").submit();
//				$.post('/admin/page/preview/', {'content': content}, function(data){
//					$(".wrapper").html('<iframe >' + data + '</iframe>');
//				});
//				$(".wrapper").html($(".editor_iframe").contents().find('body').html());
				$("#preview").attr({'value': "Edit"});
				$("#status").css({'z-index': 1000});
				$("#overlay").removeClass('hide');
			});
		} else {
			$(".wrapper").animate({ 'left': '1000px' }, 500, function() {
				$("#overlay").addClass('hide');
				$("#status").css({'z-index': 0});
				$("#page_edit").css({ 'left': '0px' });
				$("#page_edit").show();
				$("#preview").attr({'value': "Preview"});
				$(this).remove();
			});
		}
	});

    $(".checkbox-label").disableSelection();

    $(".property_list .remove").live('click', function() {
    	var $li = $(this).parent();
    	$li.slideUp('fast');
    	$li.remove();
    });

    $("#properties_form .next").bind('click', function(){
    	var properties = {};
    	$(".property_list li.sort").each(function() {
    		$this = $(this);
    		var i = $this.index();
    		var property = $this.find("div:nth-child(1)").html();
    		var container = $this.find("div:nth-child(2)").html();
    		properties[property] = [i, container];
    	});
    	$("#properties_form").append("<input type='hidden' name='properties' value='" + $.toJSON(properties) + "' />");
    	$("#properties_form").submit();
    });

	$("#add_property .form-submit").bind('click', function() {
		var name = $("#add_property .form-text").val();
		var value = $("#add_property .property_container option:selected").html();

		if ((/^[\s\d\wА-Яа-я-]{1,75}$/.test(name)) && (value.length)) {
			$row = $("ul.property_list").find("li:last-child");
			$row.before('<li class="sort block"><div></div><div></div><div class="remove">&#10006;</div></li>');
			$row.prev().find("div:nth-child(1)").html(name);
			$row.prev().find("div:nth-child(2)").html('( ' + value + ' )');
			$("#add_property .prompt").css("color", "#1155CC");
		} else {
			$("#add_property .prompt").css("color", "#990000");
		}
	});

	$(".property_list").sortable({
		items: 'li.sort',
		placeholder: "ui-state-highlight",
		forcePlaceholderSize: true
	});

	$("li.sort").disableSelection();

	var $bar = null;
    var $percent = null;
    var $status = null;
    var $image_dialog = null;

    $('#img_upload_btn').live('click', function(){
        var $form = $('.ui-dialog #ci_image_upload form');
        var action = $form.attr('action')
        var attempt = 0;
        $form.attr('action', action + '?X-Progress-ID=1')
        $form.submit();

        var interval = 0;
        var $bar = $('.ui-dialog .bar .progress');
        var $value = $('.ui-dialog .bar .percent');
        var max_width = $bar.parent().width();
        var percentVal = '0%';
        var percentComplete = 0;

        $bar.parent().css({'border': '1px solid #ccc'});
        $value.css({'display': 'block'});
        $value.text('0%');

        function get_progress() {
            result = null;
            $.ajax({
                url: action + 'progress/',
                data: {'X-Progress-ID': 1},
                success: function(data, status){
                    if (data[0] != data[1]) {
                        result = data;
                    }

                    if ((data[0] == data[1]) && (data[0] != 'error')) {
                        result = 'complete';
                    }

                    if (data[0] == 'error') {
                        if (attempt == 5) result = 'error'
                        else {
                            attempt += 1;
                            result = data;
                        }
                    }
                },
                error: function(data, status) { result = 'error'; },
                    type: 'GET',
                    dataType: 'json',
                    async: false
                });

                return result
            }

            interval = setInterval(function(){
                result = get_progress();

                if (result == 'error') {
                    clearInterval(interval);
                    $value.text('upload error');
                    $bar.css({'background-color': '#990000'});
                    return
                }

                if (result == 'complete') {
                    clearInterval(interval);
                    $value.text('100%');
                    $bar.width(max_width);
                    return
                }

                if (result[0] > 0) percentComplete = Math.round((result[0] / result[1]) * 100) / 100;
                else percentComplete = 0;

                percentVal = Math.round(percentComplete * 100) + '%';
                $value.text(percentVal);
                $bar.width(percentComplete * max_width);

            }, 1000);
        });

        $('.ui-dialog #ci_image_upload form').ajaxForm({
/*      beforeSend: function() {
            var percentVal = '0%';
            $bar.width(percentVal);
            $percent.html(percentVal);
        },
        uploadProgress: function(event, position, total, percentComplete) {
            var percentVal = percentComplete + '%';
            $bar.width(percentVal);
            $percent.html(percentVal);
        },*/
        complete: function(xhr) {
            if (xhr.responseText == 'error') {
                $(".top-text .upload_msg").css({'display':'none'});
                $(".top-text .err_msg").css({'display':'block'});
            }
        	else insert_ci_image_handler(xhr.responseText);
        },
        delegation: true,
        async: true
    });

	$(".images_add .add_image .form-submit").bind('click', function() {
		image_dialog = $("#image_result").clone().dialog({
			title: "Add image",
			closeText: 'x',
			modal: true,
			width: 640,
			height: 440,
			autoOpen: false,
			create: function(event, ui) {
				$(event.target).parent().css('position', 'fixed');
				$(".ui-dialog .top-text .upload_msg").css({'display': 'block'});
				$(".ui-dialog .top-text .err_msg").css({'display': 'none'});
			},
			close: function(event, ui) {
				$(this).dialog('destroy').remove();
			}
		});

		image_dialog.dialog("open");
		$bar = $('.ui-dialog .bar');
		$percent = $('.ui-dialog .percent');
		$status = $('.ui-dialog-content');
	});

	var insert_ci_image_handler = function(src) {
		if ($("#image_preview").length) {
			if ($("#image_preview img").attr('alt') != 'No image') {
				$.post('/admin/resize/', {'name': src, 'size': 'mini'}, function(data){
					if (data != 'error') {
						if ($(".extra_images").length == 0) {
							$("#image_preview").after('<table class="extra_images"><tr><td><div class="frame"></div></td><td><div class="frame"></div></td><td><div class="frame"></div></td></tr></table>');
							$(".extra_images td:first-child div.frame").html('<div class="crop">' + data + '</div><span class="remove">&#10006;</span>');
							image_dialog.dialog('close');
						}
						else {
							if ($(".extra_images tr:last-child td:nth-child(2) div.frame").find("img").length == 0) {
								$(".extra_images tr:last-child td:nth-child(2) div.frame").html('<div class="crop">' + data + '</div><span class="remove">&#10006;</span>');
								image_dialog.dialog('close');
								return false;
							}
							if ($(".extra_images tr:last-child td:last-child div.frame").find("img").length != 0)
								$(".extra_images").append('<tr>' +
									'<td><div class="frame"><div class="crop">' + data + '</div><span class="remove">&#10006;</span></div></td>' +
									'<td><div class="frame"></div></td>' +
									'<td><div class="frame"></div></td>' +
									'</tr>');
							else $(".extra_images tr:last-child td:last-child div.frame").html('<div class="crop">' + data + '</div><span class="remove">&#10006;</span>');
							image_dialog.dialog('close');
						}
					}
				});
			}
			else {
				$.post('/admin/resize/', {'name': src, 'size': 'small'}, function(data){
					if (data != 'error') {
						$("#image_preview").html(data);
						image_dialog.dialog('close');
					}
				});
			}
		} else {
            /* static page */
//            console.log("ok");
        }
	}

	$(".ui-dialog #ci_img_browse_btn").live('click', function() {
		$.post('/admin/browse/', {}, function(data) {
			$status = $('.ui-dialog-content');
			$status.html(data);
		});
	});

	$(".ui-dialog .thumb_browse td div.crop").live('dblclick', function() {
		var src = $(this).find('img').attr('src');
		if (src) insert_ci_image_handler($(this).find('img').attr('src'));
	});

	$("#image_result .thumb_browse td div.frame span.remove").live('click', function() {
		var src = $(this).parent().find('img').attr('src');
		if (src) {
			$.post('/admin/uploaded/remove/', {'src': src}, function(data) {
				if (data != 'error') {
					$(".ui-dialog #image_result").html(data);
				}
			});
		}
	});

	$(".browse_nav .upload input").live('click', function(){
		$status.html($("#image_result").html());
	});

	$(".browse_nav .nav .prev").live('click', function(){
		var page = $(".browse_nav").prev("input[name=page]").val();
		page =  parseInt(page) - 1;
		$.post('/admin/browse/', {'page': page}, function(data){
			if (data != 'error') {
				$(".ui-dialog-content").html(data);
			}
		});
	});

	$(".browse_nav .nav .next").live('click', function(){
		var page = $(".browse_nav").prev("input[name=page]").val();
		page =  parseInt(page) + 1;
		$.post('/admin/browse/', {'page': page}, function(data){
			if (data != 'error') {
				$(".ui-dialog-content").html(data);
			}
		});
	});

	$("table.extra_images td span.remove").live('click', function(){
        $(this).parent().html('');
        if (!$(".extra_images").find(".crop img").length) $(".extra_images").remove();
	});

	$(".data_add form").submit(function() {
		var images = {};
		images['main'] = $("#image_preview img").attr('src');
		images['extra'] = [];
		$(".extra_images img").each(function() {
			images['extra'].push($(this).attr('src'));
		});
		$(this).find("input[name=images]").val($.toJSON(images));
	});

	function sort_menu_items() {
		$("#nav_list ul").sortable({
			connectWith: ".menu-list",
			placeholder: "ui-state-highlight",
			forcePlaceholderSize: true,
			update: function(event, ui) {
				var $item = $(ui.item);
				if (this === ui.item.parent()[0]) {
					var menu = {};
					$("#nav_list").children(".menu").each(function() {
						var menu_name = $(this).children(".menu_title").html();
						var $list = $(this).children(".menu-list");
						var items = [];
						$list.children().each(function(index) {
							items[index] = $(this).find('.edit_pk').val();
						});
						menu[menu_name] = items;
					});

					$("#notificator").notification({
						text: 'The changes will be saved after confirmation',
						onOk: function(){
							$.post('/admin/nav/update/', {'menu': $.toJSON(menu)}, function(data){
								if (data['error']) {
									$("#notificator").notification({
										text: data['error'],
										type: 'error'
									});
								}
							});
						}
					});
				}
			}
		});
	}

	sort_menu_items();

	$('.category_table table tr, .items_table table tr').live('mouseover', function() {
	 	$(this).addClass('selected-row');
	});

	$('.category_table table tr, .items_table table tr').live('mouseout', function() {
		$(this).removeClass('selected-row');
	});

	$('.category_table .list .catalog-nav input[name=catalog_prev]').live('click', function(){
		var $this = $(this);
		var page = $(".catalog-nav input[name=page]").val();
		page = parseInt(page) - 1;
		if (page < 1) page = 1;
		var category = $(".catalog-nav input[name=category]").val();
		category = parseInt(category);
		if (category < 0) category = 0;
		$(".catalog-nav input[name=page]").val(page);
		$.post('/admin/catalog/', {'category': category, 'page': page}, function(data){
			$(".category_table").html(data);
		});
	});

	$('.category_table .list .catalog-nav input[name=go]').live('click', function(){
		var page = $('.catalog-nav input[name=catalog_page]').val();
		if (page < 1) page = 1;
		var category = $(".catalog-nav input[name=category]").val();
		category = parseInt(category);
		if (category < 0) category = 0;
		$(".catalog-nav input[name=page]").val(page);
		$.post('/admin/catalog/', {'category': category, 'page': page}, function(data){
			$(".category_table").html(data);
		});
	});

	$('.category_table .list .catalog-nav input[name=catalog_next]').live('click', function(){
		var page = $(".catalog-nav input[name=page]").val();
		page = parseInt(page) + 1;
		if (page < 1) page = 1;
		var category = $(".catalog-nav input[name=category]").val();
		category = parseInt(category);
		if (category < 0) category = 0;
		$(".catalog-nav input[name=page]").val(page);
		$.post('/admin/catalog/', {'category': category, 'page': page}, function(data){
			$(".category_table").html(data);
		});
	});

	$("#category_add").bind('click', function(){
		var action = 'create';
		var name = $("#category_name").val();
		$.post('/admin/catalog/category/', {'action': action, 'name': name}, function(data){
			if (data != 'error') {
				$(".category_table").html(data);
			}
		});
	});

	$(".category_table .list ul.category_meta .delete").live('click', function(){
		var action = 'delete';
		var $deleteTR = $(this).parents(".category_table table tbody tr");
		var pk = $deleteTR.find("td.first input[name=pk]").val();
		$.post('/admin/catalog/category/', {'action': action, 'pk': pk}, function(data){
			if (data != 'error') {
				if (data['number'] == 0 ) {
					$deleteTR.fadeOut(700);
				} else {
					console.log("not empty!");
				}
			}
		});
	});

	$(".category_table .list ul.category_meta .clear").live('click', function(){
		var action = 'clear';
		var $clearTR = $(this).parents(".category_table table tbody tr");
		var pk = $clearTR.find("td.first input[name=pk]").val();
		$.post('/admin/catalog/category/', {'action': action, 'pk': pk}, function(data){
			if (data != 'error') {
				if (data['number'] != 0 ) {
					console.log("empty!");
				} else {
					console.log("already empty!");
				}
			}
		});
	});

	$(".category_table .list ul.category_meta .rename").live('click', function(){
		var action = 'rename';
		var $renameTR = $(this).parents(".category_table table tbody tr");
		var pk = $renameTR.find("td.first input[name=pk]").val();
		var name = $renameTR.find("td.first .category_name").html();
		$renameTR.find("td.first .category_name").html('<input type="text" class="form-text cat_name_edit" id="category_name_form" value="' + name +'" /><input type="button" class="form-submit cat_name_edit" id="cat_edit_btn" value="Save" /></span>');
		$("#category_name_form").focus();
		$("body").bind('click', function(e) {
			if (!$(e.target).hasClass("cat_name_edit")) {
				$renameTR.find("td.first .category_name").html(name);
				$("body").unbind('click');
			}
		});
		$("#cat_edit_btn").bind('click', function(){
			var new_name = $("#category_name_form").val();
			if (new_name.length) {
				$.post('/admin/catalog/category/', {'action': action, 'pk': pk, 'name': new_name}, function(data){
					if (data != 'error') $renameTR.find("td.first .category_name").html(data['name']);
					else $renameTR.find("td.first .category_name").html(name);
					$("body").unbind('click');
				});
			}
		});
	});

	$(".category_table .list ul.category_meta .view").live('click', function() {
		var $viewTR = $(this).parents(".category_table table tbody tr");
		var pk = $viewTR.find("td.first input[name=pk]").val();
		$.post('/admin/catalog/category/', {'action': 'browse', 'pk': pk, 'page': 2}, function(data){
			if (data != 'error') {
				$(".category_table .list").animate({ 'left': '1000px' }, 500, function(){
					var catalog_table = $(this);
					$(this).hide();
					$(this).appendTo('#category_list');
					$(this).removeClass('list').addClass('hidden-list');
					$(".category_table").append(data);
					$(".category_create table").fadeOut('fast', function() {
						$(".category_create").append('<table class="back"><tr><td><div>Add new catalog item:</div><a href="/admin/catalog/add/'+ pk +'/"><input type="button" class="form-submit" value="Add" /></a></td><td><span>Back to categories:</span><input type="button" class="form-submit" id="back" value="Back" /></td></tr></table>');
					});
				});
			}
		});
	});

	$(".category_create #back").live('click', function() {
		$(".category_table .list").animate({ 'left': '1000px' }, 500, function() {
			var parent_table = $('#category_list .hidden-list');
			parent_table.appendTo('.category_table');
			parent_table.css({ 'left': '0px' });
			parent_table.removeClass('hidden-list').addClass('list');
			parent_table.fadeIn('fast');
			$(this).remove();
			$(".category_create table.back").fadeOut('fast', function() {
				$(this).remove();
				$(".category_create table").fadeIn('fast');
			});
		});
	});

	$(".category_table .list ul.category_meta .add").live('click', function(){
		var $addTR = $(this).parents(".category_table table tbody tr");
		var pk = $addTR.find("td.first input[name=pk]").val();
		window.location.href = "/admin/catalog/add/" + pk + "/";
	});

	$(".category_table .list ul.item_meta .edit").live('click', function(){
		var $editTR = $(this).parents(".category_table table tbody tr");
		var pk = $editTR.find("td.first div").html();
		window.location.href = "/admin/catalog/edit/?id=" + pk;
	});

	$(".category_table .list ul.item_meta .activate").live('click', function(){
		$this = $(this);
		var $hideTR = $(this).parents(".category_table table tbody tr");
		var pk = $hideTR.find("td.first div").html();
		$.post('/admin/catalog/activate/', {'id': pk}, function(data) {
			if (data == 'hide') {
				$hideTR.addClass('h');
				$this.html('Show');
			}
			else if (data == 'active') {
				$hideTR.removeClass('h');
				$this.html('Hide');
			}
		});
	});

	$(".category_table .list ul.item_meta .delete").live('click', function(){
		var $deleteTR = $(this).parents(".category_table table tbody tr");
		var pk = $deleteTR.find("td.first div").html();
		$.post('/admin/catalog/delete/', {'id': pk}, function(data){
			if (data != 'error') $deleteTR.fadeOut(700);
		});
	});

	$(".category_table table tr").live('mouseenter', function(){
		$("td", this).animate({ backgroundColor: "#ccc" }, 100);
	});

	$(".category_table table tr").live('mouseleave', function(){
		if ($(this).hasClass("even")) $("td", this).animate({ backgroundColor: "#f5f5f5" }, 100);
		else $("td", this).animate({ backgroundColor: "#fff" }, 100);
	});

	$("ul.category_meta li, ul.item_meta li").live('mouseenter', function(){
		$(this).animate({ backgroundColor: "#808080", color: "#f5f5f5" }, 50);
	});

	$("ul.category_meta li, ul.item_meta li").live('mouseleave', function(){
		$(this).animate({ backgroundColor: "#f5f5f5", color: "#333" }, 50);
	});

	$.fn.autoResize = function(options) {
        var settings = $.extend({
            onResize : function(){},
            animate : true,
            animateDuration : 150,
            animateCallback : function(){},
            extraSpace : 10,
            limit: 1000
        }, options);

        // Only textarea's auto-resize:
        this.filter('textarea').each(function(){
                // Get rid of scrollbars and disable WebKit resizing:
            var textarea = $(this).css({resize:'none','overflow-y':'hidden'}),
                // Cache original height, for use later:
                origHeight = textarea.height(),
                // Need clone of textarea, hidden off screen:
                clone = (function(){
                    // Properties which may effect space taken up by chracters:
                    var props = ['height','width','lineHeight','textDecoration','letterSpacing'],
                        propOb = {};
                    // Create object of styles to apply:
                    $.each(props, function(i, prop){
                        propOb[prop] = textarea.css(prop);
                    });
                    // Clone the actual textarea removing unique properties
                    // and insert before original textarea:
                    return textarea.clone().removeAttr('id').removeAttr('name').css({
                        position: 'absolute',
                        top: 0,
                        left: -9999
                    }).css(propOb).attr('tabIndex','-1').insertBefore(textarea);
                })(),
                lastScrollTop = null,
                updateSize = function() {
                    // Prepare the clone:
                    clone.height(0).val($(this).val()).scrollTop(10000);
                    // Find the height of text:
                    var scrollTop = Math.max(clone.scrollTop(), origHeight) + settings.extraSpace,
                        toChange = $(this).add(clone);
                    // Don't do anything if scrollTip hasen't changed:
                    if (lastScrollTop === scrollTop) { return; }
                    lastScrollTop = scrollTop;
                    // Check for limit:
                    if ( scrollTop >= settings.limit ) {
                        $(this).css('overflow-y','');
                        return;
                    }
                    // Fire off callback:
                    settings.onResize.call(this);
                    // Either animate or directly apply height:
                   settings.animate && textarea.css('display') === 'block' ?
                        toChange.stop().animate({height:scrollTop}, settings.animateDuration, settings.animateCallback)
                        : toChange.height(scrollTop);
                };
            // Bind namespaced handlers to appropriate events:
            textarea
                .unbind('.dynSiz')
                .bind('keyup.dynSiz', updateSize)
                .bind('keydown.dynSiz', updateSize)
                .bind('change.dynSiz', updateSize);
        });
        return this;
    };

	$(".data_add textarea").autoResize();

	if ($(".settings #settings_logo img").attr('src') == '') {
		$(".settings #settings_logo .remove").hide('fast');
	}
	$(".settings #settings_logo .remove").click(function(){
		var $this = $(this);
		$.post('/admin/settings/logo/clear/', {'action': 'delete'}, function(data){
			if(data == 'success') {
				$("#settings_logo img").attr('src', '');
				$this.hide('fast');
			}
		});
	});

	$(".settings input[type=file]").change(function(){
		$('.ui-dialog #ci_image_upload form').ajaxForm({
			beforeSend: function() {
				var percentVal = '0%';
				bar.width(percentVal);
				percent.html(percentVal);
			},
			uploadProgress: function(event, position, total, percentComplete) {
				var percentVal = percentComplete + '%';
				bar.width(percentVal);
				percent.html(percentVal);
			},
			complete: function(xhr) {
				if (xhr.responseText == 'error') {
					$(".top-text .upload_msg").css({'display':'none'});
					$(".top-text .err_msg").css({'display':'block'});
				}
				else insert_ci_image_handler(xhr.responseText);
			},
			delegation: true,
			async: true
		});
	});

	$(".settings .connect #radio_yes").bind('click', function() {
		$(".connect_email").slideDown('fast');
	});

	$(".settings .connect #radio_no").bind('click', function() {
		$(".connect_email").slideUp('fast');
	});

    $(".settings .func input").bind('click', function() {
        var theme = $(this).parent().find('input[name="theme"]').val();
        $.post('/manager/settings/theme/', {'theme': theme}, function(data) {
            if (data) {
                $("#notificator").notification({
                    text: 'Current theme: "' + data + '"',
                    type: 'info'
                });
            } else {
                $("#notificator").notification({
                    text: 'Theme has not been changed',
                    type: 'error'
                });
            };
        });
    });

	$.fn.notification = function(options) {
		var defaults = {
			text : '',
			type : 'info',
			onOk : false,
			onCancel: true
		};

		if (options) $.extend(defaults, options);

		return this.each(function() {
			var $this = $(this);
			if ($this.is(":hidden")) {
				$this.addClass(defaults['type']);
				$this.html('<div class="message">' + defaults['text'] + '</div>');
				$this.append('<div class="buttons">');
				if ( typeof(defaults['onOk']) == "function" ) {
					$this.append('<input id="ok-button" class="notify-button" type="button" value="Save" />');
				}
				if ( defaults['onCancel'] == true ) {
					$this.append('<input id="cancel-button" class="notify-button" type="button" value="Close" />');
				}
				$this.append('</div>');
				$this.slideDown('fast');
			}
			if ( typeof(defaults['onOk']) == "function" ) {
				$ok = $this.find("#ok-button");
				$ok.unbind('click');
				$ok.bind('click', function(){
					defaults['onOk']();
					$ok.unbind('click');
                    $this.removeClass();
					$this.slideUp('fast');
				});
			}

			$cancel = $this.find("#cancel-button");
			$cancel.unbind('click');
			$cancel.bind('click', function() {
                $cancel.unbind('click');
                $this.removeClass();
				$this.slideUp('fast');
			})
		});
	}
});