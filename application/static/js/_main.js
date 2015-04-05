/**
 * Created by m on 26.03.15.
 */

function PhotosModel(settings) {
	var self = this;
	var pages = [];

	self.currentCategoryName = '';
	self.currentSourceName = '';
	self.currentNextPage = '';
	self.currentMaxPage = '';
	self.is_local = false;
	self.downloadClick = false;
	self.currentAlbumId = -1;

	var pageInfo = $("#page-info");

	$(document).on("mouseup", function () {
		pageInfo.fadeOut("fast");
	});

	self.pager = $("#pager").slider({
		orientation: "vertical",
		stop       : function (e, ui) {
			var page = (pages.length - ui.value);
			var section = $(".section" + page);
			if (section.size()) {
				$('html, body').animate({
					scrollTop: section.offset().top - 60
				}, 200);
			} else {
				if (pages.length > 0) {
					// if section hasn't loaded the download it
					fetchMore(pages[page-1], null, function (response) {
						currentPage = page;
						console.log($(".section"));
						var section = $(".section" + page);
						$('html, body').animate({
							scrollTop: section.offset().top - 60
						}, 200);
					});
				}
			}
		},
		start      : function () {
			pageInfo.fadeIn("fast");
		},
		slide      : function (e, ui) {
			var page = (pages().length - ui.value);
			var handle = $("#pager .ui-slider-handle");
			pageInfo.offset({
				top : handle.offset().top,
				left: 30
			});
			pageInfo.text(page);
		}

	});

	(function () {
		var lastPosX = -1;
		var entered = false;
		$(".right-column").click(function () {
			$(".right-column").toggleClass("hovered");
		});
	})();

	var currentPage = 1;
	var lastPage = currentPage;

	var templateImageItem = $("#template-image-item").html();
	var templateSectionItem = $("#template-section-item").html();
	Mustache.parse(templateImageItem);
	Mustache.parse(templateSectionItem);

	function setImage(event) {
		if (self.downloadClick) {
			self.downloadClick = false;
		} else {
			var image = document.getElementById("image-preview");
			image.src = "";
			$(image).parent().addClass("loading");
			$.get(settings.urls.image_url, {
				'url': event.currentTarget.href
			}).done(function (real_src) {
				image.src = real_src;
				$(image).one("load", function () {
					$(image).parent().removeClass("loading");
				}).each(function () {
					if (this.complete) $(this).load();
				});
			});

			return false;
		}
	}

	function fetchInit(url) {
		currentPage = 0;
		lastPage = currentPage - 1;
		pages.length = 0;
		self.currentMaxPage = -1;
		if ($('#theplace_search_query').select2('val')) {
			$.cookie("lastCategory", $('#theplace_search_query').select2('val'), {expires: 7, path: '/'});
		}
		fetchMore(url, function (response) {
			$("#images").empty();
			self.currentAlbumId = response.data.id;
			self.currentCategoryName = response.name;

			self.pager.slider("option", "max", pages.length - 1);

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
		});
	}


	function fetchMore(url, ondone, onend) {
		if (!url)
			return;
		$("#load-progress").show();
		$.get(settings.urls.images, {
			id         : self.currentAlbumId,
			source_name: self.currentSourceName,
			url        : url
		}).done(function (response) {
			self.pager.slider("option", "value", pages.length - currentPage - 2);

			self.is_local = response.is_local;
			self.currentNextPage = response.data.next_page;
			self.currentSourceName = response.source;
			self.currentMaxPage = self.currentNextPage;

			var page = currentPage + 1;

			if (pages.length == 0) {
				pages = response.data.pages;
				page -= 1;
			}
			var $images = $(Mustache.render(templateSectionItem, {
				page       : page + 1,
				pages_count: pages.length
			}));

			if (ondone) {
				ondone(response);
			}

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
							url   : $(e.currentTarget).parent()[0].href,
							name  : self.currentCategoryName,
							source: self.currentSourceName,
						}).done(function () {
							$aimg.addClass("exists");
						}).always(function () {
							$aimg.removeClass("loading");
						});
					//} else {
					//	var link = document.createElement('a');
					//	link.href = $(e.currentTarget).parent()[0].href;
						document.body.appendChild(link);
						link.click();
					}
					return false;
				});

				$aimg.find(".removeme").click(function (e) {
					if (self.is_local) {
						$aimg.addClass("loading");
						$.post(settings.urls.remove, {
							url   : $(e.currentTarget).parent()[0].href,
							name  : self.currentCategoryName,
							source: self.currentSourceName,
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

			if (onend) {
				onend(response);
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



	if ($.cookie("lastCategory") && $.cookie("lastCategory") != "null") {
		fetchInit($.cookie("lastCategory"));
	}

	$(window).scroll(onScroll);
}