CREATE DATABASE IF NOT EXISTS scrumteach;
USE scrumteach;

CREATE TABLE IF NOT EXISTS accounts (
	id int(11) NOT NULL AUTO_INCREMENT,
  	nome varchar(50) NOT NULL,
  	password varchar(255) NOT NULL,
  	regfun int(20) NOT NULL,
    PRIMARY KEY (id)
);

create table cmtDB (
id int auto_increment primary key,
nome varchar(50) NOT NULL,
conteudo varchar(255) not null,
now_date varchar(20)
);