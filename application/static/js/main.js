/**
 * Created by m on 26.03.15.
 */

function PhotosModel(settings) {
	var self = this;

	(function () {
		var lastPosX = -1;
		var entered = false;
		$(".hover-area").hover(function (e) {
			lastPosX = e.clientX;
		}, function (e) {
			$(".right-column").toggleClass("hovered", false);
			entered = false;
		}).on("mousemove", function (e) {
			if (lastPosX - e.clientX > 50) {
				$(".right-column").toggleClass("hovered", false);
				entered = false;
			} else if (!entered && e.clientX - lastPosX > 5) {
				entered = true;
				$(".right-column").toggleClass("hovered", true);
				var image = $("#image-preview")[0];
			}
		});
	})();

	$(document).ready(function () {
		var currentPage = 1;
		var lastPage = currentPage;
		var pages = [];

		var template = _.template('<a class="image" href="<%= src %>"><img data-original="<%= thumbnail %>" /></a>');

		function setImage(event) {
			var image = document.getElementById("image-preview");
			image.src = "";
			$(image).parent().addClass("loading");
			setTimeout(function () {
				image.src = event.currentTarget.href;
				$(image).one("load", function () {
					$(image).parent().removeClass("loading");
				}).each(function () {
					if (this.complete) $(this).load();
				});
			}, 300);

			return false;
		}

		function fetchInit(url) {
			currentPage = 1;
			lastPage = currentPage - 1;
			pages.length = 0;
			if ($('#theplace_search_query').select2('val')) {
				console.log($('#theplace_search_query').select2('val'));
				$.cookie("lastCategory", $('#theplace_search_query').select2('val'), {expires: 7, path: '/'});
			}
			$("#images").empty();
			fetchMore(url, function () {
				fetchMore(pages[currentPage + 1], function (response) {
					currentPage++;
				});
				lastPage = currentPage;
				$(window).trigger('scroll');
			});
		}


		function fetchMore(url, ondone) {
			if (!url)
				return;
			$("#load-progress").show();
			$.get(settings.urls.images, {
				url: url
			}).done(function (response) {
				var first = false;
				if (pages.length == 0) {
					first = true;
					pages = response.data.pages;
					$("html, body").animate({scrollTop: 0}, "slow");
				}
				var $images = $('<div class="section"></div>');
				$("#images").append($images);
				response.data.images.forEach(function (item) {
					var $aimg = $(template({
						src      : item.src,
						thumbnail: item.thumbnail
					}));
					var $img = $aimg.find("img");
					$img.show().lazyload({
						threshold: 600,
						effect   : "fadeIn"
					});
					$aimg.on("click", setImage);
					$images.append($aimg);
				});
				$images.append("<hr\>");
				if (ondone) {
					ondone(response);
				}
				if (first) {
					$("html, body").animate({scrollTop: 1}, 0);
				}
				$("#load-progress").hide();
			});
		}


		function onScroll() {
			if ($(window).scrollTop() >= $(document).height() - $(window).height() - 600) {
				if (lastPage != currentPage) {
					fetchMore(pages[currentPage + 1], function (response) {
						currentPage++;
					});
					lastPage = currentPage;
				}
			}
		}

		$('#theplace_search_query').select2({
			placeholder       : "Enter name",
			allowClear        : true,
			minimumInputLength: 2,
			ajax              : {
				url           : settings.urls.query_categories,
				dataType      : 'json',
				delay         : 250,
				data          : function (params) {
					return {
						query: params.term, // search term
						page : params.page
					};
				},
				processResults: function (data, page) {
					return {
						results: data.items.map(function (item) {
							return {
								'id'  : item.local_url,
								'text': item.name
							}
						})
					};
				},
				cache         : true
			}
		}).on('change', function (e) {
			fetchInit(e.currentTarget.value);
		});

		if ($.cookie("lastCategory") && $.cookie("lastCategory") != "null") {
			fetchInit($.cookie("lastCategory"));
			console.log($.cookie("lastCategory"));
		}

		$(window).scroll(onScroll);
	});
}