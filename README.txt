
INFORMATION FOR SKINNERS
------------------------



CONTENTS:
0.   Running the addon 
I.   Infolabels available in script-globalsearch-main.xml
II.  Infolabels available in script-globalsearch-infodialog.xml
III. Control id's used in script-globalsearch-main.xml
IV.  Control id's used in script-globalsearch-infodialog.xml
V.   Available window properties



0. Running the addon
--------------------
The addon can be run in two ways:
- the user executes the addon
- the addon is executed by another addon/skin: RunScript(script.globalsearch,searchstring=foo)

You can specify which categories should be searched (this overrides the user preferences set in the addon settings):
RunScript(script.globalsearch,movies=true)
RunScript(script.globalsearch,tvshows=true&amp;musicvideos=true&amp;songs=true)

available options: epg, movies, tvshows, episodes, musicvideos, artists, albums, songs, actors, directors



I. Infolabels available in script-globalsearch-main.xml
-------------------------------------------------------
EPG:
ListItem.Label
ListItem.Icon
ListItem.Property(Genre)
ListItem.Property(Plot)
ListItem.Property(Duration)
ListItem.Property(Starttime)
ListItem.Property(Endtime)
ListItem.Property(ChannelName)
ListItem.Property(DBID)


MOVIES (and movies by actor/director):
ListItem.Label
ListItem.Icon
ListItem.Art()
ListItem.OriginalTitle
ListItem.Genre
ListItem.Plot
ListItem.Plotoutline
ListItem.Duration
ListItem.Studio
ListItem.Tagline
ListItem.Year
ListItem.Trailer
ListItem.Playcount
ListItem.Rating
ListItem.UserRating
ListItem.Mpaa
ListItem.Director
ListItem.Writer
ListItem.VideoResolution
ListItem.VideoCodec
ListItem.VideoAspect
ListItem.AudioCodec
ListItem.AudioChannels
ListItem.Path
ListItem.DBID


TV SHOWS:
ListItem.Label
ListItem.Icon
ListItem.Art()
ListItem.Episode
ListItem.Mpaa
ListItem.Year
ListItem.Genre
ListItem.Plot
ListItem.Premiered
ListItem.Studio
ListItem.Rating
ListItem.UserRating
ListItem.Playcount
ListItem.Path
ListItem.DBID


SEASONS:
ListItem.Label
ListItem.Icon
ListItem.Art()
ListItem.Episode
ListItem.TvShowTitle
ListItem.Playcount
ListItem.UserRating
ListItem.Path
ListItem.DBID


EPISODES:
ListItem.Label
ListItem.Icon
ListItem.Art()
ListItem.Episode
ListItem.Plot
ListItem.Rating
ListItem.UserRating
ListItem.Director
ListItem.Season
ListItem.Duration
ListItem.TvShowTitle
ListItem.Premiered
ListItem.Playcount
ListItem.VideoResolution
ListItem.VideoCodec
ListItem.VideoAspect
ListItem.AudioCodec
ListItem.AudioChannels
ListItem.Path
ListItem.DBID


MUSIC VIDEOS:
ListItem.Label
ListItem.Icon
ListItem.Art()
ListItem.Album
ListItem.Artist
ListItem.Director
ListItem.Genre
ListItem.Plot
ListItem.Rating
ListItem.UserRating
ListItem.Duration
ListItem.Studio
ListItem.Year
ListItem.Playcount
ListItem.VideoResolution
ListItem.VideoCodec
ListItem.VideoAspect
ListItem.AudioCodec
ListItem.AudioChannels
ListItem.Path
ListItem.DBID


ARTISTS:
ListItem.Label
ListItem.Icon
ListItem.Art()
ListItem.Path
ListItem.DBID
ListItem.Property(Artist_Born)
ListItem.Property(Artist_Died)
ListItem.Property(Artist_Formed)
ListItem.Property(Artist_Disbanded)
ListItem.Property(Artist_YearsActive)
ListItem.Property(Artist_Mood)
ListItem.Property(Artist_Style)
ListItem.Property(Artist_Genre)
ListItem.Property(Artist_Description)


ALBUMS:
ListItem.Label
ListItem.Icon
ListItem.Art()
ListItem.Artist
ListItem.Genre
ListItem.UserRating
ListItem.Year
ListItem.Path
ListItem.DBID
ListItem.Property(Album_Label)
ListItem.Property(Album_Description)
ListItem.Property(Album_Theme)
ListItem.Property(Album_Style)
ListItem.Property(Album_Rating)
ListItem.Property(Album_Type)
ListItem.Property(Album_Mood)


SONGS:
ListItem.Label
ListItem.Icon
ListItem.Art()
ListItem.Artist
ListItem.Album
ListItem.Genre
ListItem.Comment
ListItem.Track
ListItem.Rating
ListItem.UserRating
ListItem.Playcount
ListItem.Duration
ListItem.Year
ListItem.Path
ListItem.DBID



II. Infolabels available in script-globalsearch-infodialog.xml
--------------------------------------------------------------
You can use the same labels as above, only add a 'Container(100).' prefix to them.
for example:
Container(100).ListItem.Label
Container(100).ListItem.Property(Plot)



III. Control id's used in script-globalsearch-main.xml
------------------------------------------------------
100 - Main group id. All code should be included in this group. The script will set this id to hidden when playing a trailer.
101 - Content group id. All code, except the background images, can be included in this group. The script will set this id to hidden when an info dialog is visible.

110 - Label containing the number of found movies
111 - Container for found movies
119 - The script will set this id to visible when movies are found

120 - Label containing the number of found tv shows
121 - Container for found tv shows 
129 - The script will set this id to visible when tv shows are found

130 - Label containing the number of found seasons
131 - Container for found seasons  
139 - The script will set this id to visible when seasons are found

140 - Label containing the number of found episodes
141 - Container for found episodes 
149 - The script will set this id to visible when episodes are found

150 - label containing the number of found music videos
151 - Container for found music videos 
159 - The script will set this id to visible when music videos are found

160 - Label containing the number of found artists
161 - Container for found artists 
169 - The script will set this id to visible when artists are found

170 - Label containing the number of found albums
171 - Container for found albums 
179 - The script will set this id to visible when albums are found

180 - Label containing the number of found songs
181 - Container for found songs 
189 - The script will set this id to visible when songs are found

190 - Label containing the number of found programmes
191 - Container for found programmes 
199 - The script will set this id to visible when programmes are found

200 - Label containing the number of found movies containing the actor
201 - Container for found movies containing the actor
209 - The script will set this id to visible when movies containing the actor are found

210 - Label containing the number of found movies containing the director
211 - Container for found movies containing the director
219 - The script will set this id to visible when movies containing the director are found

990 - 'Searching...' label, visible when the script is searching
991 - Search category label, visible when the script is searching
998 - 'New search' button, visible when the script finished searching
999 - 'No results found' label, visible when no results are found



IV. Control id's used in script-globalsearch-infodialog.xml
-----------------------------------------------------------
100 - Hidden list containing the selected ListItem.


As always, do not change or remove any of the id's mentioned above!
If you want to get rid of some of them, just position them outside of the screen.

Any id not mentioned above, but used in the default xml files, can safely be changed or removed.



VI.  Available window properties
--------------------------------
Window.Property(GlobalSearch.SearchString) - the string the user is searching for

