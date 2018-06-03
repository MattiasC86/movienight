$(function() {

    // Delete from backlog
    $(".delBacklogBtn").click(function() {
        var backlogToDelete =  $(this).attr('name');
        console.log('clicked to remove backlog with movie.pk ' + backlogToDelete);

        $.ajax({
            url : 'delete/',
            type : "POST",
            data : { backlogToDelete: backlogToDelete}
        }).done(function(returned_data){
            window.location.href = myPageBacklog;

        });
    });

    // Add singlechoice to backlog
    $(".addMovieBtn").click(function() {
        console.log('clicked to save backlog');
        var movie = {
            'title': $("#resultTitle").text(),
            'year': $("#resultYear").text(),
            'director': $("#resultDirector").text(),
            'poster': $("#resultPoster").attr("src"),
            'plot': $("#resultPlot").text()
        };
        addMovieToBacklog(movie);
    });
    function saveToBacklogDone(response) {
        console.log("Save done! :)");
    }
    // Add multiplechoice to backlog
    $(".addBacklogMultiChoiceBtn").click(function() {
        var title = $(this).attr('id');

        console.log('clicked to save multichoice backlog');

        $.ajax({
            url : 'addmultichoice/',
            type : "POST",
            data : { title: title }
        }).done(function(returned_data){
            window.location.href = '{% url 'mypage:backlog' %}';
        });
    });

    $("#titleinput").keyup(function(e) {
        e.preventDefault();
        if (e.keyCode === 13) {
            $("#searchMovieBtn").click();
        }
    });
    $("#searchMovieBtn").click(function() {
        $("#moviesSearchResult").hide();
        $("#loadingIcon").show();
        console.log('searchMovieBtn');
        $("#movieInfo").hide();
        var titleInput = $("#titleinput").val();
        $.ajax({
            url : '{% url "mypage:get_movie" %}',
            type : "POST",
            data : { title: titleInput }
        }).done(function(response){
            console.log(response);
            if(response.Error) {
                console.log("Movie not found");
                $("#movieSearchResult").hide();
                $("#loadingIcon").hide();
                $("#alertMovieNotFound").fadeIn(200).fadeOut(4000);
                $("#multipleResultsBtn").show();
            } else {
                $("#resultTitle").text(response.Title);
            $("#resultDirector").text(response.Director);
            $("#resultPoster").attr("src", response.Poster);
            $("#resultYear").text(response.Year);
            $("#resultPlot").text(response.Plot);
            $("#loadingIcon").hide();
            $("#movieSearchResult").show();
            $("#multipleResultsBtn").show();
            }

        });
    });

    // Show all titles
        $("#multipleResultsBtn").click(function() {
            $("#movieSearchResult").hide();
            $("#moviesSearchResult").empty();

            var title = $("#titleinput").val();
            console.log(title);
            $.ajax({
                method: "POST",
                url: "getmovies/",
                data: {'title': title}
            }).done(function(response) {
                console.log(response);

                for(var i = 0; i < response.length; i++) {
                    $("#moviesSearchResult").append(
                        '<div class="col-xs-4 col-sm-4 col-md-4 col-lg-4 mt-3">' +
                            '<h6 style="color:deepskyblue">' + response[i].Title + ' <span class="text-muted">(' + response[i].Year + ')</span></h6>' +
                            '<img class="img-fluid" src="' + response[i].Poster + '" alt="">' +
                            '<button class="btn btn-success addBacklogMultiChoiceBtn" id="' + response[i].Title + '">+ Add to backlog</button>' +
                            '</div>'
                    );
                }
                $("#moviesSearchResult").show();

            });
        });

});
