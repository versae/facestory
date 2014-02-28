/*jshint
    forin:true, noarg:true, noempty:true, eqeqeq:true, bitwise:true,
    undef:true, curly:true, browser:true, indent:4, maxerr:50, strict:true
*/

/*global
    canvas, alert, console, video, jQuery
*/

'use strict';

// Take a screenshot using getUserMedia API.
// From http://www.miguelmota.com/blog/screenshots-with-getusermedia-api/
// Give credit where credit is due. The code is heavily inspired by
// HTML5 Rocks' article 'Capturing Audio & Video in HTML5'
// http://www.html5rocks.com/en/tutorials/getusermedia/intro/
(function ($, document, undefined) {

    // Our element ids.
    var options = {
        video: '#video',
        canvas: '#canvas',
        canvasContainer: '#canvas-container',
        captureBtn: '#capture-btn',
        tryagainBtn: '#tryagain-btn',
        message: '#message',
        progressBar: '#progress-bar',
        photo: '#photo',
        results: '#results'
    };
    // This will hold the video stream.
    var localMediaStream = null;
    // This will hold the screenshot base 64 data url.
    var dataURL = null;
    // This will hold the converted PNG url.
    var imageURL = null;
    // Our object that will hold all of the functions.
    var App = {
        // Get the video element.
        video: document.querySelector(options.video),
        // Get the canvas element.
        canvas: document.querySelector(options.canvas),
        canvasContainer: document.querySelector(options.canvasContainer),
        // Get the canvas context.
        ctx: canvas.getContext('2d'),
        // Get the capture button.
        photo: document.querySelector(options.photo),
        captureBtn: document.querySelector(options.captureBtn),
        tryagainBtn: document.querySelector(options.tryagainBtn),
        message: document.querySelector(options.message),
        progressBar: document.querySelector(options.progressBar),
        results: document.querySelector(options.results),
        colors: [
            "#e4d00a",
            "#FF7400", "#BF7130", "#A64B00", "#FF9640", "#FFB273",
            "#CD0074", "#992667", "#85004B", "#E6399B", "#E667AF",
            "#00CC00", "#269926", "#008500", "#39E639", "#67E667"
        ],

        initialize: function () {
            var that = this;
            if (this.photo.value === "") {
                this.loadUserMedia();
            } else {
                this.loadPhoto(this.photo.value);
            }

            this.tryagainBtn.onclick = function () {
                that.tryagain();
            }
        },

        loadUserMedia: function () {
            var that = this;
            // Check if navigator object contains getUserMedia object.
            navigator.getUserMedia = (
                navigator.getUserMedia || navigator.webkitGetUserMedia ||
                navigator.mozGetUserMedia || navigator.msGetUserMedia
            );
            // Check if window contains URL object.
            window.URL = window.URL || window.webkitURL;

            // Check for getUserMedia support.
            if (navigator.getUserMedia) {
                // Get video stream.
                navigator.getUserMedia({
                    video: true
                }, this.gotStream, this.noStream);

                // Bind capture button to capture method.
                this.captureBtn.onclick = function () {
                    that.capture();
                };
            } else {
                // No getUserMedia support.
                alert('Your browser does not support getUserMedia API.');
            }
        },

        // Stream error.
        noStream: function (err) {
            alert('Could not get camera stream.');
            console.log('Error: ', err);
        },

        // Stream success.
        gotStream: function (stream) {
            // Feed webcam stream to video element.
            // IMPORTANT: video element needs autoplay attribute or it will be
            // frozen at first frame.
            if (window.URL) {
                video.src = window.URL.createObjectURL(stream);
            } else {
                video.src = stream; // Opera support.
            }

            // Store the stream.
            localMediaStream = stream;
        },

        // Capture frame from live video stream.
        capture: function () {
            var that = this;
            // Check if has stream.
            if (localMediaStream) {
                // Draw whatever is in the video element on to the canvas.
                that.ctx.drawImage(video, 0, 0);
                // Create a data url from the canvas image.
                dataURL = canvas.toDataURL('image/png');
                // Call our method to save the data url to an image.
                $(options.canvas).toggle();
                $(options.video).toggle();
                $(options.captureBtn).toggle();
                $(options.progressBar).toggle();
                that.calculateSimilarities();
            }
        },

        loadPhoto: function (photoId) {
            $(options.canvas).toggle();
            $(options.video).toggle();
            $(options.captureBtn).toggle();
            $(options.progressBar).toggle();
            this.calculateSimilarities(photoId);

        },

        tryagain: function () {
            $(options.canvas).hide();
            $(options.video).show();
            $(options.captureBtn).show();
            $(options.tryagainBtn).hide();
            $(options.message).hide();
            $('.tag-point').remove();
            $('.similar-face').remove();
        },

        calculateSimilarities: function (photoId) {
            var payload, type, that = this;
            // Only place where we need jQuery to make an ajax request
            // to our server to convert the dataURL to a PNG image,
            // and return the url of the converted image.
            if (photoId != null && !photoId.isEmpty()) {
                type = "GET";
                payload = { 'photo_id': photoId };
            } else {
                type = "POST";
                payload = { 'data_uri': dataURL };
            }
            $.ajax({
                url: '/api/similarity',
                type: type,
                dataType: 'json',
                data: payload,
                // Request was successful.
                success: function (data, textStatus, xhr) {
                    console.log('data: ', data);
                    var image;
                    if (data.message === 'OK') {
                        if (type === "GET" && data.image_url !== '') {
                            image = new Image();
                            image.src = data.image_url;
                            image.onload = function(){
                                that.ctx.drawImage(image, 0, 0);
                            }
                        }
                        //imageURL = data.image_url;
                        $(data.faces).each(function (index, item) {
                            that.iterateFaces(index, item);
                        });
                        $(options.tryagainBtn).show();
                        $(options.progressBar).hide();
                    } else {
                        that.showMessage('Ups, something went wrong. Try again!');
                    }
                },
                error: function (xhr, textStatus, errorThrown) {
                    // Some error occured.
                    console.log('Error: ', errorThrown);
                    that.showMessage('Ups, something went wrong. Try again!');
                }
            });
        },

        iterateFaces: function (index, item) {
            var faceTag, faceSpan, faceDiv, symmetryInfo, container = $(options.results);
            symmetryInfo = "<br> " +
                "<em>Your symmetry index is <strong>~" +
                parseInt(100 * (1 - item.face_symmetry)) + "%</strong></em>";
            faceDiv = $("<div/>");
            faceDiv.addClass("similar-face");
            faceDiv.css({
                'background-color': this.hexToRgb(this.colors[index], 0.25),
            });
            faceTag = $("<img/>");
            faceTag.addClass("similar-face");
            faceTag.attr("src", item.face_url);
            faceTag.css({
                'border-color': this.colors[index]
            });
            faceDiv.append(faceTag);
            faceSpan = $("<span/>");
            faceSpan.addClass("similar-face");
            // Don't show the symmetry index information
            symmetryInfo = "";
            faceSpan.html("That's a perfect face for the <strong> Century " +
                          this.getCentury(item.painting_age) +
                          "</strong><br>More exactly one from the <strong>" +
                          item.painting_style + "</strong> style" + symmetryInfo);
            faceDiv.append(faceSpan);
            this.drawTags(
                item.image_width,
                item.image_height,
                item.points,
                index
            );
            container.append(faceDiv);
        },

        drawTags: function (widthPct, heightPect, tags, face_index) {
            var that = this;
            $(tags).each(function (index, item) {
                var tagSpan = $('<span/>'),
                    offset = $(options.canvas).offset(),
                    left = parseInt(widthPct * item.x / 100, 10) + offset.left,
                    top = parseInt(heightPect * item.y / 100, 10) + offset.top;
                tagSpan.addClass('tag-point');
                // tagSpan.hide();
                tagSpan.attr('style', 'top: ' + top + 'px; ' +
                                      'left: ' + left + 'px;');
                tagSpan.attr('id', item.id);
                $(options.canvasContainer).append(tagSpan);
                tagSpan.css({
                    'border-color': that.colors[face_index],
                    'background-color': that.colors[face_index],
                });
            });
        },

        getCentury: function(century) {
            return century + "<sup>th</sup>";
        },

        hexToRgb: function(hex, alpha) {
            var r, g, b, result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
            if (result) {
                r = parseInt(result[1], 16);
                g = parseInt(result[2], 16);
                b = parseInt(result[3], 16);
                return "rgba(" + r + ", " + g + ", " + b + ", " + alpha + ")"
            }
            return hex;
        },

        showMessage: function (message) {
            $(options.canvas).show();
            $(options.video).hide();
            $(options.tryagainBtn).show();
            $(options.captureBtn).hide();
            $(options.progressBar).hide();
            $(options.message).show();
            $(options.message).html(message);
        }

    };

    // Initialize our application.
    App.initialize();

    // Expose to window object for testing purposes.
    window.App = App || {};

})(jQuery, document);
