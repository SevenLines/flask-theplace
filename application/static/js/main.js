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
		ko.applyBindings(photoModel, $("html")[0]);

		$('#theplace_search_query').select2({
			placeholder: "Enter name",
			allowClear: true,
			minimumInputLength: 2,
			ajax: {
				url: urls.query_categories,
				dataType: 'json',
				delay: 250,
				data: function (params) {
					return {
						query: params.term, // search term
						page: params.page
					};
				},
				processResults: function (data, page) {
					var out = [];
					data.items.forEach(function (category) {
						var item_category = {};
						item_category.text = category.name;
						if (category.sources.length > 1) {
							item_category.children = category.sources.map(function (source) {
								var item_source = {};
								item_source.text = source.name;
								if (source.albums.length > 1) {
									item_source.children = source.albums.map(function (album) {
										var item_album = {};
										item_album.text = album.name ? album.name : album.album_id;
										item_album.id = album.local_url;
										return item_album;
									});
									return item_source;
								} else if (source.albums.length == 1) {
									item_source.id = source.albums[0].local_url;
									return item_source;
								}
								return "";
							});
						} else if (category.sources.length == 1) {
							source = category.sources[0];
							if (source.albums.length > 1) {
								item_category.children = source.albums.map(function (album) {
									var item_album = {};
									item_album.text = album.name ? album.name : album.album_id;
									item_album.id = album.local_url;
									return item_album;
								});
							} else if (source.albums.length == 1) {
								item_category.id = source.albums[0].local_url;
								item_category.text = [item_category.text, " (", source.name, ")"].join('')
							}
						}
						out.push(item_category);
					});
					return {
						results: out
					};
				}
			}
		}).on('change', function (e) {
			photoModel.select(e.currentTarget.value);
		});

		(function () {
			var lastPosX = -1;
			var entered = false;
			$(".right-column").click(function () {
				$(".right-column").toggleClass("hovered");
			});
		})();

		if ($.cookie("lastCategory") && $.cookie("lastCategory") != "null") {
			photoModel.select($.cookie("lastCategory"));
		}
	});