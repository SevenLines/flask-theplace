/**
 * Created by m on 05.04.15.
 */
require.config({
	paths: {
		'knockout': '../vendor/knockout/dist/knockout'
	}
});

define('jquery', [], function () {
	return jQuery;
});

require(['app/model', 'urls', 'knockout'],
	function (PhotoModel, urls, ko) {
		var photoModel = new PhotoModel();
		ko.applyBindings(photoModel);

		$('#theplace_search_query').select2({
			placeholder       : "Enter name",
			allowClear        : true,
			minimumInputLength: 2,
			ajax              : {
				url           : urls.query_categories,
				dataType      : 'json',
				delay         : 250,
				data          : function (params) {
					return {
						query: params.term, // search term
						page : params.page
					};
				},
				processResults: function (data, page) {
					var sources = [];
					var out = [];
					data.items.forEach(function (item) {
						if (sources.indexOf(item.source_name) == -1) {
							sources.push(item.source_name);
						}
					});

					for (var i = 0; i < sources.length; ++i) {
						var item = {};
						item.text = sources[i];
						item.children = data.items.map(function (el) {
							if (el.source_name == item.text) {
								return {
									'id'  : el.local_url,
									'text': el.name
								}
							}
							return "";
						});
						out.push(item)
					}
					return {
						results: out
					};
				}
			}
		}).on('change', function (e) {
			photoModel.select(e.currentTarget.value);
		});

		if ($.cookie("lastCategory") && $.cookie("lastCategory") != "null") {
			photoModel.select($.cookie("lastCategory"));
		}
	});