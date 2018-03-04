function getMovieByPk(pk) {

}

function getMovieByTitleDb(title) {

}

function getMovieByTitleOMDB(title) {

}

function getMovieByTitleDbToOMDB(title) {

}

function addMovieToBacklog(movie) {
    console.log("addMovieToBacklog()");
    $.ajax({
        url : '/mycouch/backlog/add/',
        type : 'POST',
        data : { title: movie.title, director: movie.director, year: movie.year, poster : movie.poster, plot: movie.plot }
    }).done(function(response) {
        console.log("done()");
        //TODO: Lägg till filmen i backloglistan utan att reloada sidan
        window.location.reload();
    })


}

//TODO: Not used right now
function saveMovieTo(moviePk, targetType, contextualObject) {
    if(targetType === 'backlog') {
        $.ajax({
        url : '/mycouch/backlog/add/',
        type : 'POST',
        data : JSON.stringify({'movie': contextualObject})
        }).done(function(response) {

        });
    } else if(targetType === 'movieNightList') {
        var movienightPk = contextualObject.movienightPk;
    }
}