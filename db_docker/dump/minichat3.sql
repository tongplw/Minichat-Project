CREATE DATABASE IF NOT EXISTS minichat;
USE minichat;

DROP TABLE IF EXISTS `messages`;

CREATE TABLE `messages` (
  `id` int(11) unsigned PRIMARY KEY AUTO_INCREMENT,
  `message` varchar(255) null,
  `user_id` varchar(255),
  `group_id` varchar(255),
  `sent_on` timestamp default current_timestamp,
  foreign key(`user_id`) references `users`(`username`),
  foreign key(`group_id`) references `groups`(`name`)
);	