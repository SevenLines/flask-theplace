/**
 * Created by m on 26.03.15.
 */

function PhotosModel(settings) {
	var self = this;
	self.currentCategoryName = '';
	self.currentSourceName = '';
	self.currentNextPage = '';
	self.is_local = false;
	self.downloadClick = false;
	self.currentAlbumId = -1;


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

		var templateImageItem = $("#template-image-item").html();
		var templateSectionItem = $("#template-section-item").html();
		Mustache.parse(templateImageItem);
		Mustache.parse(templateSectionItem);

		function setImage(event) {
			console.log("cool");
			if (self.downloadClick) {
				self.downloadClick = false;
			} else {
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
		}

		function fetchInit(url) {
			currentPage = 0;
			lastPage = currentPage - 1;
			pages.length = 0;
			if ($('#theplace_search_query').select2('val')) {
				$.cookie("lastCategory", $('#theplace_search_query').select2('val'), {expires: 7, path: '/'});
			}
			$("#images").empty();
			fetchMore(url, function (response) {
				self.currentAlbumId = response.data.id;
				self.currentCategoryName = response.name;


				var next_page = "";
				if (pages.length > 1) {
					next_page = pages[currentPage+1]
				} else {
					next_page = self.currentNextPage;
				}

				fetchMore(next_page, function (response) {
					currentPage++;
				});
				lastPage = currentPage;
			});
		}


		function fetchMore(url, ondone) {
			if (!url)
				return;
			$("#load-progress").show();
			$.get(settings.urls.images, {
				id         : self.currentAlbumId,
				source_name: self.currentSourceName,
				url        : url
			}).done(function (response) {
				self.is_local = response.is_local;
				self.currentNextPage = response.data.next_page;
				var page = currentPage + 1;

				if (pages.length == 0) {
					pages = response.data.pages;
					page -= 1;
				}
				var $images = $(Mustache.render(templateSectionItem, {
					page       : page + 1,
					pages_count: pages.length
				}));

				$("#images").append($images);
				response.data.images.forEach(function (item) {
					var rendered = Mustache.render(templateImageItem, {
						src      : item.src,
						thumbnail: item.thumbnail,
						cls      : "saveme",
						exists   : item.exists ? 'exists' : '',
						download : self.is_local ? '' : 'download'
					});
					var $aimg = $(rendered);
					var $img = $aimg.find("img");
					$img.show().lazyload({
						threshold: 600,
						effect   : "fadeIn"
					});
					$aimg.on("click", setImage);
					$aimg.find(".saveme").click(function (e) {
						if (self.is_local) {
							$aimg.addClass("loading");
							$.post(settings.urls.download, {
								url : $(e.currentTarget).parent()[0].href,
								name: self.currentCategoryName
							}).done(function () {
								$aimg.addClass("exists");
							}).always(function () {
								$aimg.removeClass("loading");
							});
						} else {
							var link = document.createElement('a');
							link.href = $(e.currentTarget).parent()[0].href;
							//link.download = "cool";
							document.body.appendChild(link);
							link.click();
							//document.body.removeChild(link);
							//self.downloadClick = true;
							//$aimg.click();
						}
						return false;
					});

					$aimg.find(".removeme").click(function (e) {
						if (self.is_local) {
							$aimg.addClass("loading");
							$.post(settings.urls.remove, {
								url : $(e.currentTarget).parent()[0].href,
								name: self.currentCategoryName
							}).done(function () {
								$aimg.removeClass("exists");
							}).always(function () {
								$aimg.removeClass("loading");
							});
						}
						return false;
					});

					$images.append($aimg);
				});
				if (ondone) {
					ondone(response);
				}
				$(window).trigger('scroll');
				$("#load-progress").hide();
			});
		}


		function onScroll() {
			if ($(window).scrollTop() >= $(document).height() - $(window).height() - 600) {
				if (lastPage != currentPage) {

					var next_page = "";
					if (pages.length > 1) {
						next_page = pages[currentPage+1]
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
					//return {
					//	results: data.items.map(function (item) {
					//		self.currentSourceName = item.source_name;
					//		return {
					//			'id'  : item.local_url,
					//			'text': item.name
					//		}
					//	})
					//};
				},
				cache         : true
			}
		}).on('change', function (e) {
			fetchInit(e.currentTarget.value);
		});

		if ($.cookie("lastCategory") && $.cookie("lastCategory") != "null") {
			fetchInit($.cookie("lastCategory"));
		}

		$(window).scroll(onScroll);
	});
}