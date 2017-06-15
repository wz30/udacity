import webbrowser
class Movie():
    """ this class provides a way to store movie related information"""
    #valid_ratings = ["G", "PG", "PG-13", "R"]
    #self constructor
    def __init__(self,movie_title, movie_storyline, poster_image,
               trailer_youtube):
        self.title = movie_title;
        self.storyline = movie_storyline;
        self.poster_image_url = poster_image;
        self.trailer_youtube_url =trailer_youtube;

    #function to show trailer by calling open
    def show_trailer(self):
        webbrowser.open(self.trailer_youtube_url)
