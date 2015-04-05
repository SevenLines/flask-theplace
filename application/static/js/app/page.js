/**
 * Created by m on 05.04.15.
 */
define(['urls', 'knockout', 'app/image'], function (urls, ko, Image) {
	return function (model, index, url, next_page_url) {
		var self = this;
		self.url = url;
		self.images = ko.observableArray([]);
		self.index = index;
		self.next_page = null;
		self.previous_page = null;
		self.model = model;
		self.next_page_url = next_page_url;

		self.loaded = ko.observable(false);
		self.loading = ko.observable(false);

		self.css = ko.pureComputed(function () {
			return [
				self.loading() ? "loading" : "",
				self.loaded() ? "loaded" : "",
				"section" + self.index,
			].join(" ")
		});

		self.load = function (ondone) {
			if (self.loading() || self.loaded()) {
				if (ondone) {
					ondone(null, self);
				}
			} else {
				self.loading(true);
				$.get(urls.images, {
					url: url,
					source_name: self.model.source_name,
					id: self.model.id
				}).done(function (r) {
					self.next_page_url = r.data.next_page;
					self.setImages(r.data.images, function () {
						setTimeout(function () {
							$(window).trigger('scroll');
						}, 1000)
					});
					if (ondone) {
						ondone(r, self);
					}
					self.loaded(true);
				}).always(function () {
					self.loading(false);
				});
			}
		};

		self.setImages = function (images, ondone) {
			images.forEach(function (img) {
				self.images.push(new Image(img, self));
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
				//effect   : "fadeIn"
			});
		};

	}
});
