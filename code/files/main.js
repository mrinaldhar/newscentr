document.onkeypress = function (e) {
    e = e || window.event;
    $('#user_input').focus();
    $('#user_input').click();
    // getStringFromUser();
};
	$('#user_input').click(function() {
		$('#top_bar').slideUp(400);
		$('#logo_small').show();
		$('#logo_small').animate({opacity: 1}, 500);
		$('#user_input').animate({width: "75%"}, 500, function() {
		$('#top_bar').css({"position":"fixed"});
		});
	});
	$('#user_input').keyup(function(e) {
    if (e.which == 13) {
    	getStringFromUser();
    }
});
	function search(q) {
		var result = "";
		$('#user_input').val(q);
		$(function() {
        $.getJSON('/search', {
          query: q
        }, function(data) {
        	console.log(data);
        	if (data["suggest"]!=$('#user_input').val().toLowerCase()) {
        		result += "<span class='stats'>Did you mean <i><u id='suggestion' onclick='search(\""+data["suggest"]+"\")'>"+data["suggest"]+"</u></i>?</span>";
        	}
        	result += "<span class='stats'>Generated "+data["number"]+" results in "+data["time"]+" seconds</span><br />";
        	$.each(data["data"], function(key, val) {
	        	result += "<ul class='resultbox'>";
	        	count = 0;
	        	$.each(val, function(i, j) {
	        		count += 1
	        		if (count < 20) {
		        		result += "<li>"+j+"</li>";
	        		}
	        		else {
	        			return;
	        		}
	        	});	
				switch(key) {
	        		case 'i':
	        		result += "<li class='small'>Infobox</li>";
	        		break;
	        		case 'b':
	        		result += "<li class='small'>Page text</li>";
	        		break;
	        		case 't':
	        		result += "<li class='small'>Page title</li>";
	        		break;
	        		case 'c':
	        		result += "<li class='small'>Categories</li>";
	        		break;
	        		case 'r':
	        		result += "<li class='small'>References</li>";
	        		break;
	        		case 'l':
	        		result += "<li class='small'>Links</li>";
	        		break;
	        	}
	        	result += "</ul>";
        	});
        	// result += JSON.stringify(data, null, '\t\t\t');
          $("#results").html(result);
        });
        return false;
    });
	}
	function getStringFromUser() {
		console.log("Searching...");
		search($('#user_input').val());
	}

	$(document).ready(function() {
		window.data = [];
		window.LAST_LOADED = 0;
		$.getJSON('/getList', {
			last: window.LAST_LOADED
        },
        function (data) {
        	console.log(data);
        	window.data = data;
        	var toPut = "";
        	$.each(data, function(index, val) {
        		toPut += "<li class='anim' onclick='show_article("+val["id"]+")'><span class='list_title'>"+val["title"]+"</span><span class='list_text'>"+val["text"].substring(0,150)+" ...</span>";
        		toPut += "</li>";
        	});
			$('#left_sidebar').append(toPut);	
			window.LAST_LOADED += 20;

        	jQuery(function($) {
			    $('#left_sidebar').bind('scroll', function() {
			        if($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
			            // alert('end reached');
						$.getJSON('/getList', {
							last: window.LAST_LOADED
						}, function(data) {
							console.log(data);
				        	var toPut = "";
							$.each(data, function(index, val) {
				        		toPut += "<li class='anim' onclick='show_article("+val["id"]+")'><span class='list_title'>"+val["title"]+"</span><span class='list_text'>"+val["text"].substring(0,150)+" ...</span>";
				        		toPut += "</li>";
				        	});
			        		$('#left_sidebar').append(toPut);
							window.data = window.data.concat(data);
							window.LAST_LOADED += 20;
						});
			        }
			    })
			});

        });
	});
	function show_article(id) {
		var curr_data = window.data[id];
		$('#container').text("");
		var toPut = "<span class='article_title'>"+curr_data["title"]+"</span>";
		toPut += "<span class='article_text'>"+curr_data["text"]+"</span>";
		$('#container').append(toPut);
		$.getJSON('/getVideos', {
			article_id: id
		}, function(data) {
			console.log(data);
			var video_players = "";
			$.each(data, function(index, value) {
				if (index == 0) {
					$('<iframe id="ytplayer" class="mainplayer" type="text/html" src="http://www.youtube.com/embed/'+value+'?autoplay=1" frameborder="0"/>').insertAfter('.article_title');
				}
				else {
					video_players += '<iframe id="ytplayer" type="text/html" width="40%" height="200px" src="http://www.youtube.com/embed/'+value+'?autoplay=0" frameborder="0"/>';
				}
			});
			$('#container').append(video_players);
		});
	}






