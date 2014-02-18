/*jshint
    forin:true, noarg:true, noempty:true, eqeqeq:true, bitwise:true,
    undef:true, curly:true, browser:true, indent:4, maxerr:50, strict:false
*/

/*global
    canvas, alert, console, video
*/

'use strict';

// Take a screenshot using getUserMedia API.
// From http://www.miguelmota.com/blog/screenshots-with-getusermedia-api/
// Give credit where credit is due. The code is heavily inspired by
// HTML5 Rocks' article "Capturing Audio & Video in HTML5"
// http://www.html5rocks.com/en/tutorials/getusermedia/intro/
(function ($, document, undefined) {

    // Our element ids.
    var options = {
        video: '#video',
        canvas: '#canvas',
        captureBtn: '#capture-btn',
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
        // Get the canvas context.
        ctx: canvas.getContext('2d'),
        // Get the capture button.
        captureBtn: document.querySelector(options.captureBtn),

        initialize: function () {
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
                that.saveDataUrlToImage();
            }
        },

        saveDataUrlToImage: function () {
            var that = this;
            var options = {
                // Change this to your own url.
                url: '/api/similarity'
            };

            // Only place where we need jQuery to make an ajax request
            // to our server to convert the dataURL to a PNG image,
            // and return the url of the converted image.
            $.ajax({
                url: options.url,
                type: 'POST',
                dataType: 'json',
                data: { 'data_uri': dataURL },
                complete: function (xhr, textStatus) {
                // Request complete.
                },
                // Request was successful.
                success: function (data, textStatus, xhr) {
                    console.log('data: ', data);
                    imageURL = data['image_url'];
                    that.drawTags(
                        data['faces']['width'],
                        data['faces']['height'],
                        data['faces']['tags'][0]['points']
                    );
                },
                error: function (xhr, textStatus, errorThrown) {
                    // Some error occured.
                    console.log('Error: ', errorThrown);
                }
            });
        },

        drawTags: function (widthPct, heightPect, tags) {
            console.log(tags)
            $(tags).each(function (index, item) {
                var tagSpan = $("<span/>"),
                    left = widthPct * item['x'] / 100,
                    top = heightPect * item['y'] / 100;
                tagSpan.addClass("tag-point");
                tagSpan.attr("style", "top: "+ top +"px; left: "+ left +"px;");
                $(options.canvas).append(tagSpan);
            });
        }

    };

    // Initialize our application.
    App.initialize();

    // Expose to window object for testing purposes.
    window.App = App || {};

})(jQuery, document);