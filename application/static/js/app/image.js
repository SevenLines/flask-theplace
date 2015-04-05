/**
 * Created by m on 05.04.15.
 */
define(['urls', 'knockout'], function (urls, ko) {
	return function (data) {
		var self = this;
		self.exists = ko.observable(data.exists);
		self.src = ko.observable(data.src);
		self.thumbnail = ko.observable(data.thumbnail);

		self.css = ko.pureComputed(function () {
			return [
				self.exists() ? "exists" : ""
			].join('')
		})
	};
});