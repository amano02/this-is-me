/**
 * ギャラリーモーダル内の検索・並び替え UI（Phase 3）
 * GET /api/works/ を fetch して結果を Ajax 更新する。
 */
(function ($) {
	'use strict';

	var API_BASE = '/api/works/';
	var DEBOUNCE_MS = 350;

	function getDetailModaalOptions() {
		if (typeof window.getDetailModaalOptions === 'function') {
			return window.getDetailModaalOptions();
		}
		return {
			type: 'inline',
			overlay_opacity: 0.8,
			background: 'transparent',
			before_open: function () {
				setTimeout(function () {
					$('.modaal-wrapper').last().css('z-index', '99999');
					$('.modaal-overlay').last().css('z-index', '99998');
				}, 100);
			}
		};
	}

	function formatDate(isoDate) {
		if (!isoDate) { return ''; }
		var parts = isoDate.split('-');
		if (parts.length !== 3) { return isoDate; }
		return parseInt(parts[0], 10) + '.' + parseInt(parts[1], 10) + '.' + parseInt(parts[2], 10);
	}

	function escapeHtml(text) {
		return $('<div>').text(text || '').html();
	}

	function renderMediaItem(media) {
		var caption = media.caption ? '<span class="caption">' + escapeHtml(media.caption) + '</span>' : '';

		switch (media.media_type) {
			case 'image':
				return media.file_url
					? '<img src="' + escapeHtml(media.file_url) + '" alt="' + escapeHtml(media.caption) + '">' + caption
					: '';
			case 'video':
				return media.file_url
					? '<video controls src="' + escapeHtml(media.file_url) + '"></video>' + caption
					: '';
			case 'audio':
				return media.file_url
					? '<audio controls src="' + escapeHtml(media.file_url) + '"></audio>' + caption
					: '';
			case 'embed':
				return media.external_url
					? '<iframe src="' + escapeHtml(media.external_url) + '" allowfullscreen></iframe>' + caption
					: '';
			case 'document':
				return media.file_url
					? '<a href="' + escapeHtml(media.file_url) + '" target="_blank" rel="noopener">' +
						escapeHtml(media.caption || '資料を見る') + '</a>' + caption
					: '';
			default:
				return '';
		}
	}

	function buildDetailHtml(work) {
		var mediaHtml = '';
		if (work.media && work.media.length) {
			work.media.forEach(function (item) {
				mediaHtml += renderMediaItem(item);
			});
		} else {
			mediaHtml = '<span class="no-thumbnail">No Media</span>';
		}

		var metaParts = [];
		if (work.created_date) {
			metaParts.push('制作日：' + formatDate(work.created_date));
		}
		if (work.production_hours) {
			metaParts.push('制作時間：' + work.production_hours + '時間');
		}
		if (work.tools && work.tools.length) {
			metaParts.push('使用ツール：' + escapeHtml(work.tools.join(', ')));
		}

		var highlightsHtml = '';
		if (work.highlights_list && work.highlights_list.length) {
			highlightsHtml = '<h4>見どころ</h4><ul>';
			work.highlights_list.forEach(function (item) {
				highlightsHtml += '<li>・' + escapeHtml(item) + '</li>';
			});
			highlightsHtml += '</ul>';
		}

		var tagsHtml = '';
		if (work.tags && work.tags.length) {
			tagsHtml = '<div class="tags-list">';
			work.tags.forEach(function (tag) {
				tagsHtml += '<span>#' + escapeHtml(tag) + '</span>';
			});
			tagsHtml += '</div>';
		}

		return (
			'<div class="detail-container">' +
				'<div class="detail-media">' + mediaHtml + '</div>' +
				'<div class="detail-text">' +
					'<h3>作品名：' + escapeHtml(work.title) + '</h3>' +
					(metaParts.length ? '<p class="detail-meta">' + metaParts.join(' / ') + '</p>' : '') +
					(work.description ? '<p>' + escapeHtml(work.description).replace(/\n/g, '<br>') + '</p>' : '') +
					highlightsHtml +
					tagsHtml +
				'</div>' +
			'</div>'
		);
	}

	function ensureDetailModal(slug) {
		var $existing = $('#detail-' + slug);
		if ($existing.length) {
			return $.Deferred().resolve($existing).promise();
		}

		return $.getJSON(API_BASE + encodeURIComponent(slug) + '/')
			.then(function (work) {
				var $detail = $('<div>', {
					id: 'detail-' + slug,
					css: { display: 'none' },
					html: buildDetailHtml(work)
				});
				$('body').append($detail);
				return $detail;
			});
	}

	function openWorkDetail(slug) {
		ensureDetailModal(slug).done(function () {
			var $trigger = $('[data-detail-trigger="' + slug + '"]');
			if (!$trigger.length) {
				$trigger = $('<a>', {
					href: '#detail-' + slug,
					'data-detail-trigger': slug,
					css: { display: 'none' }
				}).appendTo('body');
				$trigger.modaal(getDetailModaalOptions());
			}
			$trigger.modaal('open');
		});
	}

	function renderWorkItem(work) {
		var thumbHtml = work.thumbnail
			? '<img src="' + escapeHtml(work.thumbnail) + '" alt="' + escapeHtml(work.title) + '">'
			: '<span class="no-thumbnail">No Image</span>';

		return (
			'<a href="#detail-' + escapeHtml(work.slug) + '" class="detail-open" data-slug="' + escapeHtml(work.slug) + '">' +
				thumbHtml +
				'<span class="caption">' + escapeHtml(work.title) + '</span>' +
			'</a>'
		);
	}

	function getPanelParams($panel) {
		return {
			q: $panel.find('.gallery-search-input').val().trim(),
			genre: $panel.find('.gallery-genre-filter').val(),
			sort: $panel.find('.gallery-sort').val(),
			page: $panel.data('page') || 1
		};
	}

	function fetchWorks($panel, page) {
		var params = getPanelParams($panel);
		params.page = page || 1;
		$panel.data('page', params.page);

		var $results = $panel.find('.gallery-results');
		var $status = $panel.find('.gallery-status');
		var $empty = $panel.find('.gallery-empty');
		var $loadMore = $panel.find('.gallery-load-more');

		$results.addClass('is-loading');
		$status.text('読み込み中...');

		return $.getJSON(API_BASE, params).done(function (data) {
			if (params.page === 1) {
				$results.empty();
			}

			if (!data.results.length && params.page === 1) {
				$empty.show();
			} else {
				$empty.hide();
				data.results.forEach(function (work) {
					$results.append(renderWorkItem(work));
				});
			}

			$status.text(data.count + '件');

			if (data.page < data.num_pages) {
				$loadMore.show().data('next-page', data.page + 1);
			} else {
				$loadMore.hide();
			}
		}).fail(function () {
			$status.text('読み込みに失敗しました');
		}).always(function () {
			$results.removeClass('is-loading');
		});
	}

	function debounce(fn, wait) {
		var timer;
		return function () {
			var context = this;
			var args = arguments;
			clearTimeout(timer);
			timer = setTimeout(function () {
				fn.apply(context, args);
			}, wait);
		};
	}

	function initGalleryPanel($panel) {
		var debouncedSearch = debounce(function () {
			$panel.data('page', 1);
			fetchWorks($panel, 1);
		}, DEBOUNCE_MS);

		$panel.on('input', '.gallery-search-input', debouncedSearch);
		$panel.on('change', '.gallery-genre-filter, .gallery-sort', function () {
			$panel.data('page', 1);
			fetchWorks($panel, 1);
		});
		$panel.on('click', '.gallery-load-more', function () {
			var nextPage = $(this).data('next-page');
			fetchWorks($panel, nextPage);
		});
	}

	$(function () {
		$('.gallery-panel').each(function () {
			initGalleryPanel($(this));
		});

		$(document).on('click', '.gallery-results .detail-open', function (event) {
			event.preventDefault();
			openWorkDetail($(this).data('slug'));
		});
	});
})(jQuery);
