/**
 * Created by m on 05.04.15.
 */
define(['urls', 'knockout'], function (urls, ko) {
	return function (data, page) {
		var self = this;
		self.exists = ko.observable(data.exists);
		self.src = ko.observable(data.src);
		self.thumbnail = ko.observable(data.thumbnail);
		self.downloading = ko.observable(false);
		self.page = page;

		self.css = ko.pureComputed(function () {
			return [
				self.exists() ? "exists" : "",
				self.downloading() ? "loading" : ""
			].join('')
		});

		self.preview = function () {
			var image = document.getElementById("image-preview");
			image.src = "";
			$(image).parent().addClass("loading");
			$.get(urls.image_url, {
				url: self.src()
			}).done(function (real_src) {
				image.src = real_src;
				$(image).one("load", function () {
					$(image).parent().removeClass("loading");
				})
			});
		};

		self.download = function () {
			self.downloading(true);
			$.post(urls.download, {
				url: self.src,
				name: self.page.model.name(),
				source: self.page.model.source()
			}).done(function () {
				self.exists(true);
			}).always(function () {
				self.downloading(false);
			});
			return false;
		};

		self.remove = function () {
			self.downloading(true);
			$.post(urls.remove, {
				url: self.src,
				name: self.page.model.name(),
				source: self.page.model.source()
			}).done(function () {
				self.exists(false);
			}).always(function () {
				self.downloading(false);
			});
			return false;
		}
	};
});