create table IF NOT EXISTS Artist(
	artist_id int, 
	artist_name varchar(255), 
	primary key(artist_id));

create table IF NOT EXISTS Song(
	song_id int, 
	artist_id int, 
	song_name varchar(255), 
	song_url varchar(255), 
	primary key(song_id), 
	foreign key(artist_id) references Artist(artist_id));

create table IF NOT EXISTS Token(
	song_id int, 
	token varchar(255), 
	frequency int, 
	primary key(song_id, token), 
	foreign key(song_id) references Song(song_id));

create table IF NOT EXISTS TFIDF(
	song_id int, 
	score int, 
	primary key(score), 
	foreign key(song_id) references Song(song_id));
