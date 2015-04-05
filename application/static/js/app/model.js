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
			function onScroll() {
				if ($(window).scrollTop() >= $(document).height() - $(window).height() - 600) {
					if (lastPage != currentPage) {

						var next_page = "";
						if (pages.length > 1) {
							next_page = pages[currentPage + 1]
						} else {
							next_page = self.currentNextPage;
						}

						fetchMore(next_page, function (response) {
							currentPage++;
						});
						lastPage = currentPage;
					}
				}
			}

			$(window).scroll(onScroll);
		}

		self.initPage = function (element, page) {
			$(window).scroll(function () {
				if (!page.loaded()) {
					if (page.previous_page && page.previous_page.loaded()) {
						var offset = $(element[1]).offset();
						var screenBottom = $(window).scrollTop() + $(window).height() + 600;
						if (offset.top < screenBottom) {
							page.load();
						}
					} else if (page.next_page && page.next_page.loaded()) {
						var offset = $(element[1]).offset();
						var screenTop = $(window).scrollTop() + $(window).height() + 600;
						if (offset.top < screenBottom) {
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
	}
});
