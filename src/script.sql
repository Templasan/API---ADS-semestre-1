CREATE DATABASE IF NOT EXISTS scrumteach;
USE scrumteach;

CREATE TABLE IF NOT EXISTS accounts (
	idAc int(11) NOT NULL AUTO_INCREMENT,
  	nome varchar(50) NOT NULL,
  	password varchar(255) NOT NULL,
  	regfun int(20) NOT NULL,
    PRIMARY KEY (idAc)
);

create table cmtDB (
id int auto_increment,
idAc int NOT NULL,
conteudo varchar(255) not null,
now_date varchar(20),
PRIMARY KEY (id),
FOREIGN KEY (idAc) REFERENCES accounts(idAc)
);

create table scoreAv (
id int auto_increment,
idAc int NOT NULL,
scorePorcento varchar(5) not null,
now_date varchar(20),
PRIMARY KEY (id),
FOREIGN KEY (idAc) REFERENCES accounts(idAc)
);