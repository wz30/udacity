import media
import fresh_tomatoes
#toy story initialization
toy_story = media.Movie("Toy Story",
                        "A story of a boy and its toys taht come to life",
                        "https://upload.wikimedia.org/wikipedia/en/1/13/Toy_Story.jpg",
                        "https://www.youtube.com/watch?v=KYz2wyBy3kc")

#print(toy_story.storyline)
#avatar def
avatar = media.Movie("Avatar",
                     "A marine on an alien planet",
                     "https://upload.wikimedia.org/wikipedia/en/b/b0/Avatar-Teaser-Poster.jpg",
                     "https://www.youtube.com/watch?v=cRdxXPV9GNQ")
#print(avatar.storyline)
#avatar.show_trailer()
transformers = media.Movie("Transformers",
                     "The fifth installment of the live-action Transformers film series",
                     "https://upload.wikimedia.org/wikipedia/en/2/26/Transformers_The_Last_Knight_poster.jpg",
                     "https://www.youtube.com/watch?v=sgnO5fO46pE")

spider_man = media.Movie("Spider-man",
                     "Several months after the events of Captain America",
                     "https://upload.wikimedia.org/wikipedia/en/f/f9/Spider-Man_Homecoming_poster.jpg",
                     "https://www.youtube.com/watch?v=U0D3AOldjMU")

despicable_me = media.Movie("Despicable Me 3",
                     "It will be released in the United States theaters on June 30, 2017",
                     "https://upload.wikimedia.org/wikipedia/en/9/91/Despicable_Me_3_%282017%29_Teaser_Poster.jpg",
                     "https://www.youtube.com/watch?v=uApRZVgOvxc")

apes = media.Movie("War for the Planet of the Apes",
                     "2 years after the events of Dawn of the Planet of the Apes",
                     "https://upload.wikimedia.org/wikipedia/en/d/d7/War_for_the_Planet_of_the_Apes_poster.jpg",
                     "https://www.youtube.com/watch?v=UEP1Mk6Un98")
#create the thr list of movies
movies = [toy_story, avatar, transformers, spider_man, despicable_me, apes]

#pass the list of movie and generate the website
fresh_tomatoes.open_movies_page(movies)
