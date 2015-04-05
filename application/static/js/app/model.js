/**
 * Created by m on 05.04.15.
 */

define(['app/page', 'knockout', 'urls'], function (Page, ko, urls) {
	return function () {
		var self = this;
		self.name = ko.observable("");
		self.source = ko.observable("");

		self.pages = ko.observableArray([]);

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
							$('html, body').animate({
								scrollTop: section.offset().top - 60
							}, 200);
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
				if (!page.loaded()) {
					var $el = $(element[1]);
					var screenTop = $(window).scrollTop() - 600;
					var screenBottom = $(window).scrollTop() + $(window).height() + 600;
					var offset = $el.offset();
					offset.bottom = $el.height() + offset.top;
					if (page.previous_page && page.previous_page.loaded()) {
						if (offset.top > screenTop && offset.bottom < screenBottom) {
							page.load();
						}
					}
				}
			});
		};

		self.select = function (url) {
			self.pages.removeAll();
			$.get(urls.images, {
				url: url
			}).done(function (r) {
				self.name(r.name);
				self.source(r.source);
				self.pager.slider("option", "max", r.data.pages.length - 1);
				self.pager.slider("option", "value", r.data.pages.length - 1);

				var previousPage = null;

				var page = new Page(self, 1, url);
				page.setImages(r.data.images, function () {
					setTimeout(function () {
						$(window).trigger('scroll');
					}, 1000)
				});
				self.pages.push(page);
				previousPage = page;

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

				if ($('#theplace_search_query').select2('val')) {
					$.cookie("lastCategory", $('#theplace_search_query').select2('val'), {expires: 7, path: '/'});
				}
			});

		};

		init();
	}
});
