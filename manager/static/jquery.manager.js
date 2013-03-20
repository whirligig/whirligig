(function($){
    $.fn.imageDialog = function(opts){

        var obj = new $.wysiwyg.dialog.createDialog("jqueryui"),

        this.options = {
            "modal": true,
            "draggable": true,
            "title": "Title",
            "content": "Content",
            "width":  "auto",
            "height": "auto",
            "zIndex": 2000,
            "open": false,
            "close": false
        };

        this.isOpen = false;
        $.extend(this.options, opts);
        this.object = obj;

        // Opens a dialog with the specified content
        this.open = function () {
            this.isOpen = true;
            obj.init.apply(that, []);
            var $dialog = obj.show.apply(that, []);
            $that.trigger("afterOpen", [$dialog]);
        };

        this.show = function () {
            this.isOpen = true;
            $that.trigger("beforeShow");
            var $dialog = obj.show.apply(that, []);
            $that.trigger("afterShow");
        };

        this.hide = function () {
            this.isOpen = false;
            $that.trigger("beforeHide");
            var $dialog = obj.hide.apply(that, []);
            $that.trigger("afterHide", [$dialog]);
        };

        // Closes the dialog window.
        this.close = function () {
            this.isOpen = false;
            var $dialog = obj.hide.apply(that, []);
            $that.trigger("beforeClose", [$dialog]);
            obj.destroy.apply(that, []);
            $that.trigger("afterClose", [$dialog]);
            jWysiwyg.ui.focus();
        };

        if (this.options.open) {
            $that.bind("afterOpen", this.options.open);
        }

        if (this.options.close) {
            $that.bind("afterClose", this.options.close);
        }

        return this;
    };
})(jQuery);