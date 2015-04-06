/**
 * Created by m on 05.04.15.
 */

define(['app/page', 'knockout', 'urls'], function (Page, ko, urls) {
	return function () {
		var self = this;
		self.name = ko.observable("");
		self.source = ko.observable("");
		self.id = ko.observable("");

		self.pages = ko.observableArray([]);

		var blockLoading = false;

		function init() {
			var pageInfo = $("#page-info");
			self.pager = $("#pager").slider({
				orientation: "vertical",
				stop: function (e, ui) {
					var page = (self.pages().length - ui.value);
					pageInfo.fadeOut("fast");
					self.pages()[page - 1].load(function () {
						var section = $(".section" + page);
						if (section.size()) {
							blockLoading = true;
							$('html, body').animate({
								scrollTop: section.offset().top - 60
							}, 200, function () {
								console.log(blockLoading);
								blockLoading = false;
							});
						}
					});
				},
				start: function () {
					pageInfo.fadeIn("fast");
				},
				slide: function (e, ui) {
					var page = (self.pages().length - ui.value);
					var handle = $("#pager .ui-slider-handle");
					pageInfo.offset({
						top: handle.offset().top,
						left: 30
					});
					pageInfo.text(page);
				}
			});
		}

		self.initPage = function (element, page) {
			$(window).scroll(function () {
				if (!blockLoading && !page.loaded()) {
					var $el = $(element[1]);
					var screenTop = $(window).scrollTop() - 600;
					var screenBottom = $(window).scrollTop() + $(window).height() + 600;
					var offset = $el.offset();
					offset.bottom = $el.height() + offset.top;
					if (page.previous_page && page.previous_page.loaded()) {
						if (offset.top > screenTop && offset.bottom < screenBottom) {
							page.load(function (r) {
								if (page.next_page_url) {
									if (page.model.id() == self.id()) {
										var pageItem = new Page(self, self.pages().length + 1, page.next_page_url);
										pageItem.previous_page = page;
										self.pages.push(pageItem);
									}
								}
							});
							self.pager.slider("option", "max", self.pages().length - 1);
						}
					}
				}
			});
		};

		self.last_selected_value = "";
		self.select = function (url) {
			self.last_selected_value = url;

			self.pages.removeAll();
			var page = new Page(self, 1, url);
			self.pages.push(page);
			page.load(function (r) {
				if (self.last_selected_value != url) {
					return;
				}

				$(window).unbind("scroll");

				self.name(r.name);
				self.source(r.source);
				self.id(r.data.id);

				var previousPage = page;

				if (r.data.pages.length) {
					r.data.pages.forEach(function (item, index) {
						if (index == 0) {
							return;
						}
						var page = new Page(self, index + 1, item);
						if (previousPage) {
							previousPage.next_page = page;
							page.previous_page = previousPage;
						}
						self.pages.push(page);
						previousPage = page;
					});
				} else {
                    if (r.data.next_page) {
                        page = new Page(self, 2, r.data.next_page);
                        page.previous_page = previousPage;
                        self.pages.push(page);
                        previousPage = page;
                    }
				}
				self.pager.slider("option", "value", self.pages().length - 1);

			});
			if ($('#theplace_search_query').select2('val')) {
				$.cookie("lastCategory", $('#theplace_search_query').select2('val'), {expires: 7, path: '/'});
			}
			//});

		};

		init();
	}
});
