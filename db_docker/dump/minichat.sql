
CREATE DATABASE IF NOT EXISTS minichat;
USE minichat;

DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `username` varchar(255) PRIMARY KEY,
  `password` varchar(255) NULL
);


CREATE TABLE `groups` (
  name varchar(255) PRIMARY KEY
);

CREATE TABLE `messages` (
  `id` int(11) unsigned PRIMARY KEY AUTO_INCREMENT,
  `message` varchar(255) null,
  `user_id` varchar(255),
  `group_id` varchar(255),
  `sent_on` timestamp default current_timestamp,
  foreign key(`user_id`) references `users`(`username`),
  foreign key(`group_id`) references `groups`(`name`)
);	

	


