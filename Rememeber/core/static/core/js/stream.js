/**
 * Created by Jiati Le on 10/25/16.
 * All external recourse I referred will listed here:
 * http://stackoverflow.com/questions/4459379/preview-an-image-before-it-is-uploaded
 */
$(document).ready(function () {  // Runs when the document is ready

    // using jQuery
    // https://docs.djangoproject.com/en/1.10/ref/csrf/
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $('.modal').modal({
        dismissible: true, // Modal can be dismissed by clicking outside of the modal
        opacity: .5, // Opacity of modal background
        in_duration: 300, // Transition in duration
        out_duration: 200, // Transition out duration
        starting_top: '4%', // Starting top style attribute
        ending_top: '10%', // Ending top style attribute
        ready: function (modal, trigger) { // Callback for Modal open. Modal and trigger parameters available.
            $('.grid').masonry({
                itemSelector: '.grid-item',
            });
        },
        complete: function () {
        } // Callback for Modal close
    });


    $('ul.tabs').tabs({
        onShow: function (tabs, trigger) {
            $('.grid').masonry({
                itemSelector: '.grid-item',
            });
        }
    });
});

$(".button-collapse").sideNav();
$(".dropdown-button1").dropdown({
        inDuration: 300,
        outDuration: 225,
        constrain_width: false, // Does not change width of dropdown to that of the activator
        hover: true, // Activate on hover
        gutter: 0, // Spacing from edge
        belowOrigin: true, // Displays dropdown below the button
        alignment: 'right' // Displays dropdown with edge aligned to the left of button
    }
);
$(".dropdown-button2").dropdown({
        inDuration: 300,
        outDuration: 225,
        constrain_width: false, // Does not change width of dropdown to that of the activator
        hover: false, // Activate on hover
        gutter: 0, // Spacing from edge
        belowOrigin: true, // Displays dropdown below the button
        alignment: 'right' // Displays dropdown with edge aligned to the left of button
    }
);
$(document).on('click', '.like-button', function (event) {
    var meme_id = this.id;
    $.ajax({
        url: '/rememeber/favorite/' + meme_id,
        type: 'GET',
        datatype: 'json',
        success: function (data, textstatus, XHR) {
            var count = data[0]['popularity'];
            var meme_id = data[0]['meme_id'];
            var fav = $('#' + 'popularity-' + meme_id);
            fav.html(count);
        }
    })
});

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('#blah').attr('src', e.target.result);
        };

        reader.readAsDataURL(input.files[0]);
    }
}

$("#uploaded-image").change(function () {
    if (!$('#blah').length) {
        $('.image-background-div').append('<img id="blah" src="#" alt="your image"/>')
    }
    readURL(this);
    var action = $('#create_meme_form').attr('action');
    var index = action.lastIndexOf('/');
    if (action.substr(index, action.length) != '/create_meme') {
        var new_action = action.substr(0, index);
        $('#create_meme_form').attr('action', new_action);
    }
});

$('.caption-input').on('input', function (event) {
    var element_id = this.id;
    var content = this.value;
    var img = document.getElementById('blah');
    var img_width = img.clientWidth;
    var img_height = img.clientHeight;
    var index = element_id.lastIndexOf('-');
    var input_type = element_id.substr(0, index);
    var new_element_id = '.inside-' + input_type;
    var font_size = 10;
    var text_color = $('#id_text_color').val();
    $(new_element_id).html(content);
    $(new_element_id).css("color", text_color);
    $(new_element_id).css("font-family", "Times New Roman, Times, serif");
    $(new_element_id).css("font-size", font_size + "px");
    var w_of_caption = $(new_element_id).width();
    var h_of_caption = $(new_element_id).height();
    var h_frac = 0.2;
    var w_frac = 0.6;
    while (w_of_caption < w_frac * img_width && h_of_caption < h_frac * img_height) {
        font_size += 5;
        //console.log(font_size);
        $(new_element_id).css("font-size", font_size + "px");
        w_of_caption = $(new_element_id).width();
        h_of_caption = $(new_element_id).height();
    }
    //console.log($('#id_text_color').val());
});

$('#id_text_color').on('change', function () {
    var text_color = $('#id_text_color').val();
    $('span').css("color", text_color);
});

$(window).on('load', function () {
    $('.grid').masonry({
        itemSelector: '.grid-item',
    });
});


$('.template-image').on('click', function (event) {
    var src = this.src;
    if (!$('#blah').length) {
        $('.image-background-div').append('<img id="blah" src="#" alt="your image"/>')
    }
    $('#blah').attr('src', src);
    var bg_id = this.id.split('-')[0];
    var action = $('#create_meme_form').attr('action');
    var index = action.lastIndexOf('/');
    if (action.substr(index, action.length) != '/create_meme') {
        var new_action = action.substr(0, index + 1);
        $('#create_meme_form').attr('action', new_action + bg_id);
    } else {
        var new_action = action + '/' + bg_id;
        $('#create_meme_form').attr('action', new_action);
    }
});

$('.choose-user').on('click', function (event) {
    var user_id = $('.choose-user input').val();
    $('.candidate-meme').each(function (e) {
        var old_href = $(this).attr('href');
        var index = old_href.lastIndexOf('/');
        var new_href = old_href.substr(0, index + 1) + user_id;
        $(this).attr('href', new_href);
    })
});


$(document).ready(function () {
    window.setInterval(get_notified, 5000);
});

function get_notified() {
    $.ajax({
        url: '/rememeber/get-notified',
        datatype: 'json',
        type: 'GET',
        success: function (data, textstatus, XHR) {
            if (textstatus != 'success') {
                return;
            }
            if (data.length == 0) {
                return;
            }
            var datalength = parseInt($('#number').html());
            if (data.length == datalength) {
                return;
            }
            if (isNaN(datalength)) {
                $('#notification').append(
                    $('<span/>', {
                        'class': 'new badge',
                        'id': 'number'
                    }).html(data.length)
                );
            } else {
                $('#number').html(data.length);
            }
            if (isNaN(datalength)) {
                datalength = 0;
            }
            for (var j = datalength; j < data.length; j++) {
                var sender = data[j]['sender'];
                var meme_war = data[j]['meme_war'];
                var message_id = data[j]['message_id'];
                var message = $('<li/>').append(
                    $('<a/>', {
                        'href': '/rememeber/read-notification/' + message_id
                    }).html(sender + " replys to you in meme war " + meme_war)
                );
                $('#dropdown2').append(message);
            }
            // $('#notification').prepend('Notification');
        }
    })
}

$('#share_action_button').on('click', function (event) {
    var img_item = document.getElementById('this-meme-image');
    var img_url = img_item.src;
    var bttn = document.getElementById("share_action_button");
    // fb_share_button.className = "image_container post_profile_pic";
    console.log(img_url);
    bttn.href = "http://www.facebook.com/sharer.php?u=" + img_url;
    // bttn.href = "http://www.facebook.com/sharer.php?u=" + "http://assets2.ignimgs.com/2015/08/06/darth-vader-crossed-arms-1280jpg-88461e1280wjpg-67c0c2_1280w.jpg";
    bttn.target = "_blank";


});