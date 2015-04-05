/**
 * Created by m on 05.04.15.
 */
define(['urls', 'knockout', 'app/image'], function (urls, ko, Image) {
	return function (model, index, url) {
		var self = this;
		self.url = url;
		self.images = ko.observableArray([]);
		self.index = index;
		self.next_page = null;
		self.previous_page = null;

		self.loaded = ko.observable(false);
		self.loading = ko.observable(false);

		self.css = ko.pureComputed(function () {
			[
				!self.loaded() && !self.loading() ? "hidden" : ""
			].join("")
		});

		self.load = function () {
			if (self.loading()) {
				return;
			}

			self.loading(true);
			$.get(urls.images, {
				url: url
			}).done(function (r) {
				self.setImages(r.data.images, function () {
					setTimeout(function () {
						$(window).trigger('scroll');
					}, 1000)
				});
				self.loaded(true);
			}).always(function () {
				self.loading(false);
			});
		};

		self.setImages = function (images, ondone) {
			images.forEach(function (img) {
				self.images.push(new Image(img));
			});
			if (ondone) {
				ondone(self);
			}
			self.loading(false);
			self.loaded(true);
		};

		self.setupImage = function (element, index, data) {
			$(element).find('.lazy').lazyload({
				threshold: 600,
				effect   : "fadeIn"
			});
		};

	}
});
